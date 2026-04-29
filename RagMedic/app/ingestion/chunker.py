def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    if not text or not text.strip():
        return []

    text = " ".join(text.split())

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if len(chunk) > 80:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks