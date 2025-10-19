#!/usr/bin/env python3
"""Generate printable card fronts and backs from cards/card_list.csv."""
from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from pathlib import Path
from string import Template
from typing import Dict, Iterable, List

ROOT = Path(__file__).resolve().parent.parent
CARD_CSV = ROOT / "cards" / "card_list.csv"
FRONT_HTML = ROOT / "cards" / "cards_print.html"
BACK_HTML = ROOT / "cards" / "cards_back.html"
CARDS_PER_SHEET = 9

TYPE_COLORS: Dict[str, Dict[str, str]] = {
    "Node": {"accent": "#1d4ed8", "soft": "#e0edff"},
    "Control Plane": {"accent": "#1e3a8a", "soft": "#e5e9ff"},
    "Storage": {"accent": "#0ea5e9", "soft": "#def5ff"},
    "Networking": {"accent": "#6366f1", "soft": "#e5e7ff"},
    "Automation": {"accent": "#14b8a6", "soft": "#d7fcf2"},
    "Upgrade": {"accent": "#0f766e", "soft": "#d6f7ef"},
    "Workload": {"accent": "#22c55e", "soft": "#e4fbe9"},
    "Attack": {"accent": "#ef4444", "soft": "#ffe2e2"},
    "Response": {"accent": "#f59e0b", "soft": "#fff1cf"},
}

TYPE_MONOGRAMS: Dict[str, str] = {
    "Node": "ND",
    "Control Plane": "CP",
    "Storage": "ST",
    "Networking": "NW",
    "Automation": "AU",
    "Upgrade": "UP",
    "Workload": "WL",
    "Attack": "AT",
    "Response": "RS",
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
    copy_index: int = 1

    @property
    def slug_type(self) -> str:
        return "-".join(self.type.lower().split())

    @property
    def monogram(self) -> str:
        value = TYPE_MONOGRAMS.get(self.type)
        if value:
            return value
        cleaned = "".join(ch for ch in self.type.upper() if ch.isalpha())
        return (cleaned[:2] or "??").ljust(2, "?")

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


def render_front_html(cards: List[Card]) -> str:
    total_cards = len(cards)
    total_sheets = max(1, math.ceil(total_cards / CARDS_PER_SHEET))

    head_template = Template(
        """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<title>Kubernetes Cluster Clash — Листы карточек (фронты)</title>
<style>
@page {
    size: letter;
    margin: 0.5in;
}
body {
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin: 0;
    background: #0f172a;
    color: #0f172a;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
main {
    padding: 0.5in;
}
.sheet {
    display: grid;
    grid-template-columns: repeat(3, 2.5in);
    grid-auto-rows: 3.5in;
    gap: 0.3in;
    margin-bottom: 0.5in;
    page-break-after: always;
}
.sheet:last-of-type {
    page-break-after: auto;
}
.card {
    position: relative;
    box-sizing: border-box;
    border-radius: 0.2in;
    padding: 0.18in 0.16in;
    background: #ffffff;
    border: 1.5px solid rgba(15, 23, 42, 0.25);
    display: flex;
    flex-direction: column;
    gap: 0.12in;
    overflow: hidden;
}
.card-content {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    gap: 0.12in;
    min-height: 0;
}
.card-top {
    display: flex;
    align-items: center;
    gap: 0.12in;
    min-height: 0;
}
.type-glyph {
    width: 0.42in;
    height: 0.42in;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.52rem;
    letter-spacing: 0.08em;
    color: #0f172a;
    background: rgba(148, 163, 184, 0.18);
    border: 1px solid rgba(15, 23, 42, 0.12);
}
.tag {
    flex: 1 1 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.05in 0.12in;
    border-radius: 0.16in;
    color: #ffffff;
    font-weight: 700;
    font-size: 0.5rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.cost-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 0.05in 0.14in;
    border-radius: 0.16in;
    background: #0f172a;
    color: #f8fafc;
    font-size: 0.66rem;
    font-weight: 700;
}
.card-name {
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.15;
    color: #0f172a;
}
.stat-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.08in;
}
.stat-chip {
    display: flex;
    flex-direction: column;
    gap: 0.03in;
    padding: 0.05in 0.12in;
    border-radius: 0.14in;
    background: rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(15, 23, 42, 0.12);
}
.stat-label {
    font-size: 0.46rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(15, 23, 42, 0.65);
}
.stat-value {
    font-size: 0.68rem;
    font-weight: 700;
    color: #0f172a;
}
.body-panel {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    gap: 0.08in;
    padding: 0.12in 0.14in;
    border-radius: 0.16in;
    background: #f8fafc;
    border: 1px solid rgba(15, 23, 42, 0.12);
    font-size: 0.6rem;
    line-height: 1.35;
    color: #1e293b;
    min-height: 0;
}
.body-panel p {
    margin: 0;
}
.body-panel p + p {
    margin-top: 0.08in;
}
.prereq strong {
    color: #0f172a;
}
.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.48rem;
    letter-spacing: 0.04em;
    color: rgba(15, 23, 42, 0.7);
}
.series-badge {
    padding: 0.04in 0.1in;
    border-radius: 999px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    background: rgba(148, 163, 184, 0.16);
}
.placeholder {
    border: 1.5px dashed rgba(148, 163, 184, 0.6);
    background: rgba(148, 163, 184, 0.18);
    border-radius: 0.2in;
}
${styles}
</style>
</head>
<body>
<main>
<header style="margin-bottom:0.45in; color:#e2e8f0;">
  <h1 style="margin:0;font-size:1.18rem;letter-spacing:0.1em;text-transform:uppercase;">Kubernetes Cluster Clash — Фронты</h1>
  <p style="margin:0.2rem 0 0;font-size:0.65rem;color:rgba(226,232,240,0.8);">Всего карт: $total_cards &nbsp;•&nbsp; Листов: $total_sheets</p>
</header>
"""
    )

    head = head_template.substitute(
        styles=generate_type_styles(), total_cards=total_cards, total_sheets=total_sheets
    )

    body_parts: List[str] = []
    for sheet_index in range(total_sheets):
        start = sheet_index * CARDS_PER_SHEET
        end = start + CARDS_PER_SHEET
        sheet_cards = cards[start:end]
        body_parts.append("<section class=\"sheet\">")
        for card in sheet_cards:
            body_parts.append(render_card(card))
        if len(sheet_cards) < CARDS_PER_SHEET:
            placeholders = CARDS_PER_SHEET - len(sheet_cards)
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
            f"""
.card-type-{slug} {{
    border-color: {accent};
}}
.card-type-{slug} .tag {{
    background: {accent};
}}
.card-type-{slug} .type-glyph {{
    color: {accent};
    border-color: {accent}55;
    background: {soft};
}}
.card-type-{slug} .body-panel {{
    background: linear-gradient(180deg, rgba(255,255,255,0.96), {soft});
    border-color: {accent}44;
}}
.card-type-{slug} .series-badge {{
    border-color: {accent}44;
    background: {soft};
    color: {accent};
}}
"""
        )
    return "\n".join(rules)


