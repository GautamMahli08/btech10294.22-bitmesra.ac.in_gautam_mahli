TRUSTED_SOURCES = {"PubMed", "CDC", "WHO", "NICE", "ADA", "Drug Reference"}


def is_good_enough(sources: list[dict], question: str) -> bool:
    if not sources:
        return False

    top_score = max([s.get("score", 0) or 0 for s in sources], default=0)

    if top_score < 0.20:
        return False

    trusted_hits = [
        s for s in sources
        if s.get("source") in TRUSTED_SOURCES and (s.get("score") or 0) >= 0.20
    ]

    if len(trusted_hits) < 1:
        return False

    q = question.lower()

    needs_number = any(
        word in q
        for word in ["hba1c", "dose", "dosage", "target", "mg", "mmol", "%"]
    )

    if needs_number:
        has_number = any(
            any(char.isdigit() for char in (s.get("snippet") or ""))
            for s in trusted_hits
        )

        if not has_number:
            return False

    return True