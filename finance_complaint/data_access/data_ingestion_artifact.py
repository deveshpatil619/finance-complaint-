from finance_complaint.config.mongo_client import MongodbClient
from finance_complaint.entity.artifact_entity import DataIngestionArtifact


class DataIngestionArtifactData:

    def __init__(self):
        self.client = MongodbClient()
        self.collection_name = "data_ingestion_artifact"
        self.collection = self.client.database[self.collection_name]

    def save_ingestion_artifact(self, data_ingestion_artifact: DataIngestionArtifact):
        self.collection.insert_one(data_ingestion_artifact.to_dict())

    def get_ingestion_artifact(self, query):
        self.collection.find_one(query)

    def update_ingestion_artifact(self, query, data_ingestion_artifact: DataIngestionArtifact):
        self.collection.update_one(query, data_ingestion_artifact.to_dict())

    def remove_ingestion_artifact(self, query):
        self.collection.delete_one(query)

    def remove_ingestion_artifacts(self, query):
        self.collection.delete_many(query)

    def get_ingestion_artifacts(self, query):
        self.collection.find(query)
