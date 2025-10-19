#!/usr/bin/env python3
"""Generate printable HTML card sheets from cards/card_list.csv."""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parent.parent
CARD_CSV = ROOT / "cards" / "card_list.csv"
OUTPUT_HTML = ROOT / "cards" / "cards_print.html"

# Основные цвета и мягкие оттенки для разных типов карт.
TYPE_COLORS: Dict[str, Dict[str, str]] = {
    "Нода": {"accent": "#1d4ed8", "soft": "#dbeafe"},
    "Контрольный план": {"accent": "#1e3a8a", "soft": "#e0e7ff"},
    "Хранилище": {"accent": "#0ea5e9", "soft": "#cffafe"},
    "Сеть": {"accent": "#6366f1", "soft": "#e0e7ff"},
    "Автоматизация": {"accent": "#14b8a6", "soft": "#ccfbf1"},
    "Улучшение": {"accent": "#0f766e", "soft": "#d1fae5"},
    "Нагрузка": {"accent": "#22c55e", "soft": "#dcfce7"},
    "Атака": {"accent": "#ef4444", "soft": "#fee2e2"},
    "Ответ": {"accent": "#f59e0b", "soft": "#fef3c7"},
}

FIELD_ALIASES: Dict[str, Iterable[str]] = {
    "name": ("name", "название"),
    "type": ("type", "тип"),
    "cost": ("cost", "стоимость"),
    "slo": ("slo", "slo"),
    "quantity": ("quantity", "количество"),
    "prerequisite": ("prerequisite", "требование"),
    "effect": ("effect", "эффект"),
    "repair_cost": ("repair_cost", "стоимость_ремонта"),
}


@dataclass
class Card:
    name: str
    type: str
    cost: str
    slo: str
    quantity: int
    prerequisite: str
    effect: str
    repair_cost: str

    copy_index: int = 1  # which physical copy of this card (1-based)

    @property
    def slug_type(self) -> str:
        return "-".join(self.type.lower().split())

    @property
    def display_prerequisite(self) -> str:
        return self.prerequisite.strip()

    @property
    def display_effect(self) -> str:
        return self.effect.strip()

    @property
    def display_repair_cost(self) -> str:
        text = self.repair_cost.strip()
        return text if text else "-"

    @property
    def display_slo(self) -> str:
        try:
            value = int(float(self.slo))
        except ValueError:
            return self.slo
        return str(value) if value > 0 else "—"


def read_field(row: Dict[str, str], key: str) -> str:
    for alias in FIELD_ALIASES.get(key, (key,)):
        if alias in row and row[alias] is not None:
            value = str(row[alias]).strip()
            if value:
                return value
    return ""


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def load_cards(csv_path: Path) -> List[Card]:
    cards: List[Card] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            base_card = Card(
                name=read_field(row, "name"),
                type=read_field(row, "type"),
                cost=read_field(row, "cost"),
                slo=read_field(row, "slo"),
                quantity=parse_int(read_field(row, "quantity"), default=1),
                prerequisite=read_field(row, "prerequisite"),
                effect=read_field(row, "effect"),
                repair_cost=read_field(row, "repair_cost"),
            )
            for copy_index in range(1, base_card.quantity + 1):
                cards.append(
                    Card(
                        name=base_card.name,
                        type=base_card.type,
                        cost=base_card.cost,
                        slo=base_card.slo,
                        quantity=base_card.quantity,
                        prerequisite=base_card.prerequisite,
                        effect=base_card.effect,
                        repair_cost=base_card.repair_cost,
                        copy_index=copy_index,
                    )
                )
    return cards


