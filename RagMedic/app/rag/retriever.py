from app.rag.embeddings import create_embedding
from app.rag.qdrant_store import search_medical_chunks

TRUSTED_SOURCES = {"PubMed", "CDC", "WHO", "NICE", "ADA", "Drug Reference"}
MIN_SCORE = 0.20

SOURCE_PRIORITY = {
    "NICE": 0.08,
    "WHO": 0.06,
    "CDC": 0.05,
    "ADA": 0.05,
    "PubMed": 0.03,
}


def retrieve_context(query: str, limit: int = 15):
    query_vector = create_embedding(query)

    results = search_medical_chunks(query_vector, limit)

    ranked_results = []

    for r in results:
        payload = r.payload or {}
        source_name = payload.get("source", "Unknown")
        text = payload.get("text", "").strip()

        if source_name not in TRUSTED_SOURCES:
            continue

        if not text:
            continue

        score = getattr(r, "score", 0) or 0

        # Reject weak semantic matches
        if score < MIN_SCORE:
            continue

        adjusted_score = score + SOURCE_PRIORITY.get(source_name, 0)

        # Boost chunks with clinical numbers/targets/dosages
        if any(char.isdigit() for char in text):
            adjusted_score += 0.05

        # Boost likely clinical target chunks
        clinical_terms = [
            "hba1c",
            "mmol/mol",
            "target",
            "%",
            "dose",
            "dosage",
            "recommended",
            "first-line",
            "metformin",
        ]

        if any(term in text.lower() for term in clinical_terms):
            adjusted_score += 0.05

        ranked_results.append((adjusted_score, r))

    ranked_results.sort(key=lambda x: x[0], reverse=True)

    context_parts = []
    sources = []
    seen_urls = set()

    for adjusted_score, r in ranked_results[:8]:
        payload = r.payload or {}

        source_name = payload.get("source", "Unknown")
        title = payload.get("title", "Untitled")
        url = payload.get("url")
        text = payload.get("text", "").strip()

        unique_key = f"{url}-{text[:80]}"

        if unique_key in seen_urls:
            continue

        seen_urls.add(unique_key)

        context_parts.append(
            f"""
Source: {source_name}
Title: {title}
URL: {url}
Score: {round(adjusted_score, 4)}
Content:
{text}
"""
        )

        sources.append({
            "title": title,
            "source": source_name,
            "url": url,
            "score": round(adjusted_score, 4),
            "snippet": text[:300],
        })

    context = "\n\n".join(context_parts)
    context = context[:8000]

    return context, sources