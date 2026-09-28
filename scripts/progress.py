"""Elapsed time and ETA while place-and-route runs."""

import statistics

PHASES = ("xst", "ngdbuild", "map", "par", "bitgen")


def median_or_seed(samples, seed):
    if samples:
        return statistics.median(samples)
    return seed


def format_status(board, phase, elapsed_s, eta_s, over_budget=False):
    """One line for the terminal and for progress.md."""
    line = f"{board}  {phase}  {elapsed_s:.0f}s elapsed  eta {eta_s:.0f}s"
    if over_budget:
        line += "  over budget"
    return line


def estimate(seeds, history, phase, elapsed_in_phase):
    """Return eta_s and over_budget for the phase in progress.

    history maps a phase name to a list of earlier durations in seconds.
    When the current phase has already passed its median, eta is the overrun
    plus the medians of the phases that have not started.
    """
    if phase not in PHASES:
        raise KeyError(phase)
    medians = {name: median_or_seed(history.get(name) or [], seeds[name]) for name in PHASES}
    index = PHASES.index(phase)
    later = sum(medians[name] for name in PHASES[index + 1 :])
    budget = medians[phase]
    if elapsed_in_phase > budget:
        return (elapsed_in_phase - budget) + later, True
    return (budget - elapsed_in_phase) + later, False