def render_html(cards: List[Card]) -> str:
    total_cards = len(cards)
    cards_per_sheet = 9
    total_sheets = max(1, math.ceil(total_cards / cards_per_sheet))

    head_template = Template(
        """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<title>Kubernetes Cluster Clash — Листы карточек</title>
<style>
@page {
    size: letter;
    margin: 0.5in;
}
body {
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin: 0;
    background: radial-gradient(circle at top, #e0f2fe 0%, #f8fafc 60%);
    color: #0f172a;
}
main {
    padding: 0.5in;
}
.sheet {
    display: grid;
    grid-template-columns: repeat(3, 2.5in);
    grid-auto-rows: 3.5in;
    gap: 0.3in;
    margin-bottom: 0.6in;
    page-break-after: always;
}
.sheet:last-of-type {
    page-break-after: auto;
}
.card {
    position: relative;
    box-sizing: border-box;
    border: 3px solid var(--accent, #0f172a);
    border-radius: 0.25in;
    padding: 0.22in;
    background: linear-gradient(135deg, var(--accent-soft, #e2e8f0) 0%, #ffffff 70%);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 0.12in 0.35in rgba(15, 23, 42, 0.28);
    overflow: hidden;
}
.card::after {
    content: '';
    position: absolute;
    inset: 0.15in;
    border-radius: 0.18in;
    border: 1px dashed rgba(15, 23, 42, 0.08);
    pointer-events: none;
}
.card-top {
    position: relative;
    display: flex;
    justify-content: space-between;
    align-items: center;
    z-index: 1;
}
.card-name {
    position: relative;
    z-index: 1;
    margin: 0.12in 0 0.08in;
    font-size: 1.05rem;
    line-height: 1.1;
    color: #0f172a;
    text-transform: none;
}
.tag {
    padding: 0.05in 0.16in;
    border-radius: 999px;
    color: #ffffff;
    font-weight: 700;
    font-size: 0.55rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}
.cost-badge {
    padding: 0.04in 0.16in;
    border-radius: 999px;
    color: #ffffff;
    font-weight: 700;
    font-size: 0.6rem;
    letter-spacing: 0.03em;
    display: inline-flex;
    align-items: center;
    gap: 0.08in;
}
.stat-row {
    display: flex;
    gap: 0.15in;
    margin: 0 0 0.12in;
    z-index: 1;
}
.chip {
    background: rgba(15, 23, 42, 0.05);
    border: 1px solid rgba(15, 23, 42, 0.12);
    border-radius: 0.16in;
    padding: 0.04in 0.16in;
    font-size: 0.62rem;
    display: flex;
    gap: 0.1in;
    align-items: baseline;
}
.chip-label {
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: rgba(15, 23, 42, 0.7);
}
.chip-value {
    font-weight: 700;
    color: #0f172a;
}
.card-body {
    position: relative;
    z-index: 1;
    flex: 1 1 auto;
    font-size: 0.68rem;
    line-height: 1.4;
    color: #1e293b;
    background: rgba(255, 255, 255, 0.65);
    border-radius: 0.18in;
    padding: 0.14in 0.18in;
    box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.07);
}
.card-body p {
    margin: 0 0 0.12in;
}
.card-body p:last-child {
    margin-bottom: 0;
}
.prereq strong {
    color: #0f172a;
}
.card-footer {
    position: relative;
    z-index: 1;
    margin-top: 0.12in;
    font-size: 0.58rem;
    color: rgba(15, 23, 42, 0.7);
    display: flex;
    justify-content: space-between;
}
.placeholder {
    border: 2px dashed #cbd5f5;
    background: #e2e8f0;
    border-radius: 0.2in;
}
$styles
</style>
</head>
<body>
<main>
<header style="margin-bottom:0.45in;">
  <h1 style="margin:0;font-size:1.15rem;letter-spacing:0.1em;text-transform:uppercase;color:#1e293b;">Kubernetes Cluster Clash — Листы карточек</h1>
  <p style="margin:0.2rem 0 0;font-size:0.65rem;color:#475569;">Всего карт: $total_cards &nbsp;•&nbsp; Листов: $total_sheets</p>
</header>
"""
    )

    head = head_template.substitute(
        styles=generate_type_styles(), total_cards=total_cards, total_sheets=total_sheets
    )

    body_parts: List[str] = []
    for sheet_index in range(total_sheets):
        start = sheet_index * cards_per_sheet
        end = start + cards_per_sheet
        sheet_cards = cards[start:end]
        body_parts.append("<section class=\"sheet\">")
        for card in sheet_cards:
            body_parts.append(render_card(card))
        if len(sheet_cards) < cards_per_sheet:
            placeholders = cards_per_sheet - len(sheet_cards)
            body_parts.extend("<div class=\"card placeholder\"></div>" for _ in range(placeholders))
        body_parts.append("</section>")

    tail = """
</main>
</body>
</html>
"""

    return head + "\n".join(body_parts) + tail


def generate_type_styles() -> str:
    rules = []
    for card_type, palette in TYPE_COLORS.items():
        slug = "-".join(card_type.lower().split())
        accent = palette["accent"]
        soft = palette["soft"]
        rules.append(
            f".card-type-{slug} {{ --accent: {accent}; --accent-soft: {soft}; border-color: {accent}; }}\n"
            f".card-type-{slug} .tag {{ background: {accent}; box-shadow: 0 0.04in 0.12in rgba(15,23,42,0.18); }}\n"
            f".card-type-{slug} .cost-badge {{ background: {accent}; box-shadow: 0 0.04in 0.12in rgba(15,23,42,0.18); }}\n"
            f".card-type-{slug} .chip {{ border-color: rgba(15, 23, 42, 0.08); box-shadow: inset 0 0 0 1px rgba(255,255,255,0.4); background: linear-gradient(135deg, rgba(255,255,255,0.85) 0%, {soft} 100%); }}"
        )
    return "\n".join(rules)


def render_card(card: Card) -> str:
    return f"""
<div class=\"card card-type-{card.slug_type}\">
  <div class=\"card-top\">
    <span class=\"tag\">{card.type}</span>
    <span class=\"cost-badge\">⚙ {card.cost}</span>
  </div>
  <h2 class=\"card-name\">{card.name}</h2>
  <div class=\"stat-row\">
    <div class=\"chip\">
      <span class=\"chip-label\">SLO</span>
      <span class=\"chip-value\">{card.display_slo}</span>
    </div>
    <div class=\"chip\">
      <span class=\"chip-label\">Ремонт</span>
      <span class=\"chip-value\">{card.display_repair_cost}</span>
    </div>
  </div>
  <div class=\"card-body\">
    {format_prerequisite(card)}
    <p>{card.display_effect}</p>
  </div>
  <div class=\"card-footer\">
      <span>Копия {card.copy_index}/{card.quantity}</span>
      <span>Kubernetes Cluster Clash</span>
  </div>
</div>
"""


def format_prerequisite(card: Card) -> str:
    prereq = card.display_prerequisite
    if prereq:
        return f"<p class=\"prereq\"><strong>Требование:</strong> {prereq}</p>"
    return ""


def main() -> None:
    if not CARD_CSV.exists():
        raise SystemExit(f"CSV not found: {CARD_CSV}")

    cards = load_cards(CARD_CSV)
    html = render_html(cards)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(
        f"Сгенерировано {len(cards)} карт на {math.ceil(len(cards) / 9)} листах → {OUTPUT_HTML}"
    )


if __name__ == "__main__":
    main()
