from pymongo import MongoClient
import os

mongo_url = "mongodb+srv://PII_db:8FvcfxiBQc7DE4Aa@cluster0.buaqkbz.mongodb.net/?appName=Cluster0"
client = MongoClient(mongo_url)
db = client["PII_extractor"]

print(f"Collections: {db.list_collection_names()}")
if "document_records" in db.list_collection_names():
    count = db.document_records.count_documents({})
    print(f"Documents in document_records: {count}")
    for doc in db.document_records.find().limit(1):
        print(f"Sample Doc ID: {doc.get('_id')}")
        print(f"Sample Filename: {doc.get('filename')}")
