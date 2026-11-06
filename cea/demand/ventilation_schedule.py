"""Selectable ventilation requirements for occupancy schedule generation."""
import numpy as np


def ventilation_schedule(people, rate_per_person, floor_area, mode="people", area_rate=0.35):
    """Calculate the outdoor-air requirement without changing occupancy or heat gains.

    Formula
    -------
    People mode: Q(t) = N(t) × qₚ. Area mode: Q(t) = A × qₐ.
    Area mode is constant, including hours without occupants. These are prescribed
    modelling inputs, not an implementation of a ventilation compliance standard.

    Parameters
    ----------
    people : array-like
        Scheduled occupants at each time step [persons].
    rate_per_person : float
        Outdoor-air requirement per person [L/s/person].
    floor_area : float
        Conditioned floor area Af [m²], used only in area mode.
    mode : str
        Either people or area [-].
    area_rate : float
        Prescribed outdoor-air requirement per conditioned area [L/s/m²].

    Returns
    -------
    numpy.ndarray
        Outdoor-air requirement for each time step [L/s]. Demand can subtract
        infiltration downstream, depending on its configuration.
    """
    people = np.asarray(people)
    if mode == "people":
        return people * rate_per_person
    if mode != "area":
        raise ValueError(f"Unknown ventilation mode: {mode!r}; choose people or area")
    if not np.isfinite(area_rate) or area_rate < 0:
        raise ValueError("ventilation-area-rate-lpsm2 must be finite and non-negative")
    if not np.isfinite(floor_area) or floor_area < 0:
        raise ValueError("Conditioned floor area Af must be finite and non-negative")
    return np.full(people.shape, floor_area * area_rate, dtype=float)
