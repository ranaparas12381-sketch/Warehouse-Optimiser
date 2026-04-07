"""Reward computation for warehouse optimization environment."""

from __future__ import annotations

from typing import Dict

from .models import WarehouseConfig
from .utils import clamp, safe_divide, to_signed_unit, to_unit_interval


DEFAULT_SCALE_MULTIPLIER = 0.25


def _resolve_weights(config: WarehouseConfig) -> Dict[str, float]:
    """Merge user-defined weights with defaults."""
    defaults = {
        "w1": 0.4,
        "w2": 0.15,
        "w3": 0.25,
        "w4": 0.1,
        "w5": 0.05,
        "w6": 0.05,
    }
    merged = {**defaults, **(config.reward_weights or {})}
    total = sum(max(v, 0.0) for v in merged.values())
    if total <= 0:
        return defaults
    return {key: value / total for key, value in merged.items()}


def compute_reward(step_data: dict, config: WarehouseConfig) -> float:
    """
    Compute shaped reward using normalized weighted components.

    Components are converted to signed values in [-1, 1] before weighting.
    Positive components (fulfillment, efficiency) increase reward while cost
    components reduce reward through subtraction.
    """
    weights = _resolve_weights(config)

    fulfillment_rate = clamp(step_data.get("fulfillment_rate", 0.0), 0.0, 1.0)
    fulfillment_reward = to_signed_unit(fulfillment_rate)

    demand_total = max(float(step_data.get("demand_total", 0.0)), 1.0)
    average_unit_cost = max(float(step_data.get("average_unit_cost", 1.0)), 1.0)
    cost_scale = demand_total * average_unit_cost * DEFAULT_SCALE_MULTIPLIER

    holding_cost = max(float(step_data.get("holding_cost", 0.0)), 0.0)
    stockout_cost = max(float(step_data.get("stockout_cost", 0.0)), 0.0)
    order_cost = max(float(step_data.get("order_cost", 0.0)), 0.0)
    capacity_violation = max(float(step_data.get("capacity_violation", 0.0)), 0.0)

    normalized_holding_cost = to_signed_unit(to_unit_interval(holding_cost, cost_scale))
    normalized_stockout_cost = to_signed_unit(to_unit_interval(stockout_cost, cost_scale))
    normalized_order_cost = to_signed_unit(to_unit_interval(order_cost, cost_scale))

    total_capacity = float(config.warehouse_capacity)
    capacity_violation_ratio = safe_divide(capacity_violation, total_capacity)
    capacity_violation_penalty = to_signed_unit(clamp(capacity_violation_ratio, 0.0, 1.0))

    optimality_score = clamp(step_data.get("inventory_efficiency", 0.0), 0.0, 1.0)
    efficiency_bonus = to_signed_unit(optimality_score)

    reward = (
        weights["w1"] * fulfillment_reward
        - weights["w2"] * normalized_holding_cost
        - weights["w3"] * normalized_stockout_cost
        - weights["w4"] * normalized_order_cost
        - weights["w5"] * capacity_violation_penalty
        + weights["w6"] * efficiency_bonus
    )

    return float(clamp(reward, -1.0, 1.0))