def render_card(card: Card) -> str:
    prereq_html = (
        f"<p class=\"prereq\"><strong>Требование:</strong> {card.display_prerequisite}</p>"
        if card.display_prerequisite
        else ""
    )

    return f"""
<div class=\"card card-type-{card.slug_type}\">
  <div class=\"card-content\">
    <div class=\"card-top\">
      <span class=\"type-glyph\">{card.monogram}</span>
      <span class=\"tag\">{card.type}</span>
      <span class=\"cost-badge\">⚙ {card.cost}</span>
    </div>
    <h2 class=\"card-name\">{card.name}</h2>
    <div class=\"stat-row\">
      <div class=\"stat-chip\">
        <span class=\"stat-label\">SLO</span>
        <span class=\"stat-value\">{card.display_slo}</span>
      </div>
      <div class=\"stat-chip\">
        <span class=\"stat-label\">Ремонт</span>
        <span class=\"stat-value\">{card.display_repair_cost}</span>
      </div>
    </div>
    <div class=\"body-panel\">
      {prereq_html}
      <p>{card.display_effect}</p>
    </div>
    <div class=\"card-footer\">
      <span>Копия {card.copy_index}/{card.quantity}</span>
      <span class=\"series-badge\">Kubernetes Cluster Clash</span>
    </div>
  </div>
</div>
"""


