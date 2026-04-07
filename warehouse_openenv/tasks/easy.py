"""Easy task: single SKU deterministic control."""

from __future__ import annotations

from env.models import SKUConfig, WarehouseConfig
from env.warehouse_env import WarehouseEnv


TASK_NAME = "single_sku_deterministic"


def make_config() -> WarehouseConfig:
    """Build easy deterministic task configuration."""
    sku = SKUConfig(
        sku_id="SKU-001",
        name="Standard Tote Bin",
        unit_cost=18.0,
        holding_cost_rate=0.004,
        stockout_penalty=2.0,
        max_stock=120,
        reorder_point=40,
        supplier_lead_time_mean=1.0,
        supplier_lead_time_std=0.0,
        demand_mean=18.0,
        demand_std=0.0,
        seasonality_amplitude=0.0,
        seasonality_period=7,
        demand_trend=0.0,
    )

    return WarehouseConfig(
        num_skus=1,
        warehouse_capacity=140,
        max_episode_steps=15,
        task_difficulty="easy",
        stochastic_demand=False,
        stochastic_lead_times=False,
        skus=[sku],
        reward_weights={"w1": 1.0, "w2": 0.0, "w3": 0.0, "w4": 0.0, "w5": 0.0, "w6": 0.0},
        discount_factor=1.0,
        emergency_supply_enabled=False,
        disruption_probability=0.0,
    )


def make_env() -> WarehouseEnv:
    """Instantiate easy task environment."""
    return WarehouseEnv(make_config())
