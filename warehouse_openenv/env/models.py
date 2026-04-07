"""Pydantic models for the warehouse optimization environment."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, model_validator


class SKUConfig(BaseModel):
    """Configuration for an individual SKU."""

    sku_id: str = Field(..., description="Unique SKU identifier")
    name: str = Field(..., description="Human-readable SKU name")
    unit_cost: float = Field(..., gt=0, description="Procurement cost per unit")
    holding_cost_rate: float = Field(
        ..., ge=0, le=1, description="Fraction of unit cost paid per day in holding cost"
    )
    stockout_penalty: float = Field(..., ge=0, description="Penalty per unit of unmet demand")
    max_stock: int = Field(..., gt=0, description="Maximum stock allowed for this SKU")
    reorder_point: int = Field(..., ge=0, description="Inventory threshold to trigger replenishment")
    supplier_lead_time_mean: float = Field(..., gt=0, description="Mean supplier lead time in days")
    supplier_lead_time_std: float = Field(..., ge=0, description="Stddev of supplier lead time in days")
    demand_mean: float = Field(..., ge=0, description="Average daily demand")
    demand_std: float = Field(..., ge=0, description="Demand noise level")
    seasonality_amplitude: float = Field(
        ..., ge=0, description="Amplitude for seasonal demand oscillation"
    )
    seasonality_period: int = Field(..., gt=0, description="Seasonality period in days")
    demand_trend: float = Field(
        default=0.0,
        description="Linear daily demand trend; positive means growing demand",
    )

    @model_validator(mode="after")
    def validate_reorder_point(self) -> "SKUConfig":
        """Ensure SKU thresholds are internally consistent."""
        if self.reorder_point > self.max_stock:
            raise ValueError("reorder_point must be <= max_stock")
        return self


class WarehouseConfig(BaseModel):
    """Global warehouse and episode configuration."""

    num_skus: int = Field(..., gt=0, description="Number of SKUs in simulation")
    warehouse_capacity: int = Field(..., gt=0, description="Total warehouse unit capacity")
    max_episode_steps: int = Field(..., gt=0, description="Episode horizon in days")
    task_difficulty: Literal["easy", "medium", "hard"] = Field(
        ..., description="Task difficulty level"
    )
    stochastic_demand: bool = Field(..., description="Whether demand includes stochasticity")
    stochastic_lead_times: bool = Field(..., description="Whether supplier lead times are stochastic")
    skus: List[SKUConfig] = Field(..., description="List of SKU configurations")
    reward_weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "w1": 0.4,
            "w2": 0.15,
            "w3": 0.25,
            "w4": 0.1,
            "w5": 0.05,
            "w6": 0.05,
        },
        description="Reward shaping weights",
    )
    discount_factor: float = Field(
        default=0.99,
        gt=0,
        le=1,
        description="Discount factor used for hard-task long-horizon scoring",
    )
    emergency_supply_enabled: bool = Field(
        default=False,
        description="Whether emergency one-day replenishment can be triggered",
    )
    emergency_supply_cost_multiplier: float = Field(
        default=2.0,
        ge=1.0,
        description="Cost multiplier for emergency replenishment",
    )
    disruption_probability: float = Field(
        default=0.0,
        ge=0,
        le=1,
        description="Probability of supplier disruption on a given day",
    )

    @model_validator(mode="after")
    def validate_skus(self) -> "WarehouseConfig":
        """Validate SKU list against declared counts."""
        if len(self.skus) != self.num_skus:
            raise ValueError("len(skus) must match num_skus")
        return self


class ObservationModel(BaseModel):
    """Agent-visible state observation."""

    time_step: int = Field(..., ge=0, description="Current time step")
    inventory_levels: List[float] = Field(
        ..., description="Current stock per SKU normalized to [0, 1]"
    )
    pipeline_inventory: List[float] = Field(
        ..., description="On-order stock per SKU normalized to [0, 1]"
    )
    demand_forecast: List[float] = Field(
        ..., description="Forecasted next-step demand per SKU normalized to [0, 1]"
    )
    days_since_last_order: List[int] = Field(
        ..., description="Number of days since last replenishment order per SKU"
    )
    capacity_utilization: float = Field(
        ..., ge=0, description="Fraction of total warehouse capacity currently occupied"
    )


class ActionModel(BaseModel):
    """Action input to environment."""

    order_quantities: List[int] = Field(
        ..., description="Units to order per SKU, with 0 meaning no order"
    )


class StepResult(BaseModel):
    """Output of one environment transition."""

    observation: ObservationModel
    reward: float
    done: bool
    info: Dict[str, Any] = Field(
        ...,
        description=(
            "Diagnostics including fulfillment_rate, total_cost, stockout_count, "
            "holding_cost, order_cost, capacity_violation"
        ),
    )


class FullStateModel(BaseModel):
    """Complete internal environment state for debugging and analysis."""

    config: WarehouseConfig
    current_inventory: List[int]
    pipeline_orders: List[List[int]] = Field(
        ..., description="pipeline_orders[sku][t] gives units arriving at global step t"
    )
    demand_history: List[List[float]]
    reward_history: List[float]
    time_step: int
    cumulative_reward: float
    disruptions: Optional[List[bool]] = Field(
        default=None,
        description="Boolean timeline indicating whether disruption happened per step",
    )
