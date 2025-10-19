# Kubernetes Cluster Clash — Rulebook

## Theme and Goal
You are a platform engineer racing to stand up the most resilient Kubernetes cluster in a competitive market. Harvest resources, deploy workloads, and sabotage rival clusters with outages, exploits, and budget cuts. The first engineer to hit the published Service Level Objectives (SLOs) wins — unless their cluster collapses in spectacular fashion.

## Components
- 90-card main deck (see `cards/card_list.csv`).
- 4 cluster board sheets (use `playmats/player_cluster_aid.md`).
- 60 Resource tokens (generic currency representing CPU/Memory/Budget).
- 12 Resilience cubes (track cluster health).
- 20 Incident markers (track ongoing outages or exploits).
- 1 First Player marker.
- Rulebook and Quick Reference sheet.

> Prototype note: substitute poker chips or coins for tokens and cubes.

## Glossary
- **Cluster Board**: Personal tableau that holds Nodes, Control Plane, Workloads, and Support cards you have played.
- **SLO Track**: Built into the cluster board; reaching 12 SLO points wins the game.
- **Incident**: Negative effect marker placed by Attack cards that stays until cleared.
- **Resilience**: Your cluster's health. If it drops below zero, you are eliminated.

## Setup
1. Shuffle the main deck and deal each player 5 cards.
2. Give each player: 1 cluster board, 5 Resource tokens, 3 Resilience cubes set to value 6 on their board.
3. Place remaining tokens and cubes in a supply within reach.
4. Randomly select the first player; give them the marker.
5. Reveal 3 cards from the top of the deck to form the **Commons Row** market. Refill this row at the end of each turn.

## Turn Structure
Play proceeds clockwise. On your turn resolve phases in order:

1. **Refresh**
   - Remove 1 Incident marker from one card you control (optional).
   - Draw up to a hand of 5 cards.
   - Gain 2 Resource tokens from the supply.

2. **Plan (optional)**
   - You may discard any number of cards to gain 1 Resource token each.

3. **Deploy**
   - Play cards from your hand by paying their Resource cost.
   - You may purchase cards from the Commons Row by paying their cost, placing them directly into your hand, then immediately continuing your Deploy phase.
   - Infrastructure cards (Nodes, Control Plane, Storage, Networking) enter your Cluster Board.
   - Automation and Upgrade cards typically grant ongoing abilities.
   - Workload cards enter your Workload area and contribute SLO points.

4. **Incidents**
   - Resolve any Incident markers on your cards. Most reduce Resilience or disable cards until cleared.

5. **Sabotage (optional)**
   - You may play 1 Attack card from your hand, targeting another player whose Resilience is above 0. Pay its cost, apply its effect, and place Incident markers if instructed.

6. **Stabilize**
   - You may pay the specified Repair cost on cards to remove Incident markers.
   - Check your SLO total. If you have reached 12 or more, and your Resilience is above 0, your cluster is live and you win at the end of the round.
   - If your Resilience drops below 0, your cluster fails. Discard your hand, flip your board: you are out of the game.

7. **End Step**
   - Discard down to 7 cards.
   - Refill the Commons Row to 3 cards.

## Card Types

| Card Type       | Zone           | Typical Effect                                     |
|-----------------|----------------|----------------------------------------------------|
| Node            | Infrastructure | Provides capacity, increases Resilience baseline.  |
| Control Plane   | Infrastructure | Enables playing advanced cards and SLO scoring.    |
| Storage         | Infrastructure | Provides stability for Stateful workloads.         |
| Networking      | Infrastructure | Increases attack defense and market access.        |
| Workload        | Workload area  | Grants SLO points and may have ongoing effects.    |
| Automation      | Cluster board  | Grants ongoing effects or resource discounts.      |
| Upgrade         | Cluster board  | One-time boosts, improved defenses, victory points.|
| Attack          | Opponent board | Adds Incidents, steals resources, reduces SLO.     |
| Response        | Instant discard| Cancels Attacks or mitigates damage.               |

## Building Your Cluster
- You must control at least **1 Control Plane** and **2 Nodes** before you can play Workload cards.
- Each Node increases your Resilience maximum by 2 (move cube).
- The first Control Plane you play triggers a free draw.
- Workloads add SLO points equal to the value shown on the card. Track on the SLO track.
- Some cards have **Prerequisites** (e.g., "Requires Networking"). You must meet them to play the card.

## Attacking and Defending
- Attack cards specify a target and effect. Place Incident markers on the target card or player board as instructed.
- Multiple Incident markers can stack. Each Incident on a Node reduces your Resilience by 1 during the Incident phase.
- When you play a Response card, resolve its text immediately then discard it.
- You may use the Stabilize phase to remove Incidents. Some cards have custom repair costs.

## Winning the Game
- At the end of any round in which a player has 12+ SLO points and positive Resilience, they win.
- If all other players are eliminated, the surviving player wins immediately.
- In a 2-player game, reaching 15 SLO points is required for victory to ensure a longer duel.

## Solo and Co-op Variant
- Reveal the top card of the deck each round to simulate an automated attacker called **Chaos Monkey**.
- Chaos Monkey triggers Attack cards against the leading player or discards the card if not an Attack.
- Solo players must reach 15 SLO points before Resilience hits 0.

## Designer Notes
- Emphasize tempo: players should decide between expanding infrastructure and disrupting others.
- Encourage trading: allow table deals to pause attacks or share temporary alliances.
- Keep downtime low by limiting mandatory triggered abilities.

