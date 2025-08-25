# utils/helpers.py
import re

def clean_text(text: str) -> str:
    """
    Normalize whitespace and clean input text.
    """
    return re.sub(r'\s+', ' ', text.strip())
