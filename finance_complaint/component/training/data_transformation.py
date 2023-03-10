import os

from finance_complaint.entity.schema import FinanceDataSchema
import sys
from pyspark.ml.feature import StandardScaler, VectorAssembler, OneHotEncoder, StringIndexer, Imputer
from pyspark.ml.pipeline import Pipeline

from finance_complaint.config.spark_manager import spark_session
from finance_complaint.exception import FinanceException
from finance_complaint.logger import logger
from finance_complaint.entity.artifact_entity import DataValidationArtifact, DataTransformationArtifact
from finance_complaint.entity.config_entity import DataTransformationConfig
from pyspark.sql import DataFrame
from finance_complaint.ml.feature import FrequencyImputer, DerivedFeatureGenerator
from pyspark.ml.feature import IDF, Tokenizer, HashingTF
from pyspark.sql.functions import col, rand


class DataTransformation():

    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig,
                 schema=FinanceDataSchema()
                 ):
        try:
            super().__init__()
            self.data_val_artifact = data_validation_artifact
            self.data_tf_config = data_transformation_config
            self.schema = schema
        except Exception as e:
            raise FinanceException(e, sys)

    def read_data(self) -> DataFrame:
        try:
            file_path = self.data_val_artifact.accepted_file_path
            dataframe: DataFrame = spark_session.read.parquet(file_path)
            dataframe.printSchema()
            return dataframe
        except Exception as e:
            raise FinanceException(e, sys)

    def get_data_transformation_pipeline(self, ) -> Pipeline:
        try:
            """ Here all the steps of the data-transformation stage will be defined"""

            stages = [

            ]

            # numerical column transformation

            # generating additional columns
            derived_feature = DerivedFeatureGenerator(inputCols=self.schema.derived_input_features,
                                                      outputCols=self.schema.derived_output_features)
            stages.append(derived_feature) ## appending the derived_features to the list

            # creating imputer to fill null values
            imputer = Imputer(inputCols=self.schema.numerical_columns,  ## Imputer is the Imputation estimator for completing missing values, using the mean, median or mode
                              outputCols=self.schema.im_numerical_columns)
            stages.append(imputer)  ## in im_numerical_columns there will be no null values

            ## Imputed one-hot features
            frequency_imputer = FrequencyImputer(inputCols=self.schema.one_hot_encoding_features,
                                                 outputCols=self.schema.im_one_hot_encoding_features)
            stages.append(frequency_imputer)

            for im_one_hot_feature, string_indexer_col in zip(self.schema.im_one_hot_encoding_features,
                                                              self.schema.string_indexer_one_hot_features):
                string_indexer = StringIndexer(inputCol=im_one_hot_feature, outputCol=string_indexer_col) ##StringIndexer is A label indexer that maps a string column of labels to an ML column of label indices.
                stages.append(string_indexer)

            ## Applying the one-hot-encoding teachnique
            one_hot_encoder = OneHotEncoder(inputCols=self.schema.string_indexer_one_hot_features,
                                            outputCols=self.schema.tf_one_hot_encoding_features)

            stages.append(one_hot_encoder)

            ## A tokenizer that converts the input string to lowercase and then splits it by white spaces.
            tokenizer = Tokenizer(inputCol=self.schema.tfidf_features[0], outputCol="words")  ## we get words as output
            stages.append(tokenizer) 

            ## HashingTF Maps a sequence of terms to their term frequencies using the hashing trick
            hashing_tf = HashingTF(inputCol=tokenizer.getOutputCol(), outputCol="rawFeatures", numFeatures=40)
            stages.append(hashing_tf)

            ## Compute the Inverse Document Frequency (IDF) given a collection of documents.
            idf = IDF(inputCol=hashing_tf.getOutputCol(), outputCol=self.schema.tf_tfidf_features[0])
            stages.append(idf)
            
            ## VectorAssembler is a feature transformer that merges multiple columns into a vector column.
            vector_assembler = VectorAssembler(inputCols=self.schema.input_features,  ## 
                                               outputCol=self.schema.vector_assembler_output)

            stages.append(vector_assembler)

            ## StandardScaler is that it will transform your data such that its distribution will have a mean value 0 and standard deviation of 1
            standard_scaler = StandardScaler(inputCol=self.schema.vector_assembler_output,
                                             outputCol=self.schema.scaled_vector_input_features)
            stages.append(standard_scaler)
            pipeline = Pipeline(
                stages=stages
            )
            logger.info(f"Data transformation pipeline: [{pipeline}]")
            print(pipeline.stages)
            return pipeline

        except Exception as e:
            raise FinanceException(e, sys)

    def get_balanced_shuffled_dataframe(self, dataframe: DataFrame) -> DataFrame:
        try:

            count_of_each_cat = dataframe.groupby(self.schema.target_column).count().collect()
            label = []
            n_record = []
            for info in count_of_each_cat:
                n_record.append(info['count'])
                label.append(info[self.schema.target_column])

            minority_row = min(n_record)
            n_per = [minority_row / record for record in n_record]

            selected_row = []
            for label, per in zip(label, n_per):
                print(label, per)
                temp_df, _ = dataframe.filter(col(self.schema.target_column) == label).randomSplit([per, 1 - per])
                selected_row.append(temp_df)

            selected_df: DataFrame = None
            for df in selected_row:
                df.groupby(self.schema.target_column).count().show()
                if selected_df is None:
                    selected_df = df
                else:
                    selected_df = selected_df.union(df)

            selected_df = selected_df.orderBy(rand())

            selected_df.groupby(self.schema.target_column).count().show()
            return selected_df
        except Exception as e:
            raise FinanceException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        try:
            logger.info(f">>>>>>>>>>>Started data transformation <<<<<<<<<<<<<<<")
            dataframe: DataFrame = self.read_data()  ## read data using spark
            # dataframe = self.get_balanced_shuffled_dataframe(dataframe=dataframe)
            logger.info(f"Number of row: [{dataframe.count()}] and column: [{len(dataframe.columns)}]")

            test_size = self.data_tf_config.test_size   ## getting the test-size
            logger.info(f"Splitting dataset into train and test set using ration: {1 - test_size}:{test_size}") 
            train_dataframe, test_dataframe = dataframe.randomSplit([1 - test_size, test_size]) ## splitting the train-test dataframe
            logger.info(f"Train dataset has number of row: [{train_dataframe.count()}] and"
                        f" column: [{len(train_dataframe.columns)}]") 

            logger.info(f"Test dataset has number of row: [{test_dataframe.count()}] and"
                        f" column: [{len(test_dataframe.columns)}]")   

            pipeline = self.get_data_transformation_pipeline()  ## getting the transformation_pipeline

            transformed_pipeline = pipeline.fit(train_dataframe)    ## trained the transformation pipeline

            # selecting required columns
            required_columns = [self.schema.scaled_vector_input_features, self.schema.target_column]

            ## transforming the training dataset
            transformed_trained_dataframe = transformed_pipeline.transform(train_dataframe)
            transformed_trained_dataframe = transformed_trained_dataframe.select(required_columns)

            ## transforming the test dataset
            transformed_test_dataframe = transformed_pipeline.transform(test_dataframe)
            transformed_test_dataframe = transformed_test_dataframe.select(required_columns)

            export_pipeline_file_path = self.data_tf_config.export_pipeline_dir

            # creating required directory
            os.makedirs(export_pipeline_file_path, exist_ok=True)
            os.makedirs(self.data_tf_config.transformed_test_dir, exist_ok=True)
            os.makedirs(self.data_tf_config.transformed_train_dir, exist_ok=True)
            transformed_train_data_file_path = os.path.join(self.data_tf_config.transformed_train_dir,
                                                            self.data_tf_config.file_name
                                                            )
            transformed_test_data_file_path = os.path.join(self.data_tf_config.transformed_test_dir,
                                                           self.data_tf_config.file_name
                                                           )

            logger.info(f"Saving transformation pipeline at: [{export_pipeline_file_path}]")
            transformed_pipeline.save(export_pipeline_file_path)
            logger.info(f"Saving transformed train data at: [{transformed_train_data_file_path}]")
            print(transformed_trained_dataframe.count(), len(transformed_trained_dataframe.columns))
            transformed_trained_dataframe.write.parquet(transformed_train_data_file_path)

            logger.info(f"Saving transformed test data at: [{transformed_test_data_file_path}]")
            print(transformed_test_dataframe.count(), len(transformed_trained_dataframe.columns))
            transformed_test_dataframe.write.parquet(transformed_test_data_file_path)

            data_tf_artifact = DataTransformationArtifact(   ## data_transformation_artifacts
                transformed_train_file_path=transformed_train_data_file_path,
                transformed_test_file_path=transformed_test_data_file_path,
                exported_pipeline_file_path=export_pipeline_file_path,

            )

            logger.info(f"Data transformation artifact: [{data_tf_artifact}]")
            return data_tf_artifact
        except Exception as e:
            raise FinanceException(e, sys)
