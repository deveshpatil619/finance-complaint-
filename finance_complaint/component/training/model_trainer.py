import os

from finance_complaint.entity.schema import FinanceDataSchema
import sys
from pyspark.ml.feature import StringIndexer, StringIndexerModel
from pyspark.ml.pipeline import Pipeline, PipelineModel
from typing import List
from finance_complaint.config.spark_manager import spark_session
from finance_complaint.exception import FinanceException
from finance_complaint.logger import logger
from finance_complaint.entity.artifact_entity import DataTransformationArtifact, \
    PartialModelTrainerMetricArtifact, PartialModelTrainerRefArtifact, ModelTrainerArtifact
from finance_complaint.entity.config_entity import ModelTrainerConfig
from pyspark.sql import DataFrame
from pyspark.ml.feature import IndexToString
from pyspark.ml.classification import RandomForestClassifier
from finance_complaint.utils import get_score


class ModelTrainer:

    def __init__(self,
                 data_transformation_artifact: DataTransformationArtifact,  ## taking the input as DataTransformationArtifact and ModelTrainerConfig
                 model_trainer_config: ModelTrainerConfig,
                 schema=FinanceDataSchema()    ## also taking the schema as input
                 ):
        self.data_transformation_artifact = data_transformation_artifact
        self.model_trainer_config = model_trainer_config
        self.schema = schema

    def get_scores(self, dataframe: DataFrame, metric_names: List[str]) -> List[tuple]:
        """This will give us all the scores"""
        try:
            if metric_names is None:
                metric_names = self.model_trainer_config.metric_list

            scores: List[tuple] = []
            for metric_name in metric_names:
                score = get_score(metric_name=metric_name,
                                  # A keyword argument.
                                  dataframe=dataframe,
                                  label_col=self.schema.target_indexed_label,
                                  prediction_col=self.schema.prediction_column_name, )
                scores.append((metric_name, score))
            return scores
        except Exception as e:
            raise FinanceException(e, sys)

    def get_train_test_dataframe(self) -> List[DataFrame]:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path
            train_dataframe: DataFrame = spark_session.read.parquet(train_file_path)
            test_dataframe: DataFrame = spark_session.read.parquet(test_file_path)
            print(f"Train row: {train_dataframe.count()} Test row: {test_dataframe.count()}")
            dataframes: List[DataFrame] = [train_dataframe, test_dataframe]
            return dataframes
        except Exception as e:
            raise FinanceException(e, sys)

    def get_model(self, label_indexer_model: StringIndexerModel) -> Pipeline:
        try:
            stages = []
            logger.info("Creating Random Forest Classifier class.")

            """ This code is creating an instance of the RandomForestClassifier class from the pyspark.ml.classification module. This classifier is a machine learning algorithm that can be used for classification problems.
The RandomForestClassifier class takes several parameters, which are used to configure the classifier. The two parameters being passed in this code are:
labelCol: This parameter is used to specify the column name of the label (target variable) in the input DataFrame. In this case, the label column is specified as self.schema.target_indexed_label, where self.schema is an object that holds the schema of the DataFrame and target_indexed_label is the column name of the label.
featuresCol: This parameter is used to specify the column name of the features in the input DataFrame. In this case, the feature column is specified as self.schema.scaled_vector_input_features, where self.schema is an object that holds the schema of the DataFrame and scaled_vector_input_features is the column name of the feature.
Once the classifier is created, it can be trained on a dataset using the fit() method and used to make predictions on new data using the transform() method."""
            random_forest_clf = RandomForestClassifier(labelCol=self.schema.target_indexed_label,
                                                       featuresCol=self.schema.scaled_vector_input_features)

            logger.info("Creating Label generator")
            label_generator = IndexToString(inputCol=self.schema.prediction_column_name,  ## This will convert the output numerical value to string value
                                            outputCol=f"{self.schema.prediction_column_name}_{self.schema.target_column}",
                                            labels=label_indexer_model.labels)
            stages.append(random_forest_clf)
            stages.append(label_generator)
            pipeline = Pipeline(stages=stages)
            return pipeline
        except Exception as e:
            raise FinanceException(e, sys)

    def export_trained_model(self, model: PipelineModel) -> PartialModelTrainerRefArtifact:
        try:

            transformed_pipeline_file_path = self.data_transformation_artifact.exported_pipeline_file_path
            transformed_pipeline = PipelineModel.load(transformed_pipeline_file_path)

            updated_stages = transformed_pipeline.stages + model.stages  ## all stages in transformed_pipeline plus the Rndomforestclassifier and Indextostring
            transformed_pipeline.stages = updated_stages
            trained_model_file_path = self.model_trainer_config.trained_model_file_path
            transformed_pipeline.save(trained_model_file_path)

            logger.info("Creating trained model directory")
            trained_model_file_path = self.model_trainer_config.trained_model_file_path
            os.makedirs(os.path.dirname(trained_model_file_path), exist_ok=True)  ## making the folder trained_model_file_path

            ref_artifact = PartialModelTrainerRefArtifact(
                trained_model_file_path=trained_model_file_path,
                label_indexer_model_file_path=self.model_trainer_config.label_indexer_model_dir)

            logger.info(f"Model trainer reference artifact: {ref_artifact}")
            return ref_artifact

        except Exception as e:
            raise FinanceException(e, sys)

    def initiate_model_training(self) -> ModelTrainerArtifact:

        try:
            dataframes = self.get_train_test_dataframe()  
            train_dataframe, test_dataframe = dataframes[0], dataframes[1]  ## we will need the training and testing dataframe
 
            print(f"Train row: {train_dataframe.count()} Test row: {test_dataframe.count()}")
            label_indexer = StringIndexer(inputCol=self.schema.target_column,  ## converting the categorical target colmn to numerical column
                                          outputCol=self.schema.target_indexed_label)
            label_indexer_model = label_indexer.fit(train_dataframe)

            os.makedirs(os.path.dirname(self.model_trainer_config.label_indexer_model_dir), exist_ok=True) ## creating the label_indexer_model_dir file directory inside model_trainer artifact
            label_indexer_model.save(self.model_trainer_config.label_indexer_model_dir) ## savng the label_indexer_model

            train_dataframe = label_indexer_model.transform(train_dataframe)
            test_dataframe = label_indexer_model.transform(test_dataframe)

            model = self.get_model(label_indexer_model=label_indexer_model)

            trained_model = model.fit(train_dataframe)
            train_dataframe_pred = trained_model.transform(train_dataframe)  ## prediction in pyspark
            test_dataframe_pred = trained_model.transform(test_dataframe)

            print(f"number of row in training: {train_dataframe_pred.count()}")
            ## Calculating the training scores of f1 score,weightedPrecision score,weightedRecall score etc
            scores = self.get_scores(dataframe=train_dataframe_pred,metric_names=self.model_trainer_config.metric_list)
            train_metric_artifact = PartialModelTrainerMetricArtifact(f1_score=scores[0][1],
                                                                      precision_score=scores[1][1],
                                                                      recall_score=scores[2][1])
            logger.info(f"Model trainer train metric: {train_metric_artifact}")

            print(f"number of row in training: {test_dataframe_pred.count()}")
            
            ## Calculating the testing scores of f1 score,weightedPrecision score,weightedRecall score etc
            scores = self.get_scores(dataframe=test_dataframe_pred,metric_names=self.model_trainer_config.metric_list)
            test_metric_artifact = PartialModelTrainerMetricArtifact(f1_score=scores[0][1],
                                                                     precision_score=scores[1][1],
                                                                     recall_score=scores[2][1])

            logger.info(f"Model trainer test metric: {test_metric_artifact}")
            ref_artifact = self.export_trained_model(model=trained_model)

            model_trainer_artifact = ModelTrainerArtifact(model_trainer_ref_artifact=ref_artifact,
                                                          model_trainer_train_metric_artifact=train_metric_artifact,
                                                          model_trainer_test_metric_artifact=test_metric_artifact)

            logger.info(f"Model trainer artifact: {model_trainer_artifact}")

            return model_trainer_artifact

        except Exception as e:
            raise FinanceException(e, sys)
