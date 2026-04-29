import uuid
from app.ingestion.who_loader import ingest_who_url
from app.ingestion.chunker import chunk_text
from app.ingestion.pubmed_loader import get_pubmed_articles
from app.ingestion.cdc_loader import ingest_cdc_url
from app.rag.embeddings import create_embedding
from app.rag.qdrant_store import upsert_medical_chunk
from app.ingestion.nice_loader import ingest_nice_url

def store_articles_in_qdrant(articles: list[dict]) -> dict:
    total_chunks = 0

    for article in articles:
        full_text = article.get("text") or article.get("abstract") or ""

        if not full_text.strip():
            continue

        chunks = chunk_text(full_text, chunk_size=300, overlap=50)

        for chunk in chunks:
            vector = create_embedding(chunk)

            upsert_medical_chunk(
                point_id=str(uuid.uuid4()),
                vector=vector,
                text=chunk,
                source=article.get("source", "Unknown"),
                title=article.get("title", "Untitled"),
                url=article.get("url"),
                page=None,
                year=None,
            )

            total_chunks += 1

    return {
        "articles_found": len(articles),
        "chunks_stored": total_chunks,
    }


def ingest_pubmed_query(query: str, limit: int = 5) -> dict:
    articles = get_pubmed_articles(query=query, limit=limit)

    normalized_articles = []

    for article in articles:
        normalized_articles.append({
            "title": article["title"],
            "text": article["abstract"],
            "source": "PubMed",
            "url": article["url"],
        })

    result = store_articles_in_qdrant(normalized_articles)

    return {
        "source": "PubMed",
        "query": query,
        **result,
    }


def ingest_cdc_page(url: str) -> dict:
    article = ingest_cdc_url(url)

    result = store_articles_in_qdrant([article])

    return {
        "source": "CDC",
        "url": url,
        **result,
    }

def ingest_who_page(url: str) -> dict:
    article = ingest_who_url(url)

    result = store_articles_in_qdrant([article])

    return {
        "source": "WHO",
        "url": url,
        **result,
    }

def ingest_nice_page(url: str) -> dict:
    article = ingest_nice_url(url)

    result = store_articles_in_qdrant([article])

    return {
        "source": "NICE",
        "url": url,
        **result,
    }