# Player Cluster Aid

```
┌───────────────────────────────────────────────┐
│               CLUSTER OVERVIEW               │
├───────────────────────────┬───────────────────┤
│ Infrastructure Slots      │ Workload Slots    │
│ [Node][Node][Node]        │ [Service][Service]│
│ [Control][Storage][Net]   │ [Service][Service]│
├───────────────────────────┴───────────────────┤
│ Automation / Upgrades                         │
│ [      ][      ][      ][      ]              │
├───────────────────────────────────────────────┤
│ SLO Track (12)  [][][][][][][][][][]          │
│ Resilience Track (start at 6) 6 [][][]        │
│ Incident Staging Area   [ ][ ][ ]             │
└───────────────────────────────────────────────┘
```

## Usage
- Place Nodes and Control Plane in the top-left grid.
- Place Storage and Networking support cards in the remaining infrastructure slots.
- Lay Workloads in the right column; tuck supporting cards beneath their host Node if space is tight.
- Track SLO with a cube on the bottom track; hitting 12 wins (15 in duel mode).
- Track Resilience by moving a cube up or down the side track.
- Keep Incident markers in the staging area to remind you to resolve them during the Incident phase.
