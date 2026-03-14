# Progression State

Date captured: 2026-03-05
Last updated: 2026-03-14

## Live Progression Rules

- Offsite EXP is currently sourced from onsite-driven pools in idle processing.
- Character stacks currently affect:
  - stat scaling via `party_scaling`: `1.0 + 0.12 * (stacks - 1)`
  - idle EXP passive modifier: `(stacks * 0.05) + 1.0` (onsite and offsite gain paths)
- Runtime character plugin stars are strict for discovered runtime plugins:
  - valid stars are `5-7`
  - invalid stars fail discovery with an aggregated `ValueError`

## Mech 1 Live Star Effects

- Star-to-progression multiplier mapping:
  - 7 star = `2.5x`
  - 6 star = `1.0x`
  - 5 star = `0.5x`
- Live effects:
  - rebirth EXP reward gain is multiplied by star rank power
  - post-500 rebirth EXP tax is softened by star rank power
  - prestige weighted stat-growth magnitude is multiplied by star rank power
