"""Quick algorithm verification — no Qt deps."""

def select_assist_gas(material, thickness_mm, edge_quality, post_process, cost_priority):
    avoid_oxygen = post_process in ("welding", "painting")
    if material == "carbon_steel":
        if thickness_mm > 12:
            if avoid_oxygen:
                return "nitrogen"
            return "oxygen"
        if thickness_mm <= 3:
            if avoid_oxygen and cost_priority:
                return "compressed_air"
            if edge_quality == "high":
                return "nitrogen"
            if cost_priority:
                return "compressed_air"
            return "compressed_air"
        if avoid_oxygen:
            return "nitrogen"
        return "oxygen"
    if material == "stainless_steel":
        if cost_priority and thickness_mm <= 3 and not avoid_oxygen:
            return "compressed_air"
        return "nitrogen"
    if material == "galvanized_steel":
        if thickness_mm <= 3:
            return "compressed_air"
        return "nitrogen"
    if material == "aluminum":
        return "nitrogen"
    return "nitrogen"

cases = [
    ("carbon_steel", 10, "medium", "none", False, "oxygen"),
    ("stainless_steel", 2, "high", "welding", False, "nitrogen"),
    ("carbon_steel", 2, "low", "none", True, "compressed_air"),
    ("carbon_steel", 15, "low", "none", False, "oxygen"),
    ("carbon_steel", 15, "low", "welding", False, "nitrogen"),
    ("stainless_steel", 2, "high", "none", True, "compressed_air"),
    ("galvanized_steel", 2, "low", "none", False, "compressed_air"),
    ("galvanized_steel", 5, "low", "none", False, "nitrogen"),
    ("aluminum", 3, "high", "none", False, "nitrogen"),
]

passed = 0
for mat, thick, eq, pp, cp, expected in cases:
    result = select_assist_gas(mat, thick, eq, pp, cp)
    status = "PASS" if result == expected else "FAIL"
    if status == "PASS":
        passed += 1
    print(f"{status}: {mat} {thick}mm pp={pp} cost={cp} -> {result} (expected {expected})")

print(f"\n{passed}/{len(cases)} passed")
