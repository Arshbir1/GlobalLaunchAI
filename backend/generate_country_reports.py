# ✅ generate_country_reports.py (Final Report Generator)

import os
import json
import time
import random
from dotenv import load_dotenv
from pymongo import MongoClient
import google.generativeai as genai

# === Setup ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

client = MongoClient(os.getenv("MONGODB_URI"))
db = client[os.getenv("DB_NAME")]
semantics_col = db["country_semantics"]
reports_col = db["country_reports"]

# === Strict Prompt Template (UPDATED) ===
REPORT_PROMPT = """
You are GlobalLaunch AI — an expert advisor for international startup expansion.

Using the following sector-level summaries and their key indicator values for {country_code}, generate a structured 6-part country expansion report to help startup founders assess feasibility.

--- SECTORS ---
{sectors}

--- DATA (including indicators) ---
{data}

--- STARTUP IDEA ---
{startup_desc}

You must:
- Analyze the key indicators (e.g., FDI inflows, inflation, ease of business, digital index) and use them to inform feasibility insights.
- If multiple sectors show different trends, reconcile them or highlight contrasting implications.
- Avoid saying "data unavailable"; use general insights if data is thin.

Return a valid JSON object using exactly the structure shown below. No explanations outside the JSON.

{{
  "market_opportunity": {{
    "overview": "...",
    "sector_trends": ["...", "..."],
    "demand_signals": ["...", "..."]
  }},
  "regulatory_brief": {{
    "licensing": "...",
    "data_laws": "...",
    "compliance_notes": ["...", "..."]
  }},
  "risk_analysis": {{
    "economic_risks": "...",
    "political_risks": "...",
    "corruption_risks": "..."
  }},
  "trade_incentives": {{
    "tax_reliefs": "...",
    "grants": "...",
    "investment_support": ["...", "..."]
  }},
  "expansion_guide": {{
    "overview": "...",
    "market_entry_strategy": ["...", "..."],
    "operational_considerations": ["...", "..."],
    "legal_and_regulatory_compliance": ["...", "..."]
  }},
  "localized_factors": {{
    "overview": "...",
    "language": "...",
    "culture": "...",
    "local_expertise": "...",
  }}
}}
"""


# === Gemini-safe wrapper ===
def safe_generate(prompt, max_retries=5):
    for attempt in range(max_retries):
        try:
            return model.generate_content(prompt).text.strip()
        except Exception as e:
            wait_time = (2 ** attempt) + random.uniform(0.5, 3)
            print(f"⚠️ Gemini error: {e} — retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)
    raise RuntimeError("❌ Gemini failed after max retries.")

# === Main Function ===
def generate_final_reports(startup_desc: str, shortlist: list):
    for item in shortlist:
        country_code = item["country_code"]
        sectors = item["matched_sectors"]

        cached = reports_col.find_one({
            "country_code": country_code,
            "matched_sectors": {"$all": sectors},
            "report_generated": True
        })
        if cached:
            print(f"🟡 Skipping (cached): {country_code}")
            continue

        data_input = []
        for sector in sectors:
            doc = semantics_col.find_one({"country_code": country_code, "sector": sector})
            if not doc:
                continue
            data_input.append({
                "sector": sector,
                "summary": doc.get("summary", ""),
                "key_indicators": doc.get("key_indicators", {})
            })

        if not data_input:
            print(f"⚠️ Skipping {country_code} — no semantic data.")
            continue

        try:
            prompt = REPORT_PROMPT.format(
                country_code=country_code,
                sectors=", ".join(sectors),
                data=json.dumps(data_input, indent=2),
                startup_desc=startup_desc
            )

            response = safe_generate(prompt)
            if response.startswith("```json"):
                response = response.strip("` ").split("\n", 1)[1].strip()

            parsed = json.loads(response)

            reports_col.update_one(
                {"country_code": country_code},
                {"$set": {
                    "country_code": country_code,
                    "matched_sectors": sectors,
                    "startup_desc": startup_desc,
                    "report_generated": True,
                    **parsed
                }},
                upsert=True
            )

            print(f"✅ Report saved: {country_code}")
            time.sleep(5)

        except Exception as e:
            print(f"❌ Failed {country_code} — {e}")