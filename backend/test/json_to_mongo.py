from pymongo import MongoClient
import json
import os

def upload_country_jsons_to_mongodb(mongo_uri, db_name="GlobalLaunchAI", collection_name="country_profiles"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    folder_path = "data/country_jsons"

    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            iso_code = filename.replace(".json", "")
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                data["_id"] = iso_code  # Use ISO as document _id to prevent duplicates
                collection.replace_one({"_id": iso_code}, data, upsert=True)

    print("✅ All JSON files uploaded to MongoDB Atlas.")

# Example usage:
# upload_country_jsons_to_mongodb("mongodb+srv://admin:<password>@cluster.mongodb.net/?retryWrites=true&w=majority")
