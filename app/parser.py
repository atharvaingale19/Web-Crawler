from typing import Any

from bs4 import BeautifulSoup


class HTMLParser:
    """Extract structured information from HTML documents."""

    def parse(self, html: str, base_url: str) -> dict[str, Any]:
        soup = BeautifulSoup(html, "html.parser")

        title = soup.title.get_text(strip=True) if soup.title else ""

        headings = [
            heading.get_text(" ", strip=True)
            for heading in soup.find_all(["h1", "h2", "h3"])
        ]

        paragraphs = [
            paragraph.get_text(" ", strip=True)
            for paragraph in soup.find_all("p")
            if paragraph.get_text(" ", strip=True)
        ]

        links = []

        for anchor in soup.find_all("a", href=True):
            links.append({
                "text": anchor.get_text(" ", strip=True),
                "url": anchor["href"]
            })

        images = []

        for image in soup.find_all("img", src=True):
            images.append({
                "alt": image.get("alt", ""),
                "src": image["src"]
            })

        metadata = {}

        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property")
            content = meta.get("content")

            if name and content:
                metadata[name] = content

        return {
            "url": base_url,
            "title": title,
            "headings": headings,
            "paragraphs": paragraphs,
            "links": links,
            "images": images,
            "metadata": metadata,
        }