#!/usr/bin/env python3
"""Generate printable HTML card sheets from cards/card_list.csv."""
from __future__ import annotations

import csv
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
CARD_CSV = ROOT / "cards" / "card_list.csv"
OUTPUT_HTML = ROOT / "cards" / "cards_print.html"

# Mapping of card types to color accents for borders/headers.
TYPE_COLORS: Dict[str, str] = {
    "Node": "#3b82f6",
    "Control Plane": "#2563eb",
    "Storage": "#0ea5e9",
    "Networking": "#6366f1",
    "Automation": "#14b8a6",
    "Upgrade": "#0f766e",
    "Workload": "#22c55e",
    "Attack": "#ef4444",
    "Response": "#f59e0b",
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


def load_cards(csv_path: Path) -> List[Card]:
    cards: List[Card] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            base_card = Card(
                name=row.get("name", "").strip(),
                type=row.get("type", "").strip(),
                cost=row.get("cost", "").strip(),
                slo=row.get("slo", "").strip(),
                quantity=int(row.get("quantity", 1) or 1),
                prerequisite=row.get("prerequisite", "").strip(),
                effect=row.get("effect", "").strip(),
                repair_cost=row.get("repair_cost", "").strip(),
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

    head = f"""
<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\" />
<title>Kubernetes Cluster Clash — Card Fronts</title>
<style>
@page {{
    size: letter;
    margin: 0.5in;
}}
body {{
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin: 0;
    background: #f8fafc;
    color: #0f172a;
}}
main {{
    padding: 0.5in;
}}
.sheet {{
    display: grid;
    grid-template-columns: repeat(3, 2.5in);
    grid-auto-rows: 3.5in;
    gap: 0.3in;
    margin-bottom: 0.5in;
    page-break-after: always;
}}
.sheet:last-of-type {{
    page-break-after: auto;
}}
.card {{
    box-sizing: border-box;
    border: 3px solid #0f172a;
    border-radius: 0.2in;
    padding: 0.2in;
    background: white;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 0 0.08in rgba(15, 23, 42, 0.2);
}}
.card-header {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    font-weight: 700;
    text-transform: uppercase;
    font-size: 0.6rem;
}}
.card-name {{
    font-size: 0.95rem;
    text-transform: none;
    color: #0f172a;
}}
.tag {{
    padding: 0.05in 0.12in;
    border-radius: 999px;
    color: white;
    font-weight: 700;
    font-size: 0.5rem;
    letter-spacing: 0.05em;
}}
.stats {{
    display: flex;
    justify-content: flex-start;
    gap: 0.2in;
    margin: 0.1in 0;
    font-size: 0.6rem;
}}
.stat {{
    display: flex;
    flex-direction: column;
}}
.stat-label {{
    font-weight: 600;
    letter-spacing: 0.04em;
    color: #475569;
}}
.stat-value {{
    font-size: 0.8rem;
    font-weight: 700;
    color: #0f172a;
}}
.card-body {{
    flex: 1 1 auto;
    font-size: 0.62rem;
    line-height: 1.35;
    color: #1e293b;
}}
.card-body strong {{
    color: #0f172a;
}}
.card-footer {{
    font-size: 0.55rem;
    color: #475569;
}}
.meta {{
    display: flex;
    justify-content: space-between;
    font-size: 0.5rem;
    color: #475569;
}}
.placeholder {{
    border: 2px dashed #cbd5f5;
    background: #e2e8f0;
}}
{generate_type_styles()}
</style>
</head>
<body>
<main>
<header style=\"margin-bottom:0.4in;\">
  <h1 style=\"margin:0;font-size:1.1rem;text-transform:uppercase;letter-spacing:0.12em;color:#1e293b;\">Kubernetes Cluster Clash — Card Fronts</h1>
  <p style=\"margin:0.2rem 0 0;font-size:0.65rem;color:#475569;\">Total cards: {total_cards} &nbsp;•&nbsp; Sheets: {total_sheets}</p>
</header>
"""

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
    for card_type, color in TYPE_COLORS.items():
        slug = "-".join(card_type.lower().split())
        rules.append(
            f".card-type-{slug} {{ border-color: {color}; }}\n"
            f".card-type-{slug} .tag {{ background: {color}; }}"
        )
    return "\n".join(rules)


def render_card(card: Card) -> str:
    return f"""
<div class=\"card card-type-{card.slug_type}\">
  <div class=\"card-header\">
    <span class=\"tag\">{card.type}</span>
    <span class=\"card-name\">{card.name}</span>
  </div>
  <div class=\"stats\">
    <div class=\"stat\">
      <span class=\"stat-label\">Cost</span>
      <span class=\"stat-value\">{card.cost}</span>
    </div>
    <div class=\"stat\">
      <span class=\"stat-label\">SLO</span>
      <span class=\"stat-value\">{card.display_slo}</span>
    </div>
    <div class=\"stat\">
      <span class=\"stat-label\">Repair</span>
      <span class=\"stat-value\">{card.display_repair_cost}</span>
    </div>
  </div>
  <div class=\"card-body\">
    {format_prerequisite(card)}
    <p>{card.display_effect}</p>
  </div>
  <div class=\"card-footer\">
    <div class=\"meta\">
      <span>Copy {card.copy_index}/{card.quantity}</span>
      <span>Kube Cluster Clash</span>
    </div>
  </div>
</div>
"""


def format_prerequisite(card: Card) -> str:
    prereq = card.display_prerequisite
    if prereq:
        return f"<p><strong>Prerequisite:</strong> {prereq}</p>"
    return ""


def main() -> None:
    if not CARD_CSV.exists():
        raise SystemExit(f"CSV not found: {CARD_CSV}")

    cards = load_cards(CARD_CSV)
    html = render_html(cards)
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"Generated {len(cards)} cards across {math.ceil(len(cards) / 9)} sheets -> {OUTPUT_HTML}")


if __name__ == "__main__":
    main()
