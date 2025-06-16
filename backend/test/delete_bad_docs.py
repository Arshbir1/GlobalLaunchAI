# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os

# # === Setup ===
# load_dotenv()
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client[os.getenv("DB_NAME")]
# collection = db["country_semantics"]

# # === Filter for failed entries
# failed_filter = {
#     "$and": [
#         {"$or": [{"summary": {"$exists": False}}, {"summary": ""}]},
#         {"$or": [{"key_indicators": {"$exists": False}}, {"key_indicators": {}}]}
#     ]
# }

# # === Preview failed documents
# docs = list(collection.find(failed_filter))
# print(f"🔍 Found {len(docs)} failed documents:")
# for doc in docs:
#     print(f"⛔ {doc.get('country_code')} - {doc.get('sector')}")
    
# result = collection.delete_many(failed_filter)
# print(f"✅ Deleted {result.deleted_count} failed semantic documents.")








from pymongo import MongoClient
from bson import json_util
from dotenv import load_dotenv
import os

# === Setup ===
load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["country_semantics"]

# === Fetch NZL - mobility document
doc = collection.find_one({"country_code": "NZL", "sector": "mobility"})

if doc:
    print(json_util.dumps(doc, indent=2))
else:
    print("❌ Document not found.")


