# Gas Selection Decision Tree

Source: `ui/components/calculators_panel.py` (`select_assist_gas`)

## Inputs

- `material`: `carbon_steel | stainless_steel | galvanized_steel | aluminum | other`
- `thickness_mm`: numeric thickness in mm
- `edge_quality`: `high | medium | low`
- `post_process`: `none | welding | painting`
- `cost_priority`: `true | false`

Derived flag used by the algorithm:

- `avoid_oxygen = (post_process in [welding, painting])`

## Full Decision Tree

```text
START
|
+-- Compute avoid_oxygen = (post_process is welding or painting)
|
+-- material == carbon_steel?
|   |
|   +-- YES
|   |   |
|   |   +-- thickness_mm > 12?
|   |   |   |
|   |   |   +-- YES
|   |   |   |   |
|   |   |   |   +-- avoid_oxygen == true?
|   |   |   |       |
|   |   |   |       +-- YES -> GAS = nitrogen
|   |   |   |       |         Reason: Thick carbon steel usually uses oxygen,
|   |   |   |       |         but welding/painting requires oxide-free edges.
|   |   |   |       |
|   |   |   |       +-- NO  -> GAS = oxygen
|   |   |   |                 Reason: For heavy carbon steel, oxygen adds
|   |   |   |                 exothermic energy for full-depth cutting.
|   |   |   |
|   |   |   +-- NO
|   |   |       |
|   |   |       +-- thickness_mm <= 3?
|   |   |           |
|   |   |           +-- YES
|   |   |           |   |
|   |   |           |   +-- avoid_oxygen == true AND cost_priority == true?
|   |   |           |   |   |
|   |   |           |   |   +-- YES -> GAS = compressed_air
|   |   |           |   |   |         Reason: Thin sheet + post-processing +
|   |   |           |   |   |         cost priority favors low-cost, low-oxidation air.
|   |   |           |   |   |
|   |   |           |   |   +-- NO
|   |   |           |   |       |
|   |   |           |   |       +-- edge_quality == high?
|   |   |           |   |           |
|   |   |           |   |           +-- YES -> GAS = nitrogen
|   |   |           |   |           |         Reason: High edge quality on thin
|   |   |           |   |           |         carbon steel favors oxidation-free cuts.
|   |   |           |   |           |
|   |   |           |   |           +-- NO
|   |   |           |   |               |
|   |   |           |   |               +-- cost_priority == true?
|   |   |           |   |                   |
|   |   |           |   |                   +-- YES -> GAS = compressed_air
|   |   |           |   |                   |         Reason: Cost reduction is prioritized.
|   |   |           |   |                   |
|   |   |           |   |                   +-- NO  -> GAS = compressed_air
|   |   |           |   |                             Reason: Default for thin carbon steel:
|   |   |           |   |                             acceptable quality at low cost.
|   |   |           |
|   |   |           +-- NO  (this means 3 < thickness_mm <= 12)
|   |   |               |
|   |   |               +-- avoid_oxygen == true?
|   |   |                   |
|   |   |                   +-- YES -> GAS = nitrogen
|   |   |                   |         Reason: Post-processing requires oxide-free edges.
|   |   |                   |
|   |   |                   +-- NO  -> GAS = oxygen
|   |   |                             Reason: Mid-thickness carbon steel benefits from
|   |   |                             oxygen exothermic cutting support.
|   |
|   +-- NO
|       |
|       +-- material == stainless_steel?
|       |   |
|       |   +-- YES
|       |   |   |
|       |   |   +-- cost_priority == true AND thickness_mm <= 3 AND avoid_oxygen == false?
|       |   |       |
|       |   |       +-- YES -> GAS = compressed_air
|       |   |       |         Reason: Thin stainless with cost priority can use air
|       |   |       |         with reasonable quality.
|       |   |       |
|       |   |       +-- NO  -> GAS = nitrogen
|       |   |                 Reason: Stainless usually requires oxidation-free,
|       |   |                 clean, weld-ready edges.
|       |
|       +-- NO
|           |
|           +-- material == galvanized_steel?
|           |   |
|           |   +-- YES
|           |   |   |
|           |   |   +-- thickness_mm <= 3?
|           |   |       |
|           |   |       +-- YES -> GAS = compressed_air
|           |   |       |         Reason: Thin galvanized steel can use air to
|           |   |       |         dilute zinc fumes and reduce cost.
|           |   |       |
|           |   |       +-- NO  -> GAS = nitrogen
|           |   |                 Reason: Thicker galvanized parts favor nitrogen
|           |   |                 to reduce zinc-oxide fumes and improve edges.
|           |
|           +-- NO
|               |
|               +-- material == aluminum?
|               |   |
|               |   +-- YES
|               |   |   |
|               |   |   +-- thickness_mm > 6?
|               |   |       |
|               |   |       +-- YES -> GAS = nitrogen
|               |   |       |         Reason: Thick aluminum needs high-pressure,
|               |   |       |         oxidation-free assist for melt ejection.
|               |   |       |
|               |   |       +-- NO  -> GAS = nitrogen
|               |   |                 Reason: Aluminum generally requires inert gas
|               |   |                 to prevent oxide formation and keep clean edges.
|               |
|               +-- NO -> GAS = nitrogen
|                         Reason: Fallback default (safest inert option).
```

## Compact Rule List

1. Carbon steel, `thickness_mm > 12`
- `avoid_oxygen=true` -> `nitrogen`
- `avoid_oxygen=false` -> `oxygen`

2. Carbon steel, `thickness_mm <= 3`
- `avoid_oxygen=true` and `cost_priority=true` -> `compressed_air`
- else if `edge_quality=high` -> `nitrogen`
- else if `cost_priority=true` -> `compressed_air`
- else -> `compressed_air`

3. Carbon steel, `3 < thickness_mm <= 12`
- `avoid_oxygen=true` -> `nitrogen`
- `avoid_oxygen=false` -> `oxygen`

4. Stainless steel
- `cost_priority=true` and `thickness_mm <= 3` and `avoid_oxygen=false` -> `compressed_air`
- else -> `nitrogen`

5. Galvanized steel
- `thickness_mm <= 3` -> `compressed_air`
- `thickness_mm > 3` -> `nitrogen`

6. Aluminum
- Always `nitrogen` (the code has separate messages for `> 6` and `<= 6`)

7. Any unknown material
- Default -> `nitrogen`

## Outcome Summary

- `oxygen` appears only in carbon steel paths where oxygen is not explicitly avoided.
- `compressed_air` appears mainly for thin sheets and/or cost-focused decisions.
- `nitrogen` is the dominant inert option for quality, anti-oxidation, and fallback safety.
