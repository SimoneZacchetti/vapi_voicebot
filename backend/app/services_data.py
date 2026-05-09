from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DATA_FILE = Path(__file__).resolve().parent / "data" / "servizi_comunali.json"


def load_services() -> list[dict[str, Any]]:
    with DATA_FILE.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _normalize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def search_services(query: str, limit: int = 3) -> list[dict[str, Any]]:
    query_tokens = _normalize(query)
    if not query_tokens:
        return []

    services = load_services()
    scored_services: list[tuple[int, dict[str, Any]]] = []

    for service in services:
        searchable_text = " ".join(
            [
                str(service.get("title", "")),
                str(service.get("office", "")),
                str(service.get("description", "")),
                " ".join(service.get("required_documents", [])),
            ]
        )
        searchable_tokens = set(_normalize(searchable_text))
        score = sum(1 for token in query_tokens if token in searchable_tokens)

        if score > 0:
            scored_services.append((score, service))

    scored_services.sort(key=lambda item: (-item[0], item[1].get("title", "")))
    return [service for _, service in scored_services[:limit]]
