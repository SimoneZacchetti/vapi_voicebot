from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


HARDCODED_DATA_FILE = Path(__file__).resolve().parent / "data" / "servizi_comunali_hardcoded.json"


def _data_file() -> Path:
    """Use hardcoded municipal services JSON directly."""
    return HARDCODED_DATA_FILE


def load_services() -> list[dict[str, Any]]:
    with _data_file().open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def search_services(query: str = "", limit: int = 3) -> list[dict[str, Any]]:
    query_tokens = _normalize(query)

    services = load_services()

    if not query_tokens:
        return services[:limit]

    scored_services: list[tuple[int, dict[str, Any]]] = []

    for service in services:
        searchable_text = " ".join(
            [
                str(service.get("title", "")),
                str(service.get("office", "")),
                str(service.get("description", "")),
                str(service.get("opening_hours", "")),
                str(service.get("location", "")),
                " ".join(service.get("required_documents", [])),
            ]
        )
        searchable_tokens = set(_normalize(searchable_text))
        score = sum(1 for token in query_tokens if token in searchable_tokens)

        if score > 0:
            scored_services.append((score, service))

    scored_services.sort(key=lambda item: (-item[0], item[1].get("title", "")))
    return [service for _, service in scored_services[:limit]]
