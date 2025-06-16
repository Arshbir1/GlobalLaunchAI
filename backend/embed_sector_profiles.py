# import os
# import time
# from pymongo import MongoClient
# from dotenv import load_dotenv
# from vertexai.preview.language_models import TextEmbeddingModel
# import vertexai

# # === Setup ===
# load_dotenv()
# vertexai.init(project=os.getenv("PROJECT_ID"), location="us-central1")
# model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")

# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client[os.getenv("DB_NAME")]
# collection = db["country_semantics"]
# SEMANTIC_EMBEDDING = os.getenv("SEMANTIC_EMBEDDING")

# # === Embedding Loop with proper cursor handling ===
# cursor = collection.find(no_cursor_timeout=True)
# try:
#     for doc in cursor:
#         try:
#             summary = doc.get("summary")
#             if not summary:
#                 continue

#             # Skip if already embedded
#             if "embedding" in doc:
#                 print(f"⏩ Skipped {doc['country_code']} - {doc['sector']} (already embedded)")
#                 continue

#             embedding = model.get_embeddings([summary])[0].values

#             # Prefer _id, fallback to compound key
#             filter_query = {"_id": doc["_id"]} if "_id" in doc else {
#                 "country_code": doc["country_code"],
#                 "sector": doc["sector"]
#             }

#             collection.update_one(
#                 filter_query,
#                 {"$set": {SEMANTIC_EMBEDDING: embedding}}
#             )
#             print(f"✅ Embedded {doc['country_code']} - {doc['sector']}")
#             time.sleep(12.5)  # avoid quota exceed
#         except Exception as e:
#             print(f"❌ Failed {doc.get('country_code')} - {doc.get('sector')}: {e}")
# finally:
#     cursor.close()










import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from vertexai.preview.language_models import TextEmbeddingModel
import vertexai

# === Setup ===
load_dotenv()
vertexai.init(project=os.getenv("PROJECT_ID"), location="us-central1")
model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
collection = db["country_semantics"]
SEMANTIC_EMBEDDING = os.getenv("SEMANTIC_EMBEDDING")

BATCH_SIZE = 10

while True:
    docs = list(collection.find(
        {
            "summary": {"$exists": True, "$ne": ""},
            SEMANTIC_EMBEDDING: {"$exists": False}
        }
    ).limit(BATCH_SIZE))

    if not docs:
        print("✅ All documents embedded.")
        break

    for doc in docs:
        try:
            summary = doc["summary"]
            embedding = model.get_embeddings([summary])[0].values

            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {SEMANTIC_EMBEDDING: embedding}}
            )
            print(f"✅ Embedded {doc['country_code']} - {doc['sector']}")
            time.sleep(12.5)  # rate limit
        except Exception as e:
            print(f"❌ Failed {doc.get('country_code')} - {doc.get('sector')}: {e}")



