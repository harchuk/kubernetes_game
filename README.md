# Kubernetes Cluster Clash

Kubernetes Cluster Clash is a competitive tabletop card game where cloud-native engineers race to assemble resilient Kubernetes clusters while sabotaging their rivals. Balance your resources, automate your infrastructure, and survive outages to be crowned Cluster Champion.

## Project Structure

- `rules/` - printable rules reference and designer notes.
- `cards/` - card list exports for printing and prototyping.
- `playmats/` - optional player aids for tracking cluster state.
- `print_and_play/` - ready-to-print artefacts generated from source files.
- `tools/` - helper scripts for generating printable sheets.

## Status

Game materials are under active development. See `rules/rulebook.md` for how to play and `cards/card_list.csv` for the current card set.

## Generating Card Sheets

Run `./tools/generate_card_sheets.py` to build `cards/cards_print.html`, then print the file to PDF from your browser with scaling set to 100%.
