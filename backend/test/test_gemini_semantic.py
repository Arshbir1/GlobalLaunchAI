import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_MAIN_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro")

CHUNK_DIR = Path("data/chunked_country_jsons")
OUTPUT_DIR = Path("data/country_semantics")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COUNTRY_CODE = "AFG"
SECTOR = "healthtech"

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
        print(f"❌ Error parsing LLM output: {e}")
        print("⚠️ Raw response:\n", response)
        return {"summary": "", "indicators": {}, "error": str(e)}


def merge_chunks(results):
    full_summary = " ".join(chunk.get("summary", "") for chunk in results)
    indicators = {}
    for chunk in results:
        indicators.update(chunk.get("indicators", {}))
    return full_summary.strip(), indicators


def main():
    chunk_filepaths = sorted(CHUNK_DIR.glob(f"{COUNTRY_CODE}_chunk*.json"))
    if not chunk_filepaths:
        print(f"❌ No chunks found for {COUNTRY_CODE}")
        return

    print(f"🔍 Running test summary for {COUNTRY_CODE} | Sector: {SECTOR}")
    results = []

    for path in chunk_filepaths:
        with open(path, "r", encoding="utf-8") as f:
            chunk_data = json.load(f)
        if chunk_data:
            result = prompt_chunk(COUNTRY_CODE, SECTOR, chunk_data)
            results.append(result)

    summary, indicators = merge_chunks(results)
    if len(summary) > 9000:
        summary = summary[:9000].rsplit(" ", 1)[0] + "..."
        
    output = {
        "country_code": COUNTRY_CODE,
        "sector": SECTOR,
        "summary": summary,
        "key_indicators": indicators
    }

    out_path = OUTPUT_DIR / f"{COUNTRY_CODE}_{SECTOR}_TEST.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Test summary saved to {out_path}")


if __name__ == "__main__":
    main()


