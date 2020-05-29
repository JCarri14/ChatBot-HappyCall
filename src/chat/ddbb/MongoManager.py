from pymongo import MongoClient
import datetime

# Meant to be used in case any ODM implementation could not fulfill the needs
# Using singleton pattern
class MongoManager:

    __instance = None
    
    class __Manager:
        
        def __init__(self, host, port, database):
            self.client = MongoClient(host, port)
            self.db = self.client[database]
            self.collection = None
    
    instance = None

    def __init__(self):
        if not MongoManager.instance:
            MongoManager.instance = MongoManager.__Manager()
        
    def set_collection(self, collection):
        self.instance.collection = self.instance.db[collection]

    def insert_document(self, collection, item):
        self.set_collection(collection)
        self.instance.collection.insert_one(item)
    
    def insert_document(self, item):
        self.instance.collection.insert_one(item)

    def get_documents(self, collection):
        items = []
        self.instance.collection = self.instance.db[collection]
        for item in self.instance.collection.find():
            print(item)

