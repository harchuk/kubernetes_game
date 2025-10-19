#!/usr/bin/env python3
"""Generate localized printable card fronts/backs and CSV lists."""
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
BASE_DATA = ROOT / "cards" / "data" / "cards_en.json"
LOCALE_DIR = ROOT / "cards" / "i18n"
OUTPUT_DIR = ROOT / "cards"
CARDS_PER_SHEET = 9
TARGET_LANGS = ["en", "ru", "uk", "de", "es", "fr", "zh", "ja"]

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

LANG_LABELS: Dict[str, Dict[str, str]] = {
    "en": {
        "front_title": "Kubernetes Cluster Clash — Fronts",
        "back_title": "Kubernetes Cluster Clash — Backs",
        "front_subtitle": "Total cards: {cards} • Sheets: {sheets}",
        "back_subtitle": "Total cards: {cards} • Sheets: {sheets}",
        "series": "Kubernetes Cluster Clash",
        "tagline": "Orchestrate • Disrupt • Recover",
        "slo": "SLO",
        "repair": "Repair",
        "prerequisite": "Prerequisite",
        "copy": "Copy",
        "cost": "Cost",
        "none": "—",
    },
    "ru": {
        "front_title": "Kubernetes Cluster Clash — Фронты",
        "back_title": "Kubernetes Cluster Clash — Задники",
        "front_subtitle": "Всего карт: {cards} • Листов: {sheets}",
        "back_subtitle": "Всего карт: {cards} • Листов: {sheets}",
        "series": "Kubernetes Cluster Clash",
        "tagline": "Строй • Атакуй • Восстанавливай",
        "slo": "SLO",
        "repair": "Ремонт",
        "prerequisite": "Требование",
        "copy": "Копия",
        "cost": "Стоимость",
        "none": "—",
    },
}


@dataclass
class CardTemplate:
    id: str
    name: str
    type: str
    cost: int
    slo: int
    quantity: int
    prerequisite: str
    effect: str
    repair: str

    @property
    def slug_type(self) -> str:
        return "-".join(self.type.lower().split())


@dataclass
class LocalizedTemplate:
    template: CardTemplate
    name: str
    effect: str
    prerequisite: str
    repair: str

    @property
    def type(self) -> str:
        return self.template.type

    @property
    def cost(self) -> int:
        return self.template.cost

    @property
    def slo(self) -> int:
        return self.template.slo

    @property
    def quantity(self) -> int:
        return self.template.quantity

    @property
    def slug_type(self) -> str:
        return self.template.slug_type

    @property
    def monogram(self) -> str:
        return TYPE_MONOGRAMS.get(self.type, self.type[:2].upper())


@dataclass
class LocalizedCard:
    data: LocalizedTemplate
    copy_index: int

    @property
    def name(self) -> str:
        return self.data.name

    @property
    def type(self) -> str:
        return self.data.type

    @property
    def cost(self) -> int:
        return self.data.cost

    @property
    def slo(self) -> int:
        return self.data.slo

    @property
    def quantity(self) -> int:
        return self.data.quantity

    @property
    def slug_type(self) -> str:
        return self.data.slug_type

    @property
    def monogram(self) -> str:
        return self.data.monogram

    @property
    def effect(self) -> str:
        return self.data.effect

    @property
    def prerequisite(self) -> str:
        return self.data.prerequisite

    @property
    def repair(self) -> str:
        return self.data.repair


def load_templates() -> List[CardTemplate]:
    if not BASE_DATA.exists():
        raise SystemExit(f"Base data not found: {BASE_DATA}")
    payload = json.loads(BASE_DATA.read_text(encoding="utf-8"))
    cards = []
    for entry in payload.get("cards", []):
        cards.append(
            CardTemplate(
                id=entry["id"],
                name=entry["name"],
                type=entry["type"],
                cost=int(entry["cost"]),
                slo=int(entry["slo"]),
                quantity=int(entry["quantity"]),
                prerequisite=entry.get("prerequisite", ""),
                effect=entry.get("effect", ""),
                repair=entry.get("repair", ""),
            )
        )
    return cards


