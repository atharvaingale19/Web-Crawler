import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse


def setup_logging(log_directory: Path) -> None:
    """Configure file and console logging."""

    log_directory.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(
                log_directory / "crawler.log",
                encoding="utf-8"
            ),
            logging.StreamHandler(),
        ],
    )


def normalize_url(url: str) -> str:
    """Normalize a URL for duplicate detection."""

    parsed = urlparse(url)

    normalized = parsed._replace(
        fragment="",
    )

    return normalized.geturl().rstrip("/")


def is_http_url(url: str) -> bool:
    """Return True for HTTP/HTTPS URLs."""

    return urlparse(url).scheme in {"http", "https"}


def is_internal_url(url: str, base_domain: str) -> bool:
    """Check whether a URL belongs to the same domain."""

    return urlparse(url).netloc == base_domain


def make_absolute_url(base_url: str, link: str) -> str:
    """Convert a relative URL into an absolute URL."""

    return urljoin(base_url, link)