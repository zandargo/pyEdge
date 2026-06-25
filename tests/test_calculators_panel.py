import json
from pathlib import Path

from ui.components.calculators_panel import (
    _SCORE_MAX,
    _SCORE_MIN,
    _score_bar_color,
    _thickness_range,
    score_assist_gas,
)


def test_score_bar_color_uses_current_range():
    assert _score_bar_color(205, 201, 205) == "#00ff00"
    assert _score_bar_color(201, 201, 205) == "#ff0000"
    assert _score_bar_color(203, 201, 205) == "#7f7f00"
    assert _score_bar_color(400, 400, 500) == "#ff0000"
    assert _score_bar_color(425, 400, 500) == "#bf3f00"


def test_thickness_range_displays_mm():
    assert _thickness_range(3.0) == "3.00 mm"
    assert _thickness_range(12.345) == "12.35 mm"


def test_score_assist_gas_applies_compatibility_and_weights():
    scores, breakdown, disallowed = score_assist_gas(
        "carbon_steel", 2.0, "high", "welding", False
    )

    assert scores["compressed_air"] == 0.0
    assert scores["oxygen"] == 0.0
    assert scores["nitrogen"] == 125.0

    assert breakdown["material"] == {"oxygen": 1.0, "nitrogen": 1.0, "compressed_air": 0.0}
    assert breakdown["thickness"] == {"oxygen": 1.0, "nitrogen": 1.0, "compressed_air": 0.0}
    assert "compressed_air" in disallowed
    assert "oxygen" not in disallowed
    assert "nitrogen" not in disallowed


def test_score_assist_gas_reports_disallowed_gas_for_material():
    _, _, disallowed = score_assist_gas("aluminum", 2.0, "medium", "none", True)

    assert "oxygen" in disallowed
