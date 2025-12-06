from typing import Any

import requests

from .mock_data import get_mock_machine_live, get_mock_machines

USE_BACKEND = False  # Change to True when backend is ready
API_BASE = "http://localhost:8000"


def get_all_machines() -> list[dict[str, Any]]:
    if USE_BACKEND:
        return requests.get(f"{API_BASE}/machines", timeout=10).json()
    return get_mock_machines()


def get_machine_live(machine_id: str) -> dict[str, Any]:
    if USE_BACKEND:
        return requests.get(f"{API_BASE}/machine/{machine_id}/live", timeout=10).json()
    return get_mock_machine_live(machine_id)
