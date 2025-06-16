# import os
# import json
# import google.generativeai as genai
# from dotenv import load_dotenv
# from pathlib import Path
# from pymongo import MongoClient

# load_dotenv()
# genai.configure(api_key=os.getenv("GOOGLE_MAIN_API_KEY"))
# model = genai.GenerativeModel("gemini-1.5-pro")

# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client[os.getenv("DB_NAME")]
# semantics_collection = db["country_semantics"]

# CHUNK_DIR = Path("data/chunked_country_jsons")
# OUTPUT_DIR = Path("data/country_semantics")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# SECTORS = [
#     "fintech", "healthtech", "edtech", "ecommerce", "cleantech",
#     "logistics", "SaaS", "cybersecurity", "AI-ML", "retail",
#     "agritech", "mobility", "proptech", "govtech", "biotech"
# ]

# # ✅ Improved prompt with stronger sector anchoring
# CHUNK_PROMPT_TEMPLATE = """
# You are a global business analyst creating country-level investment insights.

# Given the following structured data for country: {country_code} and sector: {sector}, generate a concise, sector-specific profile using ONLY the provided data.

# 🎯 Your goal:
# - Describe the country's strengths, risks, and trends that affect companies in the "{sector}" space.
# - Include concrete numerical indicators (e.g. 5G %, inflation, FDI, business scores).
# - Link data points explicitly to sector relevance. For example, for healthtech, mention internet access, regulatory transparency, medical supply chain reliability, etc.
# - Keep it focused, realistic, and grounded in data — do not speculate beyond what's present.

# 📝 Return JSON like:
# {{
#   "summary": "...",  # ≤3000 chars
#   "indicators": {{ ... }}
# }}

# 📦 Chunked Country Data:
# {chunk_data}
# """

# def prompt_chunk(country_code, sector, chunk_data):
#     try:
#         trimmed_data = json.dumps(chunk_data)[:11000]  # leave ~1K for prompt text
#         prompt = CHUNK_PROMPT_TEMPLATE.format(
#             country_code=country_code,
#             sector=sector,
#             chunk_data=trimmed_data
#         )
#         response = model.generate_content(prompt).text.strip()

#         # Handle markdown-style code blocks like ```json ... ```
#         if response.startswith("```json"):
#             response = response.strip("` \n")
#             response = response[len("json"):].strip()

#         result = json.loads(response)

#         summary = result.get("summary", "")
#         if len(summary) > 3000:
#             summary = summary[:3000].rsplit(" ", 1)[0] + "..."
#             result["summary"] = summary

#         return result

#     except Exception as e:
#         print(f"❌ Exception while parsing LLM output: {e}")
#         print("⚠️ Raw response:\n", response)
#         return {"summary": "", "indicators": {}, "error": str(e)}


# def merge_chunks(results):
#     full_summary = " ".join(chunk.get("summary", "") for chunk in results)
#     indicators = {}
#     for chunk in results:
#         indicators.update(chunk.get("indicators", {}))
#     return full_summary.strip(), indicators


# def generate_semantic_profile(country_code, sector, chunk_filepaths):
#     chunks = []
#     for chunk_path in sorted(chunk_filepaths):
#         with open(chunk_path, "r", encoding="utf-8") as f:
#             chunk_data = json.load(f)
#         if not chunk_data:
#             chunks.append({"summary": "", "indicators": {}})
#             continue
#         result = prompt_chunk(country_code, sector, chunk_data)
#         chunks.append(result)

#     summary, indicators = merge_chunks(chunks)

#     return {
#         "sector": sector,
#         "country_code": country_code,
#         "summary": summary,
#         "key_indicators": indicators
#     }


# def main():
#     # Group chunk files by country
#     chunk_files_by_country = {}
#     for file in CHUNK_DIR.glob("*.json"):
#         if "_" not in file.stem:
#             continue
#         country_code = file.stem.split("_")[0]
#         chunk_files_by_country.setdefault(country_code, []).append(file)

#     for country_code, chunk_filepaths in chunk_files_by_country.items():
#         for sector in SECTORS:
#             print(f"🔍 {country_code} | {sector}")
#             semantic = generate_semantic_profile(country_code, sector, chunk_filepaths)

#             if "summary" in semantic:
#                 out_path = OUTPUT_DIR / f"{country_code}_{sector}.json"
#                 with open(out_path, "w", encoding="utf-8") as f:
#                     json.dump(semantic, f, indent=2)
#                 print(f"✅ Saved {out_path}")

#                 semantics_collection.update_one(
#                     {"country_code": country_code, "sector": sector},
#                     {"$set": semantic},
#                     upsert=True
#                 )
#                 print(f"☁️  Pushed to MongoDB: {country_code} [{sector}]")
#             else:
#                 print(f"❌ Failed for {country_code} {sector}")


