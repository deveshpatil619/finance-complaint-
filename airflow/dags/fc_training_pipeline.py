from asyncio import tasks
import json
from textwrap import dedent
import pendulum
import os
# training_pipeline = TrainingPipeline(FinanceConfig())


# The DAG object; we'll need this to instantiate a DAG
from airflow import DAG
training_pipeline=None
# Operators; we need this to operate!
from airflow.operators.python import PythonOperator

# [END imporETL DAG tutorial_prediction',
    # [START default_args]
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
with DAG(
    'finance_complaint', ## name of the DAG
    default_args={'retries': 2},  ## try to re-run the pipeline two times in case of failure
    # [END default_args]
    description='Machine learning Spark Project', ## description of the DAG
    schedule_interval="@weekly",  ##The Airflow scheduler monitors all tasks and DAGs, then triggers the task instances once their dependencies are complete.
    start_date=pendulum.datetime(2023, 1, 23, tz="UTC"),  ##  DAG run will only be scheduled one interval after start_date
    catchup=False,  
    tags=['example'],  ## tags is just the additional information about the DAG
) as dag:
    # [END instantiate_dag]
    # [START documentation]
    dag.doc_md = __doc__   ## string that contains the documentation for the current module
    # [END documentation]

    # [START extract_function]


    from finance_complaint.pipeline.training import  TrainingPipeline
    from finance_complaint.config.pipeline.training import FinanceConfig
    training_pipeline= TrainingPipeline(FinanceConfig())

    def data_ingestion(**kwargs):
        from finance_complaint.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,\
        ModelTrainerArtifact,ModelEvaluationArtifact,ModelPusherArtifact,PartialModelTrainerRefArtifact,PartialModelTrainerMetricArtifact
        ti = kwargs['ti']  ## the meaning of this line is that it is extracting the value of key 'ti' from kwargs and storing it in a variable ti
        data_ingestion_artifact = training_pipeline.start_data_ingestion()   ## starting the data_ingestion which will produce the data_ingestion_artifact
        print(data_ingestion_artifact)
        ti.xcom_push('data_ingestion_artifact', data_ingestion_artifact) 
        """ This line of code is using the Task Instance (ti) object to push a value into the XCOM (Cross-communication) system of Airflow.
The ti.xcom_push() function is used to push a value into the XCOM system, and takes two arguments:
The first argument is a key, which is used to identify the value that is being pushed. In this case, the key is 'data_ingestion_artifact'.
The second argument is the value that is being pushed into the XCOM system. In this case, it is the variable "data_ingestion_artifact"
It means that it is pushing the value of variable data_ingestion_artifact into the XCOM system with key 'data_ingestion_artifact' . This value can be accessed later on by other tasks using the key.
XCOM allows tasks to exchange messages, it's like a shared memory for tasks, where you can store variable that can be accessed by other tasks."""

    def data_validation(**kwargs):
        from finance_complaint.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,\
        ModelTrainerArtifact,ModelEvaluationArtifact,ModelPusherArtifact,PartialModelTrainerRefArtifact,PartialModelTrainerMetricArtifact
        ti  = kwargs['ti']
        data_ingestion_artifact = ti.xcom_pull(task_ids="data_ingestion",key="data_ingestion_artifact")
        """This line of code is using the Task Instance (ti) object to pull a value from the XCOM (Cross-communication) system of Airflow.
The ti.xcom_pull() function is used to pull a value from the XCOM system, and takes two arguments:
The first argument is the task_ids of the task which has pushed the value you want to retrieve. In this case, it is "data_ingestion".
The second argument is the key, which is used to identify the value that is being pulled. In this case, it is 'data_ingestion_artifact'
It means that it is pulling the value of key 'data_ingestion_artifact' from the task_ids 'data_ingestion' from the XCOM system and storing it in the variable data_ingestion_artifact . This value was pushed earlier by some other task using the same key.
XCOM allows tasks to exchange messages, it's like a shared memory for tasks, where you can store variable that can be accessed by other tasks.
It is used to share variable between different tasks in an airflow pipeline."""

        data_ingestion_artifact = DataIngestionArtifact(*(data_ingestion_artifact)) ## This line creates an instance of the DataIngestionArtifact class and assigns it to the variable data_ingestion_artifact. The DataIngestionArtifact class is a custom class defined in the codebase, it could be a data model that holds some information.
        # The * operator is used to unpack the elements of an iterable, such as a list or tuple. So, when * is used before a tuple or list, it means that the elements of that tuple or list will be passed as separate arguments to the function.
        data_validation_artifact=training_pipeline.start_data_validation(data_ingestion_artifact=data_ingestion_artifact)
        ti.xcom_push('data_validation_artifact', data_validation_artifact)

    def data_transformation(**kwargs):
        from finance_complaint.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,\
        ModelTrainerArtifact,ModelEvaluationArtifact,ModelPusherArtifact,PartialModelTrainerRefArtifact,PartialModelTrainerMetricArtifact
        ti  = kwargs['ti']

        data_ingestion_artifact = ti.xcom_pull(task_ids="data_ingestion",key="data_ingestion_artifact")
        data_ingestion_artifact=DataIngestionArtifact(*(data_ingestion_artifact))

        data_validation_artifact = ti.xcom_pull(task_ids="data_validation",key="data_validation_artifact")
        data_validation_artifact=DataValidationArtifact(*(data_validation_artifact))
        data_transformation_artifact=training_pipeline.start_data_transformation(
        data_validation_artifact=data_validation_artifact
        )
        ti.xcom_push('data_transformation_artifact', data_transformation_artifact)

    def model_trainer(**kwargs):
        from finance_complaint.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,\
        ModelTrainerArtifact,ModelEvaluationArtifact,ModelPusherArtifact,PartialModelTrainerRefArtifact,PartialModelTrainerMetricArtifact
        ti  = kwargs['ti']

        data_transformation_artifact = ti.xcom_pull(task_ids="data_transformation",key="data_transformation_artifact")
        data_transformation_artifact=DataTransformationArtifact(*(data_transformation_artifact))

        model_trainer_artifact=training_pipeline.start_model_trainer(data_transformation_artifact=data_transformation_artifact)

        ti.xcom_push('model_trainer_artifact', model_trainer_artifact._asdict())

    def model_evaluation(**kwargs):
        from finance_complaint.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,\
        ModelTrainerArtifact,ModelEvaluationArtifact,ModelPusherArtifact,PartialModelTrainerRefArtifact,PartialModelTrainerMetricArtifact
        ti  = kwargs['ti']
        data_ingestion_artifact = ti.xcom_pull(task_ids="data_ingestion",key="data_ingestion_artifact")
        data_ingestion_artifact=DataIngestionArtifact(*(data_ingestion_artifact))

        data_validation_artifact = ti.xcom_pull(task_ids="data_validation",key="data_validation_artifact")
        data_validation_artifact=DataValidationArtifact(*(data_validation_artifact))

        model_trainer_artifact = ti.xcom_pull(task_ids="model_trainer",key="model_trainer_artifact")
        print(model_trainer_artifact)
        model_trainer_artifact=ModelTrainerArtifact.construct_object(**model_trainer_artifact)

        model_evaluation_artifact = training_pipeline.start_model_evaluation(data_validation_artifact=data_validation_artifact,
                                                                    model_trainer_artifact=model_trainer_artifact)

    
        ti.xcom_push('model_evaluation_artifact', model_evaluation_artifact.to_dict())

    def push_model(**kwargs):
        from finance_complaint.entity.artifact_entity import DataIngestionArtifact,DataValidationArtifact,DataTransformationArtifact,\
        ModelTrainerArtifact,ModelEvaluationArtifact,ModelPusherArtifact,PartialModelTrainerRefArtifact,PartialModelTrainerMetricArtifact
        ti  = kwargs['ti']
        model_evaluation_artifact = ti.xcom_pull(task_ids="model_evaluation",key="model_evaluation_artifact")
        model_evaluation_artifact=ModelEvaluationArtifact(*(model_evaluation_artifact))
        model_trainer_artifact = ti.xcom_pull(task_ids="model_trainer",key="model_trainer_artifact")
        model_trainer_artifact=ModelTrainerArtifact.construct_object(**model_trainer_artifact)

        if model_evaluation_artifact.model_accepted:
            model_pusher_artifact = training_pipeline.start_model_pusher(model_trainer_artifact=model_trainer_artifact)
            print(f'Model pusher artifact: {model_pusher_artifact}')
        else:
            print("Trained model rejected.")
            print("Trained model rejected.")
        print("Training pipeline completed")



    """ This line creates an instance of the PythonOperator class, which is a built-in class in Airflow that allows you to define a Python function as a task in your DAG (Directed Acyclic Graph).
The PythonOperator takes several arguments, which are used to configure the task:
The first argument is the task_id, which is a unique identifier for the task within the DAG. In this case, it is 'data_ingestion'.
The second argument is the python_callable, which is the Python function that will be called when the task is executed. In this case, it is the function "data_ingestion"
It means that it is creating an instance of PythonOperator class with task_id 'data_ingestion' and python_callable function data_ingestion().
It is used to define a Python function data_ingestion() as a task in the DAG with id 'data_ingestion'.
This task will be executed by airflow when the DAG runs."""

    data_ingestion = PythonOperator(  
        task_id='data_ingestion',
        python_callable=data_ingestion,
    )
    data_ingestion.doc_md = dedent(
        """\
    #### Extract task
    A simple Extract task to get data ready for the rest of the data pipeline.
    In this case, getting data is simulated by reading from a hardcoded JSON string.
    This data is then put into xcom, so that it can be processed by the next task.
    """
    )

    data_validation = PythonOperator(
        task_id="data_validation",
        python_callable=data_validation

    )

    data_transformation = PythonOperator(
        task_id ="data_transformation",
        python_callable=data_transformation
    )

    model_trainer = PythonOperator(
        task_id="model_trainer", 
        python_callable=model_trainer

    )

    model_evaluation = PythonOperator(
        task_id="model_evaluation", python_callable=model_evaluation
    )   

    push_model  =PythonOperator(
            task_id="push_model",
            python_callable=push_model

    )

    data_ingestion >> data_validation >> data_transformation >> model_trainer >> model_evaluation >> push_model