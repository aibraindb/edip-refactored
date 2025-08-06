from pdfminer.high_level import extract_text
from typing import Optional

def extract_pdf_text(path: str) -> Optional[str]:
    try:
        return extract_text(path)
    except Exception as e:
        return None
