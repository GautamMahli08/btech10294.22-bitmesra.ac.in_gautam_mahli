import requests
from bs4 import BeautifulSoup


def ingest_nice_url(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    blocks = soup.find_all(["h1", "h2", "h3", "p", "li"])

    texts = []
    for tag in blocks:
        text = tag.get_text(" ", strip=True)
        if len(text) > 20:
            texts.append(text)

    cleaned_text = "\n".join(texts)

    print("NICE EXTRACT PREVIEW:")
    print(cleaned_text[:3000])

    title = soup.title.string.strip() if soup.title else "NICE Guideline"

    return {
        "title": title,
        "text": cleaned_text,
        "source": "NICE",
        "url": url,
    }