# if __name__ == "__main__":
#     main()





















import os
import json
import time
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
from pymongo import MongoClient

# === Setup ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_MAIN_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
semantics_collection = db["country_semantics"]

CHUNK_DIR = Path("data/chunked_country_jsons")
OUTPUT_DIR = Path("data/country_semantics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SECTORS = [
    "fintech", "healthtech", "edtech", "ecommerce", "cleantech",
    "logistics", "SaaS", "cybersecurity", "AI-ML", "retail",
    "agritech", "mobility", "proptech", "govtech", "biotech"
]

START_COUNTRY = "NZL"
START_SECTOR = "proptech"

CHUNK_PROMPT_TEMPLATE = """
You are a global business analyst creating country-level investment insights.

Given the following structured data for country: {country_code} and sector: {sector}, generate a concise, sector-specific profile using ONLY the provided data.

🎯 Your goal:
- Describe the country's strengths, risks, and trends that affect companies in the "{sector}" space.
- Include concrete numerical indicators (e.g. 5G %, inflation, FDI, business scores).
- Link data points explicitly to sector relevance. For example, for healthtech, mention internet access, regulatory transparency, medical supply chain reliability, etc.
- Keep it focused, realistic, and grounded in data — do not speculate beyond what's present.

📝 Return JSON like:
{{
  "summary": "...",  # ≤3000 chars
  "indicators": {{ ... }}
}}

📦 Chunked Country Data:
{chunk_data}
"""

def prompt_chunk(country_code, sector, chunk_data):
    try:
        trimmed_data = json.dumps(chunk_data)[:11000]
        prompt = CHUNK_PROMPT_TEMPLATE.format(
            country_code=country_code,
            sector=sector,
            chunk_data=trimmed_data
        )
        response = model.generate_content(prompt).text.strip()

        if response.startswith("```json"):
            response = response.strip("` \n")
            response = response[len("json"):].strip()

        result = json.loads(response)

        summary = result.get("summary", "")
        if len(summary) > 3000:
            summary = summary[:3000].rsplit(" ", 1)[0] + "..."
            result["summary"] = summary

        return result

    except Exception as e:
        print(f"❌ Exception while parsing LLM output: {e}")
        print("⚠️ Raw response:\n", response if 'response' in locals() else 'No response')
        return {"summary": "", "indicators": {}, "error": str(e)}

def merge_chunks(results):
    full_summary = " ".join(chunk.get("summary", "") for chunk in results)
    indicators = {}
    for chunk in results:
        indicators.update(chunk.get("indicators", {}))
    return full_summary.strip(), indicators

def generate_semantic_profile(country_code, sector, chunk_filepaths):
    chunks = []
    for chunk_path in sorted(chunk_filepaths):
        with open(chunk_path, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)
        if not chunk_data:
            chunks.append({"summary": "", "indicators": {}})
            continue
        result = prompt_chunk(country_code, sector, chunk_data)
        chunks.append(result)
        time.sleep(0.5)  # Gemini rate limit
    summary, indicators = merge_chunks(chunks)
    return {
        "sector": sector,
        "country_code": country_code,
        "summary": summary,
        "key_indicators": indicators
    }

def should_resume(country_code, sector):
    if country_code < START_COUNTRY:
        return False
    if country_code == START_COUNTRY and SECTORS.index(sector) < SECTORS.index(START_SECTOR):
        return False
    return True

def main():
    print("✅ Script Started")

    if not CHUNK_DIR.exists():
        print(f"❌ Directory does not exist: {CHUNK_DIR}")
        return

    chunk_files_by_country = {}
    for file in CHUNK_DIR.glob("*.json"):
        parts = file.stem.split("_")
        if len(parts) < 3:
            continue
        country_code = parts[0]
        chunk_files_by_country.setdefault(country_code, []).append(file)

    for country_code in sorted(chunk_files_by_country):
        for sector in SECTORS:
            if not should_resume(country_code, sector):
                continue

            print(f"\n🔍 Processing {country_code} | Sector: {sector}")
            semantic = generate_semantic_profile(country_code, sector, chunk_files_by_country[country_code])

            if "summary" in semantic:
                out_path = OUTPUT_DIR / f"{country_code}_{sector}.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(semantic, f, indent=2)
                print(f"✅ Saved to {out_path.name}")

                semantics_collection.update_one(
                    {"country_code": country_code, "sector": sector},
                    {"$set": semantic},
                    upsert=True
                )
                print(f"☁️  Updated MongoDB: {country_code} [{sector}]")
            else:
                print(f"❌ Failed for {country_code} {sector}")

if __name__ == "__main__":
    main()



