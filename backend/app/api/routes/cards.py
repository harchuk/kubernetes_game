from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Literal

from fastapi import APIRouter

router = APIRouter(prefix="/cards", tags=["cards"])

BASE_DIR = Path(__file__).resolve().parents[4] / "cards"
CARD_DATA_PATH = BASE_DIR / "data" / "cards_en.json"
JUNIOR_CSV_PATH = BASE_DIR / "card_list_junior.csv"


@router.get("/")
def list_cards(mode: Literal["classic", "junior"] = "classic") -> dict:
    if mode == "junior" and JUNIOR_CSV_PATH.exists():
        return {"mode": mode, "cards": _load_junior_cards()}
    data = _load_classic_cards()
    return {"mode": mode, "cards": data.get("cards", [])}


def _load_classic_cards() -> dict:
    with CARD_DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _load_junior_cards() -> list[dict]:
    with JUNIOR_CSV_PATH.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        cards: list[dict] = []
        for row in reader:
            cards.append({
                "name": row.get("name"),
                "type": row.get("type"),
                "stars": int(row.get("stars") or 0),
                "cost": int(row.get("cost") or 0),
                "action": row.get("action"),
            })
        return cards
