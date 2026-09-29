import streamlit as st

from app.crawler import WebCrawler
from app.exporter import DataExporter


st.set_page_config(
    page_title="Web Crawler",
    page_icon="🌐",
    layout="wide",
)


st.title("🌐 Web Crawler & Data Extraction Engine")

st.markdown(
    """
    Crawl a website, extract structured information,
    follow internal links, and export the collected data.
    """
)


with st.sidebar:

    st.header("Crawler Configuration")

    seed_url = st.text_input(
        "Seed URL",
        value="https://quotes.toscrape.com/",
    )

    max_depth = st.slider(
        "Maximum crawl depth",
        min_value=0,
        max_value=3,
        value=1,
    )

    delay = st.slider(
        "Request delay (seconds)",
        min_value=0.5,
        max_value=5.0,
        value=1.0,
        step=0.5,
    )

    keyword = st.text_input(
        "Keyword search",
    )


if st.button(
    "🚀 Start Crawl",
    type="primary",
):

    if not seed_url.startswith(
        ("http://", "https://")
    ):
        st.error(
            "Please enter a valid HTTP/HTTPS URL."
        )

    else:

        with st.spinner(
            "Crawling website..."
        ):

            crawler = WebCrawler(
                max_depth=max_depth,
                delay=delay,
            )

            crawl_data = crawler.crawl(
                [seed_url]
            )

            st.session_state[
                "crawler"
            ] = crawler

            st.session_state[
                "crawl_data"
            ] = crawl_data


if "crawl_data" in st.session_state:

    crawl_data = st.session_state[
        "crawl_data"
    ]

    stats = crawl_data[
        "statistics"
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Pages Visited",
        stats["pages_visited"],
    )

    col2.metric(
        "Failures",
        stats["failures"],
    )

    col3.metric(
        "Execution Time",
        f"{stats['execution_time_seconds']} s",
    )

    st.divider()

    st.subheader(
        "Extracted Pages"
    )

    for page in crawl_data["results"]:

        with st.expander(
            page.get(
                "title",
                "Untitled page",
            )
        ):

            st.write(
                "**URL:**",
                page["url"],
            )

            st.write(
                "**Depth:**",
                page["depth"],
            )

            st.write(
                "**Headings**"
            )

            st.write(
                page["headings"]
            )

            st.write(
                "**Paragraphs**"
            )

            st.write(
                " ".join(
                    page["paragraphs"]
                )[:2000]
            )

            st.write(
                f"**Links:** "
                f"{len(page['links'])}"
            )

            st.write(
                f"**Images:** "
                f"{len(page['images'])}"
            )

    if keyword:

        st.subheader(
            f"Keyword Results: `{keyword}`"
        )

        crawler = st.session_state[
            "crawler"
        ]

        matches = crawler.search(
            keyword
        )

        st.write(
            f"{len(matches)} matching pages found."
        )

        for match in matches:

            st.write(
                match["url"]
            )

    st.divider()

    st.subheader(
        "Export Data"
    )

    exporter = DataExporter()

    json_path = (
        "output/streamlit_crawl.json"
    )

    csv_path = (
        "output/streamlit_crawl.csv"
    )

    exporter.export_json(
        crawl_data["results"],
        __import__("pathlib").Path(
            json_path
        ),
    )

    exporter.export_csv(
        crawl_data["results"],
        __import__("pathlib").Path(
            csv_path
        ),
    )

    with open(
        json_path,
        "rb",
    ) as file:

        st.download_button(
            "Download JSON",
            file,
            file_name="crawl_results.json",
            mime="application/json",
        )

    with open(
        csv_path,
        "rb",
    ) as file:

        st.download_button(
            "Download CSV",
            file,
            file_name="crawl_results.csv",
            mime="text/csv",
        )