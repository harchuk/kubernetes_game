#!/usr/bin/env python3
"""Lightweight simulator to explore balance trends for Kubernetes Cluster Clash."""
from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import Counter, deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
CARDS_DATA = ROOT / "cards" / "data" / "cards_en.json"

BASE_HAND_SIZE = 5
REFRESH_GAIN = 3
WIN_SLO_THRESHOLD = 10
MAX_RESILIENCE = 6

STRATEGY_ORDER = {
    "builder": [
        "Control Plane",
        "Node",
        "Storage",
        "Networking",
        "Automation",
        "Workload",
        "Upgrade",
        "Attack",
        "Response",
    ],
    "saboteur": [
        "Attack",
        "Node",
        "Control Plane",
        "Workload",
        "Automation",
        "Upgrade",
        "Storage",
        "Networking",
        "Response",
    ],
    "balanced": [
        "Node",
        "Control Plane",
        "Workload",
        "Attack",
        "Storage",
        "Networking",
        "Automation",
        "Upgrade",
        "Response",
    ],
}

# Priority boost applied when an attack would finish a player this turn.
FINISH_ATTACK_BONUS = 20


@dataclass
class CardDef:
    id: str
    name: str
    type: str
    cost: int
    slo: int
    prerequisite: str


@dataclass
class CardTemplate:
    definition: CardDef
    quantity: int


def load_card_templates() -> List[CardTemplate]:
    payload = json.loads(CARDS_DATA.read_text(encoding="utf-8"))
    templates: List[CardTemplate] = []
    for entry in payload["cards"]:
        templates.append(
            CardTemplate(
                definition=CardDef(
                    id=entry["id"],
                    name=entry["name"],
                    type=entry["type"],
                    cost=int(entry["cost"]),
                    slo=int(entry["slo"]),
                    prerequisite=entry.get("prerequisite", ""),
                ),
                quantity=int(entry["quantity"]),
            )
        )
    return templates


@dataclass
class PlayerState:
    index: int
    strategy: str
    resources: int = 5
    resilience: int = MAX_RESILIENCE
    resilience_max: int = MAX_RESILIENCE
    slo: int = 0
    nodes: int = 0
    gpu_nodes: int = 0
    control_planes: int = 0
    storage: int = 0
    networking: int = 0
    automation: int = 0
    upgrades: int = 0
    workloads: int = 0
    passive_income: int = 0
    autoscaler: bool = False
    skip_plan: bool = False
    control_locked: int = 0
    incidents: int = 0
    hand: List[str] = field(default_factory=list)
    tableau: List[str] = field(default_factory=list)
    response_reserve: List[str] = field(default_factory=list)

    def reset_for_new_game(self) -> None:
        self.resources = 5
        self.resilience = MAX_RESILIENCE
        self.resilience_max = MAX_RESILIENCE
        self.slo = 0
        self.nodes = 0
        self.gpu_nodes = 0
        self.control_planes = 0
        self.storage = 0
        self.networking = 0
        self.automation = 0
        self.upgrades = 0
        self.workloads = 0
        self.passive_income = 0
        self.autoscaler = False
        self.skip_plan = False
        self.control_locked = 0
        self.incidents = 0
        self.hand.clear()
        self.tableau.clear()
        self.response_reserve.clear()

    def capacity(self) -> int:
        return max(self.nodes, 0)

    def can_play_workload(self) -> bool:
        return self.control_planes > 0 and self.nodes >= 1 and self.workloads < self.capacity()

    def apply_incident(self, amount: int = 1) -> None:
        self.incidents += amount

    def heal_incident(self, amount: int = 1) -> None:
        self.incidents = max(0, self.incidents - amount)

    def adjust_resilience(self, delta: int) -> None:
        self.resilience = max(0, min(self.resilience_max, self.resilience + delta))


@dataclass
class SimulationConfig:
    num_players: int = 3
    games: int = 100
    max_turns: int = 40
    strategies: Iterable[str] = ("builder", "balanced", "saboteur")
    seed: Optional[int] = None


@dataclass
class SimulationResult:
    total_games: int
    wins: Counter
    avg_turns: float
    mean_slo: float
    mean_resilience: float
    attack_rate: float
    data_points: List[Dict[str, float]]


def build_deck(templates: List[CardTemplate]) -> List[str]:
    deck: List[str] = []
    for tmpl in templates:
        deck.extend([tmpl.definition.id] * tmpl.quantity)
    random.shuffle(deck)
    return deck


def prerequisite_met(player: PlayerState, definition: CardDef) -> bool:
    prereq = definition.prerequisite.lower()
    if not prereq:
        return True
    if "requires 2 node" in prereq:
        return player.nodes >= 2
    if "requires node" in prereq and "gpu" not in prereq:
        return player.nodes >= 1
    if "requires gpu" in prereq:
        return player.gpu_nodes >= 1
    if "requires control plane" in prereq:
        return player.control_planes >= 1 and player.control_locked == 0
    if "requires storage" in prereq:
        return player.storage >= 1
    if "requires networking" in prereq:
        return player.networking >= 1
    return True


