from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


START_URL = "https://www.comune.codroipo.ud.it/it/servizi"
_BACKEND_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = _BACKEND_ROOT / "app" / "data"
OUTPUT_FILE = DATA_DIR / "servizi_comunali_hardcoded.json"

LABEL_PATTERNS = {
    "required_documents": ["cosa serve", "documenti necessari", "documentazione", "requisiti"],
    "opening_hours": ["tempi e scadenze", "orari", "quando"],
    "location": ["contatti", "dove", "indirizzo", "sede"],
}

SECTION_HEADERS = {
    "A chi è rivolto",
    "Descrizione",
    "Come fare",
    "Cosa serve",
    "Cosa si ottiene",
    "Quanto Costa",
    "Tempi e scadenze",
    "Accedi al servizio",
    "Ulteriori informazioni",
    "Condizioni di servizio",
    "Contatti",
    "Contenuto",
    "Contenuto del sito",
    "Home",
    "Servizi",
    "INDICE DELLA PAGINA",
    "ESPANDI",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_lines(text: str) -> list[str]:
    return [normalize_text(line) for line in text.splitlines() if normalize_text(line)]


def extract_title(page_title: str) -> str:
    if " - " in page_title:
        return normalize_text(page_title.split(" - ", 1)[0])
    return normalize_text(page_title)


def section_text(lines: list[str], heading: str) -> str:
    try:
        start = lines.index(heading)
    except ValueError:
        return ""

    chunks: list[str] = []
    for line in lines[start + 1 :]:
        if line in SECTION_HEADERS:
            break
        chunks.append(line)
    return normalize_text(" ".join(chunks))


def section_items(lines: list[str], heading: str) -> list[str]:
    try:
        start = lines.index(heading)
    except ValueError:
        return []

    items: list[str] = []
    for line in lines[start + 1 :]:
        if line in SECTION_HEADERS:
            break
        if line and line not in {"Nessun requisito richiesto", "Nessun requisito richiesto."}:
            items.append(line)
    return items


def breadcrumb_category(lines: list[str]) -> str:
    for line in lines:
        if line.startswith("Home/Servizi/"):
            parts = [part.strip() for part in line.split("/") if part.strip()]
            if len(parts) >= 3:
                return parts[2]
    return ""


def collect_service_urls(page) -> list[str]:
    urls = page.eval_on_selector_all(
        'a[href*="/it/servizi-224003/"]',
        "(els) => Array.from(new Set(els.map(a => a.href).filter(Boolean)))",
    )
    return [
        url
        for url in urls
        if url.startswith("http") and urlparse(url).netloc == "www.comune.codroipo.ud.it" and "/it/servizi-224003/" in url
    ]


def collect_service_links(page, start_url: str, max_pages: int) -> list[str]:
    discovered: list[str] = []
    visited: set[str] = set()
    queue: list[str] = [start_url]

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        page.goto(url, wait_until="networkidle", timeout=120000)
        for service_url in collect_service_urls(page):
            if service_url not in discovered:
                discovered.append(service_url)

        if len(discovered) >= max_pages:
            break

        # Crawl only the service sections and categories that keep the /it/servizi path.
        more_urls = page.eval_on_selector_all(
            'a[href^="https://www.comune.codroipo.ud.it/it/servizi"]',
            "(els) => Array.from(new Set(els.map(a => a.href).filter(Boolean)))",
        )
        for link in more_urls:
            if (
                link.startswith("http")
                and urlparse(link).netloc == "www.comune.codroipo.ud.it"
                and "/it/servizi" in link
                and link not in visited
                and link not in queue
            ):
                queue.append(link)

    return discovered


def scrape_service(page, url: str) -> dict[str, Any]:
    page.goto(url, wait_until="networkidle", timeout=120000)
    body_text = page.locator("body").inner_text(timeout=120000)
    lines = normalize_lines(body_text)

    title = extract_title(page.title())
    description = section_text(lines, "Descrizione")
    required_documents = section_items(lines, "Cosa serve")
    opening_hours = section_text(lines, "Tempi e scadenze")
    location = section_text(lines, "Contatti")
    category = breadcrumb_category(lines)

    if not required_documents and description:
        required_documents = []

    return {
        "title": title,
        "office": category,
        "description": description,
        "required_documents": required_documents,
        "opening_hours": opening_hours,
        "location": location,
        "source_url": url,
        "breadcrumbs": [line for line in lines if line.startswith("Home/")],
        "category": category,
    }


def crawl_services(start_url: str, max_pages: int) -> list[dict[str, Any]]:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1800})
        try:
            page.goto(start_url, wait_until="networkidle", timeout=120000)
            service_urls = collect_service_links(page, start_url, max_pages)

            services: list[dict[str, Any]] = []
            for url in service_urls[:max_pages]:
                try:
                    services.append(scrape_service(page, url))
                except PlaywrightTimeoutError as exc:
                    print(f"[warn] Skipping {url}: {exc}")

            services.sort(key=lambda item: item["title"].lower())
            return services
        finally:
            browser.close()


def write_output(services: list[dict[str, Any]], output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "source": START_URL,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
        "count": len(services),
        "services": services,
    }
    output_file.write_text(json.dumps(payload["services"], ensure_ascii=False, indent=2), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape Codroipo municipal services and save a JSON dataset for the RAG prototype."
    )
    parser.add_argument("--url", default=START_URL, help="Starting URL to crawl")
    parser.add_argument("--output", default=str(OUTPUT_FILE), help="Output JSON file path")
    parser.add_argument("--max-pages", type=int, default=120, help="Maximum number of pages to visit")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    services = crawl_services(args.url, args.max_pages)
    output_file = Path(args.output)
    write_output(services, output_file)
    print(f"Saved {len(services)} services to {output_file}")


if __name__ == "__main__":
    main()