def load_translations(lang: str) -> Dict[str, Dict[str, str]]:
    path = LOCALE_DIR / f"{lang}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def localize_templates(
    templates: List[CardTemplate], lang: str, translations: Dict[str, Dict[str, str]]
) -> List[LocalizedTemplate]:
    localized: List[LocalizedTemplate] = []
    for tmpl in templates:
        trans = translations.get(tmpl.id, {})
        localized.append(
            LocalizedTemplate(
                template=tmpl,
                name=trans.get("name", tmpl.name),
                effect=trans.get("effect", tmpl.effect),
                prerequisite=trans.get("prerequisite", tmpl.prerequisite),
                repair=trans.get("repair", tmpl.repair),
            )
        )
    return localized


def expand_cards(localized_templates: List[LocalizedTemplate]) -> List[LocalizedCard]:
    cards: List[LocalizedCard] = []
    for tmpl in localized_templates:
        for idx in range(1, tmpl.quantity + 1):
            cards.append(LocalizedCard(data=tmpl, copy_index=idx))
    return cards


def get_labels(lang: str) -> Dict[str, str]:
    labels = LANG_LABELS["en"].copy()
    labels.update(LANG_LABELS.get(lang, {}))
    labels.setdefault("none", "-")
    labels.setdefault("prerequisite", "Prerequisite")
    return labels


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


def render_front_html(lang: str, cards: List[LocalizedCard], labels: Dict[str, str]) -> str:
    total_cards = len(cards)
    total_sheets = max(1, math.ceil(total_cards / CARDS_PER_SHEET))
    styles = generate_type_styles()
    head = f"""
<!DOCTYPE html>
<html lang=\"{lang}\">
<head>
<meta charset=\"utf-8\" />
<title>{escape(labels['front_title'])}</title>
<style>
@page {{
    size: letter;
    margin: 0.5in;
}}
body {{
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    margin: 0;
    background: #0f172a;
    color: #0f172a;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
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
}}
.card-content {{
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    gap: 0.12in;
    min-height: 0;
}}
.card-top {{
    display: flex;
    align-items: center;
    gap: 0.12in;
}}
.type-glyph {{
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
}}
.tag {{
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
}}
.cost-badge {{
    display: inline-flex;
    flex-direction: column;
    align-items: center;
    padding: 0.04in 0.14in;
    border-radius: 0.14in;
    background: #0f172a;
    color: #f8fafc;
}}
.cost-label {{
    font-size: 0.45rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    opacity: 0.65;
}}
.cost-value {{
    font-size: 0.7rem;
    font-weight: 700;
}}
.card-name {{
    margin: 0;
    font-size: 0.9rem;
    line-height: 1.15;
    color: #0f172a;
}}
.stat-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 0.08in;
}}
.stat-chip {{
    display: flex;
    flex-direction: column;
    gap: 0.03in;
    padding: 0.05in 0.12in;
    border-radius: 0.14in;
    background: rgba(15, 23, 42, 0.04);
    border: 1px solid rgba(15, 23, 42, 0.12);
}}
.stat-label {{
    font-size: 0.46rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(15, 23, 42, 0.65);
}}
.stat-value {{
    font-size: 0.68rem;
    font-weight: 700;
    color: #0f172a;
}}
.body-panel {{
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
}}
.body-panel p {{
    margin: 0;
}}
.body-panel p + p {{
    margin-top: 0.08in;
}}
.prereq strong {{
    color: #0f172a;
}}
.card-footer {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.48rem;
    letter-spacing: 0.04em;
    color: rgba(15, 23, 42, 0.7);
}}
.series-badge {{
    padding: 0.04in 0.1in;
    border-radius: 999px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    background: rgba(148, 163, 184, 0.16);
}}
.placeholder {{
    border: 1.5px dashed rgba(148, 163, 184, 0.6);
    background: rgba(148, 163, 184, 0.18);
    border-radius: 0.2in;
}}
{styles}
</style>
</head>
<body>
<main>
<header style=\"margin-bottom:0.4in; color:#e2e8f0;\">
  <h1 style=\"margin:0;font-size:1.08rem;letter-spacing:0.1em;text-transform:uppercase;\">{escape(labels['front_title'])} [{lang.upper()}]</h1>
  <p style=\"margin:0.18rem 0 0;font-size:0.6rem;color:rgba(226,232,240,0.82);\">{escape(labels['front_subtitle'].format(cards=total_cards, sheets=total_sheets))}</p>
</header>
"""

    body_parts: List[str] = [head]
    for sheet_index in range(total_sheets):
        start = sheet_index * CARDS_PER_SHEET
        end = start + CARDS_PER_SHEET
        sheet_cards = cards[start:end]
        body_parts.append("<section class=\"sheet\">")
        for card in sheet_cards:
            body_parts.append(render_card(card, labels))
        if len(sheet_cards) < CARDS_PER_SHEET:
            placeholders = CARDS_PER_SHEET - len(sheet_cards)
            body_parts.extend("<div class=\"card placeholder\"></div>" for _ in range(placeholders))
        body_parts.append("</section>")

    body_parts.append("</main>\n</body>\n</html>")
    return "\n".join(body_parts)