def attack_targets(players: List[PlayerState], attacker: PlayerState) -> List[PlayerState]:
    return [p for p in players if p.index != attacker.index and p.resilience > 0]


def handle_attack(card_id: str, attacker: PlayerState, players: List[PlayerState], attack_log: Counter) -> None:
    targets = attack_targets(players, attacker)
    if not targets:
        return
    target = max(targets, key=lambda p: (p.slo, p.resilience))
    # Simple response: if target stored a response card, cancel once.
    if target.response_reserve:
        target.response_reserve.pop()
        attack_log['responses'] += 1
        return
    attack_log['attacks'] += 1
    if card_id == 'ddos_burst':
        target.adjust_resilience(-2)
        target.resources = max(0, target.resources - 2)
        target.apply_incident(2)
    elif card_id == 'supply_chain_compromise':
        if target.automation > 0:
            target.automation -= 1
        target.apply_incident(1)
        target.adjust_resilience(-1)
    elif card_id == 'rogue_cronjob':
        if target.workloads > 0:
            target.workloads -= 1
            target.slo = max(0, target.slo - 1)
    elif card_id == 'budget_freeze':
        target.resources = max(0, target.resources - 2)
        target.skip_plan = True
    elif card_id == 'compliance_audit':
        target.resources = max(0, target.resources - 1)
    elif card_id == 'zombie_pod_swarm':
        target.adjust_resilience(-1)
        target.apply_incident(1)
        target.control_locked = max(target.control_locked, 1)


def passive_effects(player: PlayerState) -> None:
    if player.autoscaler and player.nodes >= 2:
        player.resources += player.nodes // 2
    if player.passive_income:
        player.resources += player.passive_income


def play_card(
    player: PlayerState,
    definition: CardDef,
    deck_discard: deque,
    attack_log: Counter,
    players: List[PlayerState],
) -> None:
    card_id = definition.id
    card_type = definition.type
    player.resources -= definition.cost
    if card_type == 'Node':
        player.nodes += 1
        player.resilience_max += 2
        player.resilience = min(player.resilience_max, player.resilience + 1)
        if card_id == 'gpu_accelerator_node':
            player.gpu_nodes += 1
    elif card_type == 'Control Plane':
        if player.control_locked:
            player.control_locked -= 1
        player.control_planes += 1
    elif card_type == 'Storage':
        player.storage += 1
    elif card_type == 'Networking':
        player.networking += 1
    elif card_type == 'Automation':
        player.automation += 1
        if card_id == 'stateless_api_service':
            player.passive_income += 1
        if card_id == 'cluster_autoscaler':
            player.autoscaler = True
    elif card_type == 'Upgrade':
        player.upgrades += 1
    elif card_type == 'Workload':
        player.workloads += 1
        player.slo += definition.slo
    elif card_type == 'Attack':
        handle_attack(card_id, player, players, attack_log)
        deck_discard.append(card_id)
        return
    elif card_type == 'Response':
        player.response_reserve.append(card_id)
        return
    # Persistent cards remain in tableau for bookkeeping.
    player.tableau.append(card_id)


def choose_play_sequence(
    player: PlayerState,
    hand: List[str],
    definitions: Dict[str, CardDef],
    players: List[PlayerState],
) -> List[str]:
    order = STRATEGY_ORDER.get(player.strategy, STRATEGY_ORDER['balanced'])
    type_priority = {card_type: (len(order) - idx) for idx, card_type in enumerate(order)}
    scored_cards: List[Tuple[int, int, str]] = []
    for card_id in hand:
        definition = definitions[card_id]
        base_priority = type_priority.get(definition.type, 0)
        cost_penalty = definition.cost
        slo_bonus = definition.slo * 2
        if definition.type == 'Attack':
            targets = attack_targets(players, player)
            if targets and max(t.slo for t in targets) + definition.slo >= WIN_SLO_THRESHOLD:
                base_priority += FINISH_ATTACK_BONUS
        scored_cards.append((base_priority * 100 - cost_penalty + slo_bonus, -definition.cost, card_id))
    scored_cards.sort(reverse=True)
    return [card_id for *_ , card_id in scored_cards]


def resolve_turn(
    player: PlayerState,
    players: List[PlayerState],
    draw_pile: deque,
    discard_pile: deque,
    definitions: Dict[str, CardDef],
    attack_log: Counter,
) -> None:
    # Refresh
    if player.incidents:
        player.heal_incident()
    to_draw = max(0, BASE_HAND_SIZE - len(player.hand))
    draw_cards(player, to_draw, draw_pile, discard_pile)
    gain = REFRESH_GAIN + (1 if player.passive_income else 0)
    player.resources += gain

    if player.skip_plan:
        player.skip_plan = False
    passive_effects(player)

    playable_order = choose_play_sequence(player, list(player.hand), definitions, players)
    for card_id in playable_order:
        if card_id not in player.hand:
            continue
        definition = definitions[card_id]
        if player.resources < definition.cost:
            continue
        if definition.type == 'Workload' and not player.can_play_workload():
            continue
        if not prerequisite_met(player, definition):
            continue
        player.hand.remove(card_id)
        play_card(player, definition, discard_pile, attack_log, players)

    # Responses kept in reserve already. Discard remaining cards down to 7.
    while len(player.hand) > 7:
        discard_pile.append(player.hand.pop())


def draw_cards(player: PlayerState, count: int, draw_pile: deque, discard_pile: deque) -> None:
    for _ in range(count):
        if not draw_pile:
            if not discard_pile:
                break
            deck_restore = list(discard_pile)
            discard_pile.clear()
            random.shuffle(deck_restore)
            draw_pile.extend(deck_restore)
        player.hand.append(draw_pile.pop())


def play_game(config: SimulationConfig, templates: List[CardTemplate]) -> Tuple[int, int, List[PlayerState], Counter, int]:
    draw_pile = deque(build_deck(templates))
    discard_pile: deque[str] = deque()
    definitions = {tmpl.definition.id: tmpl.definition for tmpl in templates}
    players = [PlayerState(index=i, strategy=list(config.strategies)[i % len(config.strategies)]) for i in range(config.num_players)]
    for p in players:
        p.reset_for_new_game()
        draw_cards(p, BASE_HAND_SIZE, draw_pile, discard_pile)
    attack_log: Counter = Counter()
    turn = 0
    winner: Optional[int] = None

    while turn < config.max_turns and winner is None:
        for player in players:
            if player.resilience <= 0:
                continue
            resolve_turn(player, players, draw_pile, discard_pile, definitions, attack_log)
            if player.slo >= WIN_SLO_THRESHOLD and player.resilience > 0:
                winner = player.index
                break
        turn += 1

    if winner is None:
        # Determine winner by highest SLO then resilience.
        alive = [p for p in players if p.resilience > 0]
        if alive:
            alive.sort(key=lambda p: (p.slo, p.resilience), reverse=True)
            winner = alive[0].index
        else:
            winner = 0
    return winner, turn, players, attack_log, len(draw_pile)


def run_simulation(config: SimulationConfig) -> SimulationResult:
    if config.seed is not None:
        random.seed(config.seed)
    templates = load_card_templates()
    wins: Counter = Counter()
    turns: List[int] = []
    slo_values: List[int] = []
    resilience_values: List[int] = []
    attack_counter: Counter = Counter()
    discard_sizes: List[int] = []

    for _ in range(config.games):
        winner, turn_count, players, attack_log, draw_remaining = play_game(config, templates)
        wins[winner] += 1
        turns.append(turn_count)
        attack_counter.update(attack_log)
        discard_sizes.append(draw_remaining)
        for p in players:
            slo_values.append(p.slo)
            resilience_values.append(p.resilience)

    total_attacks = attack_counter.get('attacks', 0)
    total_turns = sum(turns)
    avg_turns = statistics.mean(turns) if turns else 0.0
    mean_slo = statistics.mean(slo_values) if slo_values else 0.0
    mean_res = statistics.mean(resilience_values) if resilience_values else 0.0
    attack_rate = total_attacks / total_turns if total_turns else 0.0
    datapoints = [
        {
            "turns": avg_turns,
            "mean_slo": mean_slo,
            "mean_resilience": mean_res,
            "attack_rate": attack_rate,
        }
    ]
    return SimulationResult(
        total_games=config.games,
        wins=wins,
        avg_turns=avg_turns,
        mean_slo=mean_slo,
        mean_resilience=mean_res,
        attack_rate=attack_rate,
        data_points=datapoints,
    )


def format_summary(result: SimulationResult, config: SimulationConfig) -> str:
    lines = [f"Games: {result.total_games}"]
    lines.append(f"Average turns: {result.avg_turns:.2f}")
    lines.append(f"Average SLO per player: {result.mean_slo:.2f}")
    lines.append(f"Average resilience per player: {result.mean_resilience:.2f}")
    lines.append(f"Attacks per turn: {result.attack_rate:.2f}")
    for player_index, wins in sorted(result.wins.items()):
        strategy = list(config.strategies)[player_index % len(config.strategies)]
        lines.append(f"Player {player_index + 1} ({strategy}) wins: {wins}")
    return "\n".join(lines)


def parse_args() -> SimulationConfig:
    parser = argparse.ArgumentParser(description="Simulate Kubernetes Cluster Clash matches")
    parser.add_argument("--players", type=int, default=3, help="Number of players")
    parser.add_argument("--games", type=int, default=100, help="Number of games to simulate")
    parser.add_argument("--max-turns", type=int, default=40, help="Turn limit to prevent infinite games")
    parser.add_argument(
        "--strategies",
        nargs="*",
        default=["builder", "balanced", "saboteur"],
        help="Strategy identifiers per seat",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args()
    if not args.strategies:
        args.strategies = ["balanced"]
    return SimulationConfig(
        num_players=args.players,
        games=args.games,
        max_turns=args.max_turns,
        strategies=args.strategies,
        seed=args.seed,
    )


def main() -> None:
    config = parse_args()
    result = run_simulation(config)
    print(format_summary(result, config))


if __name__ == "__main__":
    main()