def render_back_html(cards: List[Card]) -> str:
    total_cards = len(cards)
    total_sheets = max(1, math.ceil(total_cards / CARDS_PER_SHEET))

    head_template = Template(
        """
<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<title>Kubernetes Cluster Clash — Листы карточек (задники)</title>
<style>
@page {
    size: letter;
    margin: 0.5in;
}
body {
    margin: 0;
    background: radial-gradient(circle at top, #0f172a 0%, #111827 40%, #1e293b 100%);
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
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
.card-back {
    position: relative;
    border-radius: 0.28in;
    background: linear-gradient(135deg, #0b3a82, #2563eb 45%, #f97316 100%);
    overflow: hidden;
    box-shadow: 0 0.18in 0.55in rgba(15, 23, 42, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.16);
    color: #f8fafc;
    display: flex;
    align-items: center;
    justify-content: center;
}
.card-back::before {
    content: '';
    position: absolute;
    width: 200%;
    height: 200%;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(25deg);
    background: radial-gradient(circle at top left, rgba(255,255,255,0.18), transparent 50%),
                radial-gradient(circle at bottom right, rgba(249, 115, 22, 0.24), transparent 55%),
                linear-gradient(160deg, rgba(14, 165, 233, 0.18), transparent 60%);
    mix-blend-mode: screen;
}
.card-back::after {
    content: '';
    position: absolute;
    width: 140%;
    height: 140%;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background-image:
        radial-gradient(circle at 20% 20%, rgba(255,255,255,0.22) 0%, transparent 45%),
        repeating-linear-gradient(60deg, rgba(255,255,255,0.04) 0, rgba(255,255,255,0.04) 6px, transparent 6px, transparent 18px);
    opacity: 0.6;
}
.back-content {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.18in;
    padding: 0.4in;
    text-align: center;
    backdrop-filter: blur(1px);
}
.logo-stack {
    position: relative;
    display: flex;
    gap: 0.18in;
    align-items: center;
}
.logo-ring {
    width: 0.8in;
    height: 0.8in;
    border-radius: 999px;
    border: 3px solid rgba(255,255,255,0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    box-shadow: 0 0.1in 0.3in rgba(15, 23, 42, 0.35);
    background: rgba(15, 23, 42, 0.25);
}
.logo-ring.kube {
    border-color: rgba(59, 130, 246, 0.85);
    background: rgba(59, 130, 246, 0.2);
}
.logo-ring.argo {
    border-color: rgba(249, 115, 22, 0.9);
    background: rgba(249, 115, 22, 0.24);
}
.title {
    font-size: 0.95rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    font-weight: 700;
}
.subtitle {
    font-size: 0.6rem;
    letter-spacing: 0.35em;
    text-transform: uppercase;
    opacity: 0.75;
}
.grid-ribbon {
    position: absolute;
    inset: 18% 15%;
    border-radius: 0.22in;
    border: 1px solid rgba(255,255,255,0.15);
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.18), rgba(59, 130, 246, 0.12));
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.05);
    mix-blend-mode: screen;
}
.placeholder {
    border: 2px dashed rgba(148, 163, 184, 0.5);
    border-radius: 0.24in;
    background: rgba(148, 163, 184, 0.2);
}
.card-back.placeholder {
    background: rgba(148, 163, 184, 0.12);
    border: 2px dashed rgba(148, 163, 184, 0.5);
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.25);
}
.card-back.placeholder::before,
.card-back.placeholder::after,
.card-back.placeholder .grid-ribbon,
.card-back.placeholder .back-content {
    display: none;
}
</style>
</head>
<body>
<main>
<header style="margin-bottom:0.45in; color:#e2e8f0;">
  <h1 style="margin:0;font-size:1.18rem;letter-spacing:0.1em;text-transform:uppercase;">Kubernetes Cluster Clash — Задники</h1>
  <p style="margin:0.2rem 0 0;font-size:0.65rem;color:rgba(226,232,240,0.8);">Всего карт: $total_cards &nbsp;•&nbsp; Листов: $total_sheets</p>
</header>
"""
    )

    head = head_template.substitute(total_cards=total_cards, total_sheets=total_sheets)

    body_parts: List[str] = [head]
    for sheet_index in range(total_sheets):
        start = sheet_index * CARDS_PER_SHEET
        end = start + CARDS_PER_SHEET
        sheet_cards = cards[start:end]
        body_parts.append("<section class=\"sheet\">")
        for _ in sheet_cards:
            body_parts.append(render_back_card())
        if len(sheet_cards) < CARDS_PER_SHEET:
            placeholders = CARDS_PER_SHEET - len(sheet_cards)
            body_parts.extend(render_back_placeholder() for _ in range(placeholders))
        body_parts.append("</section>")

    tail = """
</main>
</body>
</html>
"""

    return "\n".join(body_parts) + tail


def render_back_card() -> str:
    return """
<div class=\"card-back\">
  <span class=\"grid-ribbon\"></span>
  <div class=\"back-content\">
    <div class=\"logo-stack\">
      <span class=\"logo-ring kube\">K8S</span>
      <span class=\"logo-ring argo\">ARGO</span>
    </div>
    <div class=\"title\">Kubernetes Cluster Clash</div>
    <div class=\"subtitle\">Build • Break • Recover</div>
  </div>
</div>
"""


def render_back_placeholder() -> str:
    return "<div class=\"card-back placeholder\"></div>"


def main() -> None:
    if not CARD_CSV.exists():
        raise SystemExit(f"CSV not found: {CARD_CSV}")

    cards = load_cards(CARD_CSV)
    front_html = render_front_html(cards)
    FRONT_HTML.write_text(front_html, encoding="utf-8")

    back_html = render_back_html(cards)
    BACK_HTML.write_text(back_html, encoding="utf-8")

    sheets = math.ceil(len(cards) / CARDS_PER_SHEET)
    print(
        f"Сгенерированы фронты и задники: {len(cards)} карт, {sheets} листов -> {FRONT_HTML.name}, {BACK_HTML.name}"
    )


if __name__ == "__main__":
    main()
