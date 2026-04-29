import requests
import xml.etree.ElementTree as ET


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def search_pubmed(query: str, limit: int = 5) -> list[str]:
    url = f"{BASE_URL}/esearch.fcgi"

    params = {
        "db": "pubmed",
        "term": query,
        "retmode": "json",
        "retmax": limit,
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("esearchresult", {}).get("idlist", [])


def fetch_pubmed_details(pubmed_ids: list[str]) -> list[dict]:
    if not pubmed_ids:
        return []

    url = f"{BASE_URL}/efetch.fcgi"

    params = {
        "db": "pubmed",
        "id": ",".join(pubmed_ids),
        "retmode": "xml",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    root = ET.fromstring(response.text)
    articles = []

    for article in root.findall(".//PubmedArticle"):
        pmid = article.findtext(".//PMID", default="")
        title = article.findtext(".//ArticleTitle", default="No title")

        abstract_parts = article.findall(".//AbstractText")
        abstract = " ".join(
            part.text.strip() for part in abstract_parts if part.text
        )

        if not abstract:
            continue

        articles.append({
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "source": "PubMed",
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })

    return articles


def get_pubmed_articles(query: str, limit: int = 5) -> list[dict]:
    ids = search_pubmed(query, limit)
    return fetch_pubmed_details(ids)