"""Medium task: multi-SKU stochastic inventory planning."""

from __future__ import annotations

from env.models import SKUConfig, WarehouseConfig
from env.warehouse_env import WarehouseEnv


TASK_NAME = "multi_sku_stochastic"


MEDIUM_SKUS = [
    SKUConfig(
        sku_id="SKU-101",
        name="Phone Charger",
        unit_cost=12.0,
        holding_cost_rate=0.006,
        stockout_penalty=10.0,
        max_stock=220,
        reorder_point=90,
        supplier_lead_time_mean=3.0,
        supplier_lead_time_std=1.0,
        demand_mean=48.0,
        demand_std=6.0,
        seasonality_amplitude=0.08,
        seasonality_period=7,
        demand_trend=0.08,
    ),
    SKUConfig(
        sku_id="SKU-102",
        name="Laptop Sleeve",
        unit_cost=16.0,
        holding_cost_rate=0.005,
        stockout_penalty=11.0,
        max_stock=180,
        reorder_point=70,
        supplier_lead_time_mean=3.0,
        supplier_lead_time_std=1.0,
        demand_mean=33.0,
        demand_std=5.5,
        seasonality_amplitude=0.12,
        seasonality_period=14,
        demand_trend=0.04,
    ),
    SKUConfig(
        sku_id="SKU-103",
        name="Packing Tape",
        unit_cost=7.5,
        holding_cost_rate=0.004,
        stockout_penalty=8.5,
        max_stock=280,
        reorder_point=120,
        supplier_lead_time_mean=3.0,
        supplier_lead_time_std=1.0,
        demand_mean=72.0,
        demand_std=9.0,
        seasonality_amplitude=0.05,
        seasonality_period=7,
        demand_trend=0.02,
    ),
    SKUConfig(
        sku_id="SKU-104",
        name="Barcode Labels",
        unit_cost=5.0,
        holding_cost_rate=0.003,
        stockout_penalty=7.0,
        max_stock=260,
        reorder_point=100,
        supplier_lead_time_mean=3.0,
        supplier_lead_time_std=1.0,
        demand_mean=60.0,
        demand_std=8.0,
        seasonality_amplitude=0.06,
        seasonality_period=10,
        demand_trend=0.03,
    ),
    SKUConfig(
        sku_id="SKU-105",
        name="Wireless Mouse",
        unit_cost=24.0,
        holding_cost_rate=0.007,
        stockout_penalty=14.0,
        max_stock=140,
        reorder_point=60,
        supplier_lead_time_mean=3.0,
        supplier_lead_time_std=1.0,
        demand_mean=22.0,
        demand_std=4.0,
        seasonality_amplitude=0.1,
        seasonality_period=14,
        demand_trend=0.05,
    ),
]


def make_config() -> WarehouseConfig:
    """Build medium stochastic task configuration."""
    return WarehouseConfig(
        num_skus=5,
        warehouse_capacity=650,
        max_episode_steps=30,
        task_difficulty="medium",
        stochastic_demand=True,
        stochastic_lead_times=True,
        skus=MEDIUM_SKUS,
        reward_weights={"w1": 0.4, "w2": 0.15, "w3": 0.25, "w4": 0.1, "w5": 0.05, "w6": 0.05},
        discount_factor=0.99,
        emergency_supply_enabled=False,
        disruption_probability=0.0,
    )


def make_env() -> WarehouseEnv:
    """Instantiate medium task environment."""
    return WarehouseEnv(make_config())
