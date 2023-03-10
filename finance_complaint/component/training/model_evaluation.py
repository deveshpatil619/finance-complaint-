from finance_complaint.entity.artifact_entity import ModelEvaluationArtifact, DataValidationArtifact, \
    ModelTrainerArtifact
from finance_complaint.entity.config_entity import ModelEvaluationConfig
from finance_complaint.entity.schema import FinanceDataSchema
from finance_complaint.exception import FinanceException
from finance_complaint.logger import logger
import sys
from pyspark.sql import DataFrame
from pyspark.ml.feature import StringIndexerModel
from pyspark.ml.pipeline import PipelineModel
from finance_complaint.config.spark_manager import spark_session
from finance_complaint.utils import get_score

from pyspark.sql.types import StringType, FloatType, StructType, StructField
from finance_complaint.entity.estimator import S3FinanceEstimator
from finance_complaint.data_access.model_eval_artifact import ModelEvaluationArtifactData


class ModelEvaluation:

    def __init__(self,
                 data_validation_artifact: DataValidationArtifact,
                 model_trainer_artifact: ModelTrainerArtifact,
                 model_eval_config: ModelEvaluationConfig,
                 schema=FinanceDataSchema()
                 ):
        try:
            self.model_eval_artifact_data = ModelEvaluationArtifactData()
            self.data_validation_artifact = data_validation_artifact
            self.model_eval_config = model_eval_config
            self.model_trainer_artifact = model_trainer_artifact
            self.schema = schema
            self.bucket_name = self.model_eval_config.bucket_name
            self.s3_model_dir_key = self.model_eval_config.model_dir
            self.s3_finance_estimator = S3FinanceEstimator(
                bucket_name=self.bucket_name,
                s3_key=self.s3_model_dir_key
            )
            self.metric_report_schema = StructType([StructField("model_accepted", StringType()),
                                                    StructField("changed_accuracy", FloatType()),
                                                    StructField("trained_model_path", StringType()),
                                                    StructField("best_model_path", StringType()),
                                                    StructField("active", StringType())]
                                                   )

        except Exception as e:
            raise FinanceException(e, sys)


    def read_data(self) -> DataFrame:
        try:
            file_path = self.data_validation_artifact.accepted_file_path  ## accepted_file_path location 
            dataframe: DataFrame = spark_session.read.parquet(file_path) ## storing it in dataframe format
            return dataframe
        except Exception as e:
            # Raising an exception.
            raise FinanceException(e, sys)

    def evaluate_trained_model(self) -> ModelEvaluationArtifact: ## if we already have a model then evaluate_trained_model will run
        is_model_accepted, is_active = False, False ## by default the status we are keeping it to false
        trained_model_file_path = self.model_trainer_artifact.model_trainer_ref_artifact.trained_model_file_path ## trained_model_file_path location
        label_indexer_model_path = self.model_trainer_artifact.model_trainer_ref_artifact.label_indexer_model_file_path ## label_indexer_model_path location

        ## The taget column categorical we need to convert to indexes
        label_indexer_model = StringIndexerModel.load(label_indexer_model_path)  ## loading the label_indexer_model_path in StringIndexerModel
        trained_model = PipelineModel.load(trained_model_file_path) ## loading the trained model

        dataframe: DataFrame = self.read_data() ## reading the accepted data
        dataframe = label_indexer_model.transform(dataframe)   

        best_model_path = self.s3_finance_estimator.get_latest_model_path() ## loading the best model from the s3 bucket

        ## All the stages in the trained_model artifact will run when we do the prediction of the model
        trained_model_dataframe = trained_model.transform(dataframe) ## here we will get the prediction on training dataset
        best_model_dataframe = self.s3_finance_estimator.transform(dataframe) 

        trained_model_f1_score = get_score(dataframe=trained_model_dataframe, metric_name="f1",
                                           label_col=self.schema.target_indexed_label,
                                           prediction_col=self.schema.prediction_column_name)
        best_model_f1_score = get_score(dataframe=best_model_dataframe, metric_name="f1",
                                        label_col=self.schema.target_indexed_label,
                                        prediction_col=self.schema.prediction_column_name)

        logger.info(f"Trained_model_f1_score: {trained_model_f1_score}, Best model f1 score: {best_model_f1_score}")
        changed_accuracy = trained_model_f1_score - best_model_f1_score ## calculating the change in accuracy in our trained model vs the best model in bucket

        if changed_accuracy >= self.model_eval_config.threshold:  ## comparing the changed accuracy with our threshold 
            is_model_accepted, is_active = True, True  ## changing the status of the model and accepting it if the changed_accuracy is greater then the threshold

        model_evaluation_artifact = ModelEvaluationArtifact(model_accepted=is_model_accepted,  ## preparing the model_evaluation_artifacts
                                                            changed_accuracy=changed_accuracy,
                                                            trained_model_path=trained_model_file_path,
                                                            best_model_path=best_model_path,
                                                            active=is_active
                                                            )
        return model_evaluation_artifact

    def initiate_model_evaluation(self) -> ModelEvaluationArtifact:
        try:
            model_accepted = True
            is_active = True

            if not self.s3_finance_estimator.is_model_available(key=self.s3_finance_estimator.s3_key):  ## if the model is not available in the s3 bucket
                latest_model_path = None 
                trained_model_path = self.model_trainer_artifact.model_trainer_ref_artifact.trained_model_file_path
                ## just preparing the model_evaluation_artifact
                model_evaluation_artifact = ModelEvaluationArtifact(model_accepted=model_accepted,
                                                                    changed_accuracy=0.0,
                                                                    trained_model_path=trained_model_path,
                                                                    best_model_path=latest_model_path,
                                                                    active=is_active
                                                                    )
            else:
                model_evaluation_artifact = self.evaluate_trained_model()

            logger.info(f"Model evaluation artifact: {model_evaluation_artifact}")
            ## saving the artfact in the mongodb
            self.model_eval_artifact_data.save_eval_artifact(model_eval_artifact=model_evaluation_artifact)
            return model_evaluation_artifact
        except Exception as e:
            raise FinanceException(e, sys)
