from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from app.config import settings

qdrant = QdrantClient(url=settings.QDRANT_URL)


def create_collection_if_not_exists():
    collections = qdrant.get_collections().collections
    existing_names = [collection.name for collection in collections]

    if settings.QDRANT_COLLECTION not in existing_names:
        qdrant.create_collection(
            collection_name=settings.QDRANT_COLLECTION,
            vectors_config=VectorParams(
                size=settings.EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )


def upsert_medical_chunk(
    point_id: str,
    vector: list[float],
    text: str,
    source: str,
    title: str,
    url: str | None = None,
    page: int | None = None,
    year: int | None = None,
):
    payload = {
        "text": text,
        "source": source,
        "title": title,
        "url": url,
        "page": page,
        "year": year,
    }

    qdrant.upsert(
        collection_name=settings.QDRANT_COLLECTION,
        points=[
            PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
        ]
    )


def search_medical_chunks(
    query_vector: list[float],
    limit: int = 5,
):
    result = qdrant.query_points(
        collection_name=settings.QDRANT_COLLECTION,
        query=query_vector,
        limit=limit,
        with_payload=True
    )

    return result.points