from app.ingestion.website_ingestor import (
    ingest_pubmed_query,
    ingest_cdc_page,
    ingest_who_page,
    ingest_nice_page,
)

from app.ingestion.seed_data import (
    seed_diabetes_hba1c_guideline,
    seed_metformin_dose_guideline,
)


TOPIC_SOURCE_MAP = {
    "diabetes": {
        "cdc": [
            "https://www.cdc.gov/diabetes/about/about-type-2-diabetes.html",
        ],
        "who": [
            "https://www.who.int/news-room/fact-sheets/detail/diabetes",
        ],
        "nice": [
            "https://www.nice.org.uk/guidance/ng28/chapter/Recommendations",
        ],
    },
    "covid": {
        "cdc": [
            "https://www.cdc.gov/covid/signs-symptoms/index.html",
        ],
        "who": [
            "https://www.who.int/health-topics/coronavirus",
        ],
        "nice": [],
    },
    "hypertension": {
        "cdc": [
            "https://www.cdc.gov/high-blood-pressure/about/index.html",
        ],
        "who": [
            "https://www.who.int/news-room/fact-sheets/detail/hypertension",
        ],
        "nice": [
            "https://www.nice.org.uk/guidance/ng136/chapter/Recommendations",
        ],
    },
    "obesity": {
        "cdc": [
            "https://www.cdc.gov/obesity/index.html",
        ],
        "who": [
            "https://www.who.int/news-room/fact-sheets/detail/obesity-and-overweight",
        ],
        "nice": [
            "https://www.nice.org.uk/guidance/cg189/chapter/Recommendations",
        ],
    },
}


def detect_topic(query: str) -> str | None:
    q = query.lower()

    if "covid" in q or "coronavirus" in q:
        return "covid"

    if "diabetes" in q or "hba1c" in q or "metformin" in q:
        return "diabetes"

    if "hypertension" in q or "blood pressure" in q:
        return "hypertension"

    if "obesity" in q or "overweight" in q:
        return "obesity"

    return None


def safe_call(func, *args):
    try:
        return func(*args)
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
        }


def auto_ingest_for_query(query: str) -> dict:
    q = query.lower()

    result = {
        "query": query,
        "topic": None,
        "pubmed": None,
        "cdc": [],
        "who": [],
        "nice": [],
        "nice_seed": None,
        "metformin_seed": None,
    }

    # Always try PubMed for unknown/current medical queries
    result["pubmed"] = safe_call(ingest_pubmed_query, query, 5)

    topic = detect_topic(query)
    result["topic"] = topic

    if not topic:
        return result

    urls = TOPIC_SOURCE_MAP.get(topic, {})

    for url in urls.get("cdc", []):
        result["cdc"].append(safe_call(ingest_cdc_page, url))

    for url in urls.get("who", []):
        result["who"].append(safe_call(ingest_who_page, url))

    for url in urls.get("nice", []):
        result["nice"].append(safe_call(ingest_nice_page, url))

    # Targeted fallback seed for HbA1c numeric guideline values
    if topic == "diabetes" and ("hba1c" in q or "target" in q):
        result["nice_seed"] = safe_call(seed_diabetes_hba1c_guideline)

    # Targeted fallback seed for metformin starting dose
    if topic == "diabetes" and "metformin" in q and any(
        word in q for word in ["dose", "dosage", "starting", "start"]
    ):
        result["metformin_seed"] = safe_call(seed_metformin_dose_guideline)

    return result