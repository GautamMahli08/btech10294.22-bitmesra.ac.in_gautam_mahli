import uuid

from app.rag.embeddings import create_embedding
from app.rag.qdrant_store import upsert_medical_chunk


def seed_diabetes_hba1c_guideline():
    text = """
    For adults with type 2 diabetes managed either by lifestyle and diet, or by lifestyle and diet combined with a single drug not associated with hypoglycaemia, support the person to aim for an HbA1c level of 48 mmol/mol (6.5%).

    For adults with type 2 diabetes on a drug associated with hypoglycaemia, support the person to aim for an HbA1c level of 53 mmol/mol (7.0%).

    HbA1c targets should be individualised based on patient factors, comorbidities, risk of hypoglycaemia, and clinical judgement.
    """

    vector = create_embedding(text)

    upsert_medical_chunk(
        point_id=str(uuid.uuid4()),
        vector=vector,
        text=text,
        source="NICE",
        title="NICE NG28 Type 2 Diabetes HbA1c Targets",
        url="https://www.nice.org.uk/guidance/ng28/chapter/Recommendations",
        page=None,
        year=2025,
    )

    return {
        "source": "NICE",
        "message": "HbA1c guideline seed stored",
    }

def seed_metformin_dose_guideline():
    import uuid
    from app.rag.embeddings import create_embedding
    from app.rag.qdrant_store import upsert_medical_chunk

    text = """
    Metformin is commonly started at 500 mg once daily with food or 500 mg twice daily with meals.
    The dose may be increased gradually based on tolerance and glycaemic response.
    Gastrointestinal side effects are common, so gradual titration is recommended.
    Renal function should be checked before and during treatment.
    """

    vector = create_embedding(text)

    upsert_medical_chunk(
        point_id=str(uuid.uuid4()),
        vector=vector,
        text=text,
        source="Drug Reference",
        title="Metformin Starting Dose Reference",
        url="Local seed data for MVP demo",
        page=None,
        year=2026,
    )

    return {
        "source": "Drug Reference",
        "message": "Metformin dose seed stored",
    }