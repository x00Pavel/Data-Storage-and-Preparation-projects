import pymongo
import os
import dotenv
from enum import Enum
from common import current_location

class ConnectionType(Enum):
    LOCAL = "local"
    REMOTE = "remote"


dotenv.load_dotenv(current_location.joinpath("../.env"))

class Database():

    def __init__(self, db_name: str, collection_name: str, connection_type):
        env_var = "MONGO_URI" if connection_type == ConnectionType.REMOTE else "MONGO_LOCAL_URI"
        url = os.getenv(env_var)
        print(f"Connecting to database {url}")
        self.client = pymongo.MongoClient(url)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def insert(self, data: dict):
        self.collection.insert_one(data)

    def find(self, query: dict):
        return self.collection.find(query)

    def find_one(self, query: dict):
        return self.collection.find_one(query)

    def update(self, query: dict, data: dict):
        self.collection.update_one(query, {"$set": data})

    def delete(self, query: dict):
        self.collection.delete_one(query)

    def delete_many(self, query: dict):
        self.collection.delete_many(query)

    def count(self, query: dict):
        return self.collection.count_documents(query)

    def drop(self):
        self.collection.drop()

    def close(self):
        self.client.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()