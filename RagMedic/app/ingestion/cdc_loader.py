import requests
from bs4 import BeautifulSoup


def clean_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return " ".join(soup.get_text(" ").split())


def ingest_cdc_url(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    text = clean_html(response.text)

    soup = BeautifulSoup(response.text, "lxml")
    title = soup.title.string.strip() if soup.title else "CDC Page"

    return {
        "title": title,
        "text": text,
        "source": "CDC",
        "url": url,
    }