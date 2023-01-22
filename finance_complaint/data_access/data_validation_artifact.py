from finance_complaint.config.mongo_client import MongodbClient
from finance_complaint.entity.artifact_entity import DataValidationArtifact


class DataValidationArtifactData:

    def __init__(self):
        self.client = MongodbClient()
        self.collection_name = "data_validation_artifact"
        self.collection = self.client.database[self.collection_name]

    def save_validation_artifact(self, data_validation_artifact: DataValidationArtifact):
        self.collection.insert_one(data_validation_artifact.to_dict())

    def get_validation_artifact(self, query):
        self.collection.find_one(query)

    def update_validation_artifact(self, query, data_validation_artifact: DataValidationArtifact):
        self.collection.update_one(query, data_validation_artifact.to_dict())

    def remove_validation_artifact(self, query):
        self.collection.delete_one(query)

    def remove_validation_artifacts(self, query):
        self.collection.delete_many(query)

    def get_validation_artifacts(self, query):
        self.collection.find(query)
