# core/splitter.py
import re

def split_into_items(text: str, mode: str = "paragraph") -> list:
    """
    Split text into indexed items based on mode.
    Returns: [{'idx': 0, 'content': '...'}, ...]
    """
    if mode == "paragraph":
        chunks = re.split(r'\n\s*\n', text)
    elif mode == "sentence":
        chunks = re.split(r'(?<=[.!?])\s+', text)
    elif mode == "line":
        chunks = text.splitlines()
    else:
        chunks = [text.strip()]

    return [
        {"idx": i, "content": chunk.strip()}
        for i, chunk in enumerate(chunks) if chunk.strip()
    ]
