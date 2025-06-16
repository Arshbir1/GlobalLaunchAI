# ✅ get_final_shortlist.py (Final Ranking with Indicator Weights)

import os
from dotenv import load_dotenv
from pymongo import MongoClient
from fallback_sector_detection import detect_sectors
import vertexai
from vertexai.preview.language_models import TextEmbeddingModel
from google.oauth2 import service_account

# === Setup ===
load_dotenv()
# vertexai.init(project=os.getenv("PROJECT_ID"), location="us-central1")
credentials = service_account.Credentials.from_service_account_file(os.getenv("SERVICE_ACCOUNT_PATH"))


vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location="us-central1",
    credentials=credentials
)
embedding_model = TextEmbeddingModel.from_pretrained("gemini-embedding-001")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
semantics_col = db["country_semantics"]

PATH_NAME = os.getenv("SEMANTIC_EMBEDDING")
INDEX_NAME = os.getenv("SEMANTIC_IDX")

# === Weights for scoring ===
WEIGHTS = {
    "vector": 0.6,
    "digital_index": 0.1,
    "fdi_inflows_millions": 0.1,
    "corruption_index": 0.1,
    "ease_of_starting_business": 0.1
}

# === Embed query ===
def embed_query(text):
    return embedding_model.get_embeddings([text])[0].values

# === Sector-aware vector search ===
def vector_search_country_semantics(query_embedding, sector, top_k=200):
    return list(semantics_col.aggregate([
        {
            "$vectorSearch": {
                "index": INDEX_NAME,
                "path": PATH_NAME,
                "queryVector": query_embedding,
                "numCandidates": 500,
                "limit": top_k
            }
        },
        {"$match": {"sector": {"$regex": f"^{sector}$", "$options": "i"}}},
        {"$project": {
            "_id": 0,
            "country_code": 1,
            "sector": 1,
            "score": {"$meta": "vectorSearchScore"},
            "summary": 1,
            "key_indicators": 1
        }}
    ]))

# === Utility to extract indicator score safely ===
def extract_score(indicators, key):
    val = indicators.get(key, 0)
    return val.get("score", 0) if isinstance(val, dict) else val

# === Main shortlist with final score computation ===
def get_shortlist(user_input, top_n=5):
    sectors = detect_sectors(user_input)
    query_vector = embed_query(user_input)

    print(f"🔎 Detected sectors: {sectors}")

    country_data = {}

    for sector in sectors:
        results = vector_search_country_semantics(query_vector, sector)
        for doc in results:
            code = doc["country_code"]
            vec_score = doc["score"]
            indicators = doc.get("key_indicators", {})

            if code not in country_data:
                country_data[code] = {
                    "vector_score": 0.0,
                    "matched_sectors": set(),
                    "indicators": {}
                }

            if sector not in country_data[code]["matched_sectors"]:
                country_data[code]["vector_score"] += vec_score
                country_data[code]["matched_sectors"].add(sector)

            country_data[code]["indicators"].update(indicators)

    # Compute final weighted score
    ranked = []
    for code, data in country_data.items():
        indicators = data["indicators"]
        score = 0
        score += data["vector_score"] * WEIGHTS["vector"]
        score += (extract_score(indicators, "digital_index") / 100) * WEIGHTS["digital_index"]
        score += (extract_score(indicators, "fdi_inflows_millions") / 100000) * WEIGHTS["fdi_inflows_millions"]
        score += ((100 - extract_score(indicators, "corruption_index")) / 100) * WEIGHTS["corruption_index"]
        score += (extract_score(indicators, "ease_of_starting_business") / 100) * WEIGHTS["ease_of_starting_business"]

        ranked.append({
            "country_code": code,
            "aggregate_score": round(score, 4),
            "matched_sectors": list(data["matched_sectors"])
        })

    return sorted(ranked, key=lambda x: -x["aggregate_score"])[:top_n]

# === CLI test ===
if __name__ == "__main__":
    user_input = "We have made an AI-ML platform to help farmers"
    top = get_shortlist(user_input, top_n=5)

    print("\n🏁 Top Countries:")
    for item in top:
        print(f"{item['country_code']} → {item['aggregate_score']} via {item['matched_sectors']}")