def render_card(card: LocalizedCard, labels: Dict[str, str]) -> str:
    prerequisite = card.prerequisite.strip()
    prereq_html = (
        f"<p class=\"prereq\"><strong>{escape(labels['prerequisite'])}:</strong> {escape(prerequisite)}</p>"
        if prerequisite
        else ""
    )
    slo_display = str(card.slo) if card.slo > 0 else labels.get("none", "-")
    repair_text = card.repair.strip() or labels.get("none", "-")
    return """
<div class=\"card card-type-{slug}\">
  <div class=\"card-content\">
    <div class=\"card-top\">
      <span class=\"type-glyph\">{glyph}</span>
      <span class=\"tag\">{type}</span>
      <span class=\"cost-badge\"><span class=\"cost-label\">{cost_label}</span><span class=\"cost-value\">{cost}</span></span>
    </div>
    <h2 class=\"card-name\">{name}</h2>
    <div class=\"stat-row\">
      <div class=\"stat-chip\">
        <span class=\"stat-label\">{slo_label}</span>
        <span class=\"stat-value\">{slo}</span>
      </div>
      <div class=\"stat-chip\">
        <span class=\"stat-label\">{repair_label}</span>
        <span class=\"stat-value\">{repair}</span>
      </div>
    </div>
    <div class=\"body-panel\">
      {prereq}
      <p>{effect}</p>
    </div>
    <div class=\"card-footer\">
      <span>{copy_label} {copy}/{total}</span>
      <span class=\"series-badge\">{series}</span>
    </div>
  </div>
</div>
""".format(
        slug=card.slug_type,
        glyph=escape(card.monogram),
        type=escape(card.type),
        cost_label=escape(labels["cost"]),
        cost=escape(str(card.cost)),
        name=escape(card.name),
        slo_label=escape(labels["slo"]),
        slo=escape(slo_display),
        repair_label=escape(labels["repair"]),
        repair=escape(repair_text),
        prereq=prereq_html,
        effect=escape(card.effect),
        copy_label=escape(labels["copy"]),
        copy=card.copy_index,
        total=card.quantity,
        series=escape(labels["series"]),
    )


