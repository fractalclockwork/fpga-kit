from progress import estimate, format_status


SEEDS = {"xst": 10, "ngdbuild": 10, "map": 10, "par": 50, "bitgen": 5}


def test_eta_uses_seed_until_history_exists():
    eta, over = estimate(SEEDS, {}, "par", 10)
    assert eta == 45
    assert over is False


def test_over_budget_adds_overrun_and_later_phases():
    eta, over = estimate(SEEDS, {}, "par", 70)
    assert over is True
    assert eta == 25


def test_history_median_replaces_seed():
    eta, over = estimate(SEEDS, {"par": [10, 30]}, "par", 0)
    assert eta == 25
    assert over is False


def test_status_line_names_the_phase():
    assert format_status("nexys3", "map", 16.2, 21.4) == "nexys3  map  16s elapsed  eta 21s"
    assert format_status("nexys3", "par", 70, 25, over_budget=True).endswith("  over budget")
