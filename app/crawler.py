import logging
import time
from collections import deque
from time import perf_counter
from typing import Any
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import (
    DEFAULT_DELAY,
    DEFAULT_DEPTH,
    MAX_RETRIES,
    REQUEST_TIMEOUT,
    USER_AGENT,
)
from .parser import HTMLParser
from .utils import (
    is_http_url,
    is_internal_url,
    make_absolute_url,
    normalize_url,
)


logger = logging.getLogger(__name__)


class WebCrawler:
    """Recursive internal web crawler with robots.txt support."""

    def __init__(
        self,
        max_depth: int = DEFAULT_DEPTH,
        delay: float = DEFAULT_DELAY,
        timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ) -> None:

        self.max_depth = max_depth
        self.delay = delay
        self.timeout = timeout

        self.parser = HTMLParser()

        self.visited: set[str] = set()
        self.results: list[dict[str, Any]] = []

        self.failed_urls: list[str] = []

        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy
        )

        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        self.session.headers.update({
            "User-Agent": USER_AGENT
        })

    def _robots_allowed(self, url: str) -> bool:
        """Check robots.txt before fetching a URL."""

        parsed = urlparse(url)

        robots_url = (
            f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        )

        parser = RobotFileParser()
        parser.set_url(robots_url)

        try:
            parser.read()

            allowed = parser.can_fetch(
                USER_AGENT,
                url,
            )

            if not allowed:
                logger.warning(
                    "Blocked by robots.txt: %s",
                    url,
                )

            return allowed

        except Exception as exc:
            logger.warning(
                "Could not read robots.txt for %s: %s",
                parsed.netloc,
                exc,
            )

            return True

    def _fetch(self, url: str) -> str | None:
        """Download HTML content."""

        try:
            response = self.session.get(
                url,
                timeout=self.timeout,
            )

            response.raise_for_status()

            content_type = response.headers.get(
                "Content-Type",
                "",
            )

            if "text/html" not in content_type.lower():
                logger.info(
                    "Skipping non-HTML resource: %s",
                    url,
                )
                return None

            return response.text

        except requests.RequestException as exc:
            logger.error(
                "Request failed for %s: %s",
                url,
                exc,
            )

            self.failed_urls.append(url)

            return None

    def crawl(self, seed_urls: list[str]) -> dict[str, Any]:
        """Crawl internal pages starting from seed URLs."""

        start_time = perf_counter()

        queue = deque(
            (normalize_url(url), 0)
            for url in seed_urls
            if is_http_url(url)
        )

        while queue:

            current_url, depth = queue.popleft()

            if current_url in self.visited:
                continue

            if depth > self.max_depth:
                continue

            self.visited.add(current_url)

            logger.info(
                "Crawling depth=%s: %s",
                depth,
                current_url,
            )

            if not self._robots_allowed(current_url):
                continue

            html = self._fetch(current_url)

            if html is None:
                continue

            data = self.parser.parse(
                html,
                current_url,
            )

            data["depth"] = depth

            self.results.append(data)

            base_domain = urlparse(
                current_url
            ).netloc

            if depth < self.max_depth:

                for link_data in data["links"]:

                    absolute_url = make_absolute_url(
                        current_url,
                        link_data["url"],
                    )

                    absolute_url = normalize_url(
                        absolute_url
                    )

                    if not is_http_url(absolute_url):
                        continue

                    if not is_internal_url(
                        absolute_url,
                        base_domain,
                    ):
                        continue

                    if absolute_url not in self.visited:
                        queue.append(
                            (
                                absolute_url,
                                depth + 1,
                            )
                        )

            time.sleep(self.delay)

        execution_time = perf_counter() - start_time

        return {
            "results": self.results,
            "statistics": {
                "pages_visited": len(self.results),
                "failures": len(self.failed_urls),
                "execution_time_seconds": round(
                    execution_time,
                    2,
                ),
            },
        }

    def search(
        self,
        keyword: str,
    ) -> list[dict[str, Any]]:
        """Search collected content for a keyword."""

        keyword = keyword.lower()

        matches = []

        for page in self.results:

            searchable_text = " ".join([
                page.get("title", ""),
                *page.get("headings", []),
                *page.get("paragraphs", []),
            ]).lower()

            if keyword in searchable_text:
                matches.append(page)

        return matches