TRUSTED_SOURCES = {"PubMed", "CDC", "WHO", "NICE", "ADA", "Drug Reference"}


def calculate_confidence(sources: list[dict]) -> dict:
    if not sources:
        return {
            "confidence": "Low",
            "reason": "No relevant trusted medical sources were found."
        }

    unique_trusted_sources = set()

    for source in sources:
        source_name = source.get("source")
        score = source.get("score") or 0

        if source_name in TRUSTED_SOURCES and score >= 0.40:
            unique_trusted_sources.add(source_name)

    count = len(unique_trusted_sources)

    if count == 0:
        return {
            "confidence": "Low",
            "reason": "Retrieved sources were not relevant enough to support the answer."
        }

    if count == 1:
        return {
            "confidence": "Medium",
            "reason": "Only one relevant trusted medical source supports the answer."
        }

    return {
        "confidence": "High",
        "reason": "Multiple relevant trusted medical sources support the answer."
    }