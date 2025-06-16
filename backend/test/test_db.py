from pymongo.mongo_client import MongoClient
from json_to_mongo import upload_country_jsons_to_mongodb
from csv_to_mongo import upload_csv_metadata

import os
from dotenv import load_dotenv
load_dotenv()

uri = os.getenv("MONGODB_URI")

# Create a new client and connect to the server
client = MongoClient(uri)

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    upload_csv_metadata(uri)
    upload_country_jsons_to_mongodb(uri)
except Exception as e:
    print(e)