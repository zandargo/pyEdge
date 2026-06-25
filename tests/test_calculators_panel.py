import json
from pathlib import Path

from ui.components.calculators_panel import _SCORE_MAX, _SCORE_MIN, _score_bar_color, _thickness_range


def test_score_bar_color_uses_current_range():
    assert _score_bar_color(205, 201, 205) == "#00ff00"
    assert _score_bar_color(201, 201, 205) == "#ff0000"
    assert _score_bar_color(203, 201, 205) == "#7f7f00"
    assert _score_bar_color(400, 400, 500) == "#ff0000"
    assert _score_bar_color(425, 400, 500) == "#bf3f00"


def test_thickness_range_matches_gas_scoring_json():
    rules_path = Path(__file__).parent.parent / "ref" / "gasScoring.json"
    scoring = json.loads(rules_path.read_text(encoding="utf-8"))
    thickness_rules = scoring["rules"]["thickness"]

    test_values = {
        0.5: "<=1.9",
        1.9: "<=1.9",
        2.0: "2-6",
        3.5: "2-6",
        8.0: "8-12.7",
        12.7: "8-12.7",
        13.0: ">12.7",
        50.0: ">12.7",
    }

    for thickness, expected_key in test_values.items():
        assert _thickness_range(thickness) == expected_key

    # Ensure all JSON bucket keys are covered by at least one test input.
    seen_keys = {expected for expected in test_values.values()}
    assert seen_keys == set(thickness_rules)
