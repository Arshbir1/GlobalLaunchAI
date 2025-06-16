import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# === Setup ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_MAIN_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

# === Static Config ===
COUNTRY_CODE = "AUS"
SECTOR = "healthtech"
SEMANTIC_PATH = Path(f"data/country_semantics/{COUNTRY_CODE}_{SECTOR}_TEST.json")
OUTPUT_DIR = Path("data/country_insights")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STARTUP_DESC = (
    "A digital health startup offering remote diagnostics and telemedicine services, "
    "targeting underserved urban and rural populations, requiring strong broadband access, "
    "favorable regulations, and ease of entry for digital platforms."
)

# === Prompt Template ===
INSIGHT_PROMPT = """
You are an expert global expansion strategist advising startups on where to expand next.

Given the following multi-year country summary and relevant sector indicators,
analyze the overall attractiveness of the country: {country_code}, for a startup in the {sector} sector.

Consider market demand, digital infrastructure, regulatory complexity, entry barriers, trade incentives, economic stability,
and localized operational risks.

Write a concise strategic analysis (600–800 words) that captures how suitable this country is for a startup in this sector.
Be analytical, specific, and use relevant metrics from the data. Prioritize real-world expansion feasibility over generic fluff.

DATA:
{data}

STARTUP:
{startup_desc}
"""

def generate_insight_card(country_code, sector, startup_desc):
    # Step 1: Load semantic profile from local JSON
    if not SEMANTIC_PATH.exists():
        print(f"❌ Semantic file not found: {SEMANTIC_PATH}")
        return

    with open(SEMANTIC_PATH, "r", encoding="utf-8") as f:
        semantic_data = json.load(f)

    data_input = {
        "summary": semantic_data.get("summary", ""),
        "key_indicators": semantic_data.get("key_indicators", {})
    }

    try:
        # Step 2: Format the prompt
        prompt = INSIGHT_PROMPT.format(
            country_code=country_code,
            sector=sector,
            data=json.dumps(data_input, indent=2),
            startup_desc=startup_desc
        )

        # Step 3: Generate insight
        response = model.generate_content(prompt).text.strip()

        parsed = {
            "country_code": country_code,
            "sector": sector,
            "insight": response
        }

        # Step 4: Save to local file
        out_path = OUTPUT_DIR / f"{country_code}_{sector}_insight_TEST.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(parsed, f, indent=2)

        print(f"✅ Insight saved locally to: {out_path}")
        return parsed

    except Exception as e:
        print(f"❌ Error generating insight: {str(e)}")


if __name__ == "__main__":
    result = generate_insight_card(COUNTRY_CODE, SECTOR, STARTUP_DESC)
    if result and "insight" in result:
        print("\n🧠 Insight Preview:\n")
        print(result["insight"][:1000] + "..." if len(result["insight"]) > 1000 else result["insight"])
