# ✅ chatbot.py — Gemini-powered RAG-style chatbot for GlobalLaunch AI

import os
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
reports_col = db["country_reports"]

# === Prompt Template ===
CHAT_PROMPT_TEMPLATE = """
You are GlobalLaunch AI, a strategic international expansion advisor for startups.

Answer the user's question using the following AI-generated country expansion reports for the top 5 suggested countries.

Always be clear and concise. If comparing countries, synthesize key differences or benefits. If answering about a specific country, highlight the relevant data.

--- USER QUESTION ---
{user_question}

--- COUNTRY REPORTS ---
{formatted_reports}

Avoid saying "I don't have access" or "not enough data" — instead, offer useful and cautious recommendations based on what's available.
"""

# === Helper to format report content concisely ===
def format_report_for_prompt(report):
    return f"""
🔹 Country: {report['country_code']}

• Market Opportunity: {report['market_opportunity']['overview']}
• Regulatory Brief: {report['regulatory_brief']['licensing']}
• Risk (Economic): {report['risk_analysis']['economic_risks']}
• Trade Incentives: {report['trade_incentives']['tax_reliefs']}
• Expansion Strategy: {report['expansion_guide']['overview']}
• Local Culture: {report['localized_factors']['culture']}
    """.strip()

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

# === Main Chat Handler ===
def generate_answer(question: str, top_countries: list) -> str:
    # Fetch relevant reports from DB
    reports = list(reports_col.find(
        {"country_code": {"$in": top_countries}},
        {"_id": 0}
    ))

    if not reports:
        return "Sorry, no data available for the selected countries."

    formatted_reports = "\n\n".join(format_report_for_prompt(r) for r in reports)

    final_prompt = CHAT_PROMPT_TEMPLATE.format(
        user_question=question,
        formatted_reports=formatted_reports
    )

    print("🔍 Sending prompt to Gemini...")
    response = safe_generate(final_prompt)
    return response


