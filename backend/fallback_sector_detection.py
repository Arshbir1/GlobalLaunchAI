# import re
# from collections import defaultdict

# SECTORS = [
#     "fintech", "healthtech", "edtech", "ecommerce", "cleantech",
#     "logistics", "SaaS", "cybersecurity", "AI-ML", "retail",
#     "agritech", "mobility", "proptech", "govtech", "biotech"
# ]

# def detect_sectors(user_input, max_results=3):
#     keywords = {
#         "fintech": ["finance", "bank", "payment", "payments", "wallet", "kyc", "remittance", "loan", "fintech", "investing", "credit"],
#         "healthtech": ["health", "hospital", "clinic", "doctor", "nurse", "medical", "telemedicine", "wellness", "pharma", "healthcare"],
#         "edtech": ["education", "learning", "school", "student", "tutor", "online course", "lms", "elearning", "teaching"],
#         "ecommerce": ["shop", "retail", "buy", "sell", "marketplace", "checkout", "store", "ecommerce", "cart"],
#         "cleantech": ["renewable", "sustainability", "solar", "wind", "energy", "green", "carbon", "cleantech", "emissions", "ev", "electric vehicle"],
#         "logistics": ["delivery", "shipping", "supply chain", "freight", "warehouse", "logistics", "fleet", "tracking"],
#         "SaaS": ["software", "b2b", "subscription", "platform", "cloud", "crm", "erp", "saas"],
#         "cybersecurity": ["security", "encryption", "firewall", "antivirus", "threat", "cyber", "malware", "phishing"],
#         "AI-ML": ["ai", "machine learning", "ml", "deep learning", "nlp", "neural", "predictive", "generative", "llm"],
#         "retail": ["store", "shopping", "mall", "consumer", "retail", "sales", "products"],
#         "agritech": ["agriculture", "farming", "crop", "farm", "drone", "yield", "agritech", "soil", "agro"],
#         "mobility": ["transport", "ride", "vehicle", "car", "scooter", "mobility", "commute", "electric vehicle", "ev"],
#         "proptech": ["real estate", "property", "housing", "rent", "buying house", "mortgage", "proptech", "brokerage"],
#         "govtech": ["government", "public sector", "policy", "citizen", "govtech", "e-governance", "regulation"],
#         "biotech": ["biology", "biotech", "dna", "genomics", "life sciences", "pharmaceutical", "biological", "biomedical"]
#     }

#     user_input = user_input.lower()
#     match_counts = defaultdict(int)

#     for sector, terms in keywords.items():
#         for term in terms:
#             # use word boundary matching for precision
#             if re.search(rf"\b{re.escape(term)}\b", user_input):
#                 match_counts[sector] += 1

#     if not match_counts:
#         print("⚠️ No specific sector detected — using 'general'.")
#         return ["general"]

#     # Sort and return top N sectors
#     sorted_sectors = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)
#     top_matches = [sector for sector, _ in sorted_sectors[:max_results]]

#     return top_matches













import os
import google.generativeai as genai
from dotenv import load_dotenv

# === Setup ===
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

SECTORS = [
    "fintech", "healthtech", "edtech", "ecommerce", "cleantech",
    "logistics", "SaaS", "cybersecurity", "AI-ML", "retail",
    "agritech", "mobility", "proptech", "govtech", "biotech"
]

def detect_sectors(user_input, max_results=3):
    prompt = f"""
You are a startup classification assistant. Your job is to classify a given business idea into at most {max_results} relevant sectors from this fixed list:

{", ".join(SECTORS)}

Business idea:
\"\"\"{user_input.strip()}\"\"\"

Respond ONLY with a valid Python list of up to {max_results} matching sector names. Do not explain or add anything else.
Example format: ["SaaS", "AI-ML"]
"""

    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt)

    try:
        result = eval(response.text.strip())
        # Filter to ensure result is valid
        valid = [s for s in result if s in SECTORS]
        return valid[:max_results] if valid else ["general"]
    except Exception:
        print("⚠️ Failed to parse Gemini response. Falling back to ['general'].")
        return ["general"]


