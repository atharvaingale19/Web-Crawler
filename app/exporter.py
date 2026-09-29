import csv
import json
from pathlib import Path
from typing import Any


class DataExporter:
    """Export crawl results to JSON and CSV."""

    def export_json(
        self,
        data: list[dict[str, Any]],
        output_path: Path,
    ) -> None:
        with output_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def export_csv(
        self,
        data: list[dict[str, Any]],
        output_path: Path,
    ) -> None:

        rows = []

        for item in data:
            rows.append({
                "url": item.get("url", ""),
                "title": item.get("title", ""),
                "headings": " | ".join(item.get("headings", [])),
                "paragraphs": " ".join(item.get("paragraphs", [])),
                "link_count": len(item.get("links", [])),
                "image_count": len(item.get("images", [])),
            })

        fieldnames = [
            "url",
            "title",
            "headings",
            "paragraphs",
            "link_count",
            "image_count",
        ]

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
            )

            writer.writeheader()
            writer.writerows(rows)