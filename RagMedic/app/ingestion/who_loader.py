import requests
from bs4 import BeautifulSoup


def clean_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "lxml")

    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return " ".join(soup.get_text(" ").split())


def ingest_who_url(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    title = soup.title.string.strip() if soup.title else "WHO Page"

    text = clean_html(response.text)

    return {
        "title": title,
        "text": text,
        "source": "WHO",
        "url": url,
    }