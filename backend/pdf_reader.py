# pdf_reader.py
import fitz  # PyMuPDF
from typing import List, Tuple
from fallback_sector_detection import detect_sectors

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF using PyMuPDF.
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text.strip()


def detect_sectors_from_pdf(pdf_path: str, max_results: int = 3) -> Tuple[List[str], str]:
    """
    Extracts text from a PDF, detects business sectors using fallback logic.
    Returns a tuple: (top matching sectors, raw extracted text).
    """
    text = extract_text_from_pdf(pdf_path)
    sectors = detect_sectors(text, max_results=max_results)
    return sectors, text


# === CLI test ===
if __name__ == "__main__":
    test_path = "samples/sample_pitchdeck.pdf"  # Update to your test file
    sectors, raw_text = detect_sectors_from_pdf(test_path)

    print("✅ Detected Sectors:", sectors)
    print("\n--- Extracted Text Preview ---\n")
    print(raw_text[:1500], "...")  # Just a preview
