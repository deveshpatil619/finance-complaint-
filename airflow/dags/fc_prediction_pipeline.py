from asyncio import tasks
import json
from textwrap import dedent
import pendulum
import os

# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator

# [START instantiate_dag]
with DAG(
    'finance_complaint_prediction',
    default_args={'retries': 2},
    description='Machine learning Spark Project for predictions',
    schedule_interval="@weekly",
    start_date=pendulum.datetime(2023, 1, 23, tz="UTC"),
    catchup=False,  
    tags=['example'],
) as dag:
    # [END instantiate_dag]
    # [START documentation]
    dag.doc_md = __doc__
    # [END documentation]

    from finance_complaint.pipeline.training import  TrainingPipeline
    from finance_complaint.config.pipeline.training import FinanceConfig
    training_pipeline= TrainingPipeline(FinanceConfig())

    # [START extract_function]
    def data_ingestion(**kwargs):
        ti = kwargs['ti']
        # Code to load data for predictions
        data_ingestion_artifact = training_pipeline.start_data_ingestion()  
        print(data_ingestion_artifact)
        ti.xcom_push('data_ingestion_artifact', data_ingestion_artifact)

    def data_validation(**kwargs):
        ti = kwargs['ti']
        data_ingestion_artifact = ti.xcom_pull(task_ids="data_ingestion",key="data_ingestion_artifact")
        # Code to preprocess data for predictions
        data_validation_artifact = training_pipeline.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
        ti.xcom_push('data_preprocessing_artifact', data_validation_artifact)

    def model_prediction(**kwargs):
        ti = kwargs['ti']
        data_preprocessing_artifact = ti.xcom_pull(task_ids="data_preprocessing",key="data_preprocessing_artifact")
        # Code to load trained model and make predictions
        predictions = ...
        ti.xcom_push('predictions', predictions)

    def post_processing(**kwargs):
        ti = kwargs['ti']
        predictions = ti.xcom_pull(task_ids="model_prediction",key="predictions")
        # Code to post-process predictions
        post_processing_artifact = ...
        ti.xcom_push('post_processing_artifact', post_processing_artifact)

    def output_results(**kwargs):
        ti = kwargs['ti']
        post_processing_artifact = ti.xcom_pull(task_ids="post_processing",key="post_processing_artifact")
        # Code to output results to a file or database
        ...
        
    # Define the tasks
    data_ingestion_task = PythonOperator(
        task_id='data_ingestion',
        python_callable=data_ingestion,
        provide_context=True,
    )
    data_preprocessing_task = PythonOperator(
       
