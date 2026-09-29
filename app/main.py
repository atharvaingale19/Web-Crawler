import logging

from .config import LOG_DIR, OUTPUT_DIR
from .crawler import WebCrawler
from .exporter import DataExporter
from .utils import setup_logging


def main() -> None:

    setup_logging(LOG_DIR)

    logger = logging.getLogger(__name__)

    print("=" * 60)
    print("WEB CRAWLER & DATA EXTRACTION ENGINE")
    print("=" * 60)

    seed = input(
        "Enter seed URL: "
    ).strip()

    depth = int(
        input(
            "Maximum crawl depth [2]: "
        ) or "2"
    )

    delay = float(
        input(
            "Delay between requests [1.0]: "
        ) or "1.0"
    )

    crawler = WebCrawler(
        max_depth=depth,
        delay=delay,
    )

    try:
        crawl_data = crawler.crawl([seed])

        exporter = DataExporter()

        exporter.export_json(
            crawl_data["results"],
            OUTPUT_DIR / "crawl_results.json",
        )

        exporter.export_csv(
            crawl_data["results"],
            OUTPUT_DIR / "crawl_results.csv",
        )

        print("\nCrawl completed.")
        print(
            f"Pages visited: "
            f"{crawl_data['statistics']['pages_visited']}"
        )

        print(
            f"Failures: "
            f"{crawl_data['statistics']['failures']}"
        )

        print(
            f"Execution time: "
            f"{crawl_data['statistics']['execution_time_seconds']} seconds"
        )

        print("\nFiles created:")
        print("output/crawl_results.json")
        print("output/crawl_results.csv")

        logger.info("Crawl completed successfully.")

    except Exception as exc:

        logger.exception(
            "Crawler execution failed: %s",
            exc,
        )

        print(
            f"\nCrawler failed: {exc}"
        )


if __name__ == "__main__":
    main()