from pymongo import MongoClient
import pandas as pd
import os

def upload_csv_metadata(mongo_uri, db_name="GlobalLaunchAI", collection_name="country_datasets"):
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[collection_name]

    folder_path = "data/datasets"
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(".csv"):
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path)
                    doc = {
                        "_id": os.path.relpath(file_path, folder_path),  # unique ID based on relative path
                        "preview": df.head(10).to_dict(orient="records"),
                        "shape": df.shape,
                        "path": file_path
                    }
                    collection.replace_one({"_id": doc["_id"]}, doc, upsert=True)
                except Exception as e:
                    print(f"⚠️ Failed to read {file_path}: {e}")

    print("✅ CSV metadata uploaded to MongoDB.")