def render_back_html(lang: str, total_cards: int, labels: Dict[str, str]) -> str:
    total_sheets = max(1, math.ceil(total_cards / CARDS_PER_SHEET))
    head = f"""
<!DOCTYPE html>
<html lang=\"{lang}\">
<head>
<meta charset=\"utf-8\" />
<title>{escape(labels['back_title'])}</title>
<style>
@page {{
    size: letter;
    margin: 0.5in;
}}
body {{
    margin: 0;
    background: #0f172a;
    font-family: 'Segoe UI', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
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
.card-back {{
    position: relative;
    border-radius: 0.2in;
    background: radial-gradient(circle at top, #1d4ed8, #0f172a 65%);
    overflow: hidden;
    border: 1.5px solid rgba(148, 163, 184, 0.45);
    box-shadow: 0 0.18in 0.42in rgba(15, 23, 42, 0.35);
    color: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
}}
.card-back::before {{
    content: '';
    position: absolute;
    inset: -30% -10%;
    background: repeating-linear-gradient(60deg, rgba(226, 232, 240, 0.08) 0, rgba(226, 232, 240, 0.08) 12px, transparent 12px, transparent 24px),
                repeating-linear-gradient(-60deg, rgba(59, 130, 246, 0.08) 0, rgba(59, 130, 246, 0.08) 12px, transparent 12px, transparent 24px);
    opacity: 0.4;
    mix-blend-mode: screen;
}}
.card-back::after {{
    content: '';
    position: absolute;
    inset: 12% 14%;
    border-radius: 0.18in;
    border: 1px solid rgba(226, 232, 240, 0.3);
    background: linear-gradient(120deg, rgba(148, 163, 184, 0.15), transparent);
}}
.back-content {{
    position: relative;
    z-index: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.16in;
    padding: 0.3in;
    text-align: center;
}}
.emblem {{
    width: 0.95in;
    height: 0.95in;
    border-radius: 50%;
    border: 3px solid rgba(226, 232, 240, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: rgba(15, 23, 42, 0.4);
    box-shadow: 0 0.12in 0.35in rgba(15, 23, 42, 0.35);
}}
.title {{
    font-size: 0.95rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    font-weight: 700;
}}
.subtitle {{
    font-size: 0.58rem;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    opacity: 0.75;
}}
.placeholder {{
    border: 1.5px dashed rgba(148, 163, 184, 0.55);
    border-radius: 0.2in;
    background: rgba(148, 163, 184, 0.18);
}}
.card-back.placeholder::before,
.card-back.placeholder::after,
.card-back.placeholder .back-content {{
    display: none;
}}
</style>
</head>
<body>
<main>
<header style=\"margin-bottom:0.4in; color:#e2e8f0;\">
  <h1 style=\"margin:0;font-size:1.08rem;letter-spacing:0.1em;text-transform:uppercase;\">{escape(labels['back_title'])} [{lang.upper()}]</h1>
  <p style=\"margin:0.18rem 0 0;font-size:0.6rem;color:rgba(226,232,240,0.82);\">{escape(labels['back_subtitle'].format(cards=total_cards, sheets=total_sheets))}</p>
</header>
"""

    body_parts: List[str] = [head]
    remaining = total_cards
    for _ in range(total_sheets):
        count = min(CARDS_PER_SHEET, remaining)
        remaining -= count
        body_parts.append("<section class=\"sheet\">")
        for _ in range(count):
            body_parts.append(render_back_card(labels))
        for _ in range(CARDS_PER_SHEET - count):
            body_parts.append(render_back_placeholder())
        body_parts.append("</section>")

    body_parts.append("</main>\n</body>\n</html>")
    return "\n".join(body_parts)


def render_back_card(labels: Dict[str, str]) -> str:
    return """
<div class=\"card-back\">
  <div class=\"back-content\">
    <div class=\"emblem\">KC</div>
    <div class=\"title\">{series}</div>
    <div class=\"subtitle\">{tagline}</div>
  </div>
</div>
""".format(series=escape(labels["series"]), tagline=escape(labels["tagline"]))


def render_back_placeholder() -> str:
    return "<div class=\"card-back placeholder\"></div>"


def write_card_csv(lang: str, templates: List[LocalizedTemplate]) -> Path:
    path = OUTPUT_DIR / f"card_list_{lang}.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["name", "type", "cost", "slo", "quantity", "prerequisite", "effect", "repair"])
        for tmpl in templates:
            writer.writerow(
                [
                    tmpl.name,
                    tmpl.type,
                    tmpl.cost,
                    tmpl.slo,
                    tmpl.quantity,
                    tmpl.prerequisite,
                    tmpl.effect,
                    tmpl.repair,
                ]
            )
    return path


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    ensure_output_dir()
    templates = load_templates()
    total_cards = sum(t.quantity for t in templates)
    summary: List[str] = []

    for lang in TARGET_LANGS:
        labels = get_labels(lang)
        translations = load_translations(lang)
        localized_templates = localize_templates(templates, lang, translations)
        cards = expand_cards(localized_templates)

        front_html = render_front_html(lang, cards, labels)
        front_path = OUTPUT_DIR / f"cards_print_{lang}.html"
        front_path.write_text(front_html, encoding="utf-8")
        if lang == "en":
            (OUTPUT_DIR / "cards_print.html").write_text(front_html, encoding="utf-8")

        back_html = render_back_html(lang, total_cards, labels)
        back_path = OUTPUT_DIR / f"cards_back_{lang}.html"
        back_path.write_text(back_html, encoding="utf-8")
        if lang == "en":
            (OUTPUT_DIR / "cards_back.html").write_text(back_html, encoding="utf-8")

        csv_path = write_card_csv(lang, localized_templates)
        if lang == "en":
            (OUTPUT_DIR / "card_list.csv").write_text(csv_path.read_text(encoding="utf-8"), encoding="utf-8")

        summary.append(f"{lang}: {len(cards)} cards -> {front_path.name}, {csv_path.name}")

    print("Generated assets for languages:")
    for line in summary:
        print(f"  - {line}")


if __name__ == "__main__":
    main()
