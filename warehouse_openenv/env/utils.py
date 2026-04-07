"""Utility helpers for warehouse simulation."""

from __future__ import annotations

import math
from typing import Iterable, List

import numpy as np


EPSILON = 1e-9


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp a float to a closed interval."""
    return max(min_value, min(max_value, value))


def safe_divide(numerator: float, denominator: float) -> float:
    """Perform division with protection against zero denominators."""
    if abs(denominator) < EPSILON:
        return 0.0
    return numerator / denominator


def to_unit_interval(value: float, scale: float) -> float:
    """Map non-negative value into [0, 1] using bounded rational transform."""
    if scale <= 0:
        return 0.0
    clipped = max(0.0, value)
    return clipped / (clipped + scale)


def to_signed_unit(value_0_1: float) -> float:
    """Map [0, 1] value into [-1, 1]."""
    bounded = clamp(value_0_1, 0.0, 1.0)
    return 2.0 * bounded - 1.0


def seasonal_multiplier(step: int, amplitude: float, period: int) -> float:
    """Return multiplicative seasonal factor with mean 1.0."""
    if period <= 0:
        return 1.0
    return 1.0 + amplitude * math.sin(2.0 * math.pi * (step % period) / period)


def moving_average(values: Iterable[float], window: int) -> float:
    """Compute trailing moving average for baseline heuristics."""
    values_list = list(values)
    if not values_list:
        return 0.0
    if window <= 0:
        return float(np.mean(values_list))
    tail = values_list[-window:]
    return float(np.mean(tail))


def normalize_vector(values: List[float], scales: List[float]) -> List[float]:
    """Normalize vector values by corresponding scales into [0, 1]."""
    normalized: List[float] = []
    for value, scale in zip(values, scales):
        if scale <= 0:
            normalized.append(0.0)
        else:
            normalized.append(clamp(value / scale, 0.0, 1.0))
    return normalized
