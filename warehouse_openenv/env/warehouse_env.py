"""Core OpenEnv-compatible warehouse simulation environment."""

from __future__ import annotations

from typing import Dict, List, Optional

import numpy as np

from .models import (
    ActionModel,
    FullStateModel,
    ObservationModel,
    SKUConfig,
    StepResult,
    WarehouseConfig,
)
from .reward import compute_reward
from .utils import clamp, normalize_vector, safe_divide, seasonal_multiplier


MIN_LEAD_TIME_DAYS = 1
MAX_LEAD_TIME_DAYS = 30
PIPELINE_PADDING_DAYS = 90


class WarehouseEnv:
    """Industrial-grade multi-SKU warehouse inventory simulation."""

    def __init__(self, config: WarehouseConfig):
        self.config = config
        self.rng = np.random.default_rng(42)
        self.time_step = 0
        self.cumulative_reward = 0.0
        self.current_inventory: List[int] = []
        self.pipeline_orders: List[List[int]] = []
        self.demand_history: List[List[float]] = []
        self.reward_history: List[float] = []
        self.days_since_last_order: List[int] = []
        self.disruptions: List[bool] = []

        max_expected_lead = max(
            int(np.ceil(s.supplier_lead_time_mean + 4 * s.supplier_lead_time_std)) for s in self.config.skus
        )
        self.pipeline_horizon = self.config.max_episode_steps + max_expected_lead + PIPELINE_PADDING_DAYS

    def reset(self, seed: int = None) -> ObservationModel:
        """
        Reset the environment to initial state.
        If seed is provided, set numpy random seed for reproducibility.
        """
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        self.time_step = 0
        self.cumulative_reward = 0.0
        self.reward_history = []
        self.disruptions = []
        self.demand_history = [[] for _ in range(self.config.num_skus)]

        self.current_inventory = []
        for sku in self.config.skus:
            if self.config.task_difficulty == "easy":
                initial = max(sku.reorder_point, int(0.6 * sku.max_stock))
            elif self.config.task_difficulty == "medium":
                initial = int(clamp(0.55 * sku.max_stock, 0, sku.max_stock))
            else:
                initial = int(clamp(0.45 * sku.max_stock, 0, sku.max_stock))
            self.current_inventory.append(initial)

        self.pipeline_orders = [[0 for _ in range(self.pipeline_horizon)] for _ in range(self.config.num_skus)]
        self.days_since_last_order = [0 for _ in range(self.config.num_skus)]

        return self._build_observation()

    def step(self, action: ActionModel) -> StepResult:
        """
        Execute one time step and return transition data.

        Process order:
          1. Receive pending deliveries
          2. Generate stochastic demand
          3. Fulfill demand
          4. Place new orders
          5. Apply costs
          6. Advance time
          7. Compute reward
          8. Check terminal condition
        """
        self._validate_action(action)
        self._receive_pending_deliveries()

        demand = self._generate_demand(self.time_step)
        self._record_demand(demand)

        fulfilled, unmet, stockout_count = self._fulfill_demand(demand)
        order_summary = self._place_orders(action, unmet)
        cost_summary = self._compute_step_costs(unmet)

        demand_total = float(sum(demand))
        fulfilled_total = float(sum(fulfilled))
        fulfillment_rate = 1.0 if demand_total <= 0 else fulfilled_total / demand_total
        average_unit_cost = float(np.mean([sku.unit_cost for sku in self.config.skus]))

        step_data: Dict[str, float] = {
            "fulfillment_rate": fulfillment_rate,
            "holding_cost": cost_summary["holding_cost"],
            "stockout_cost": cost_summary["stockout_cost"],
            "order_cost": order_summary["order_cost"],
            "capacity_violation": cost_summary["capacity_violation"],
            "demand_total": demand_total,
            "average_unit_cost": average_unit_cost,
            "inventory_efficiency": cost_summary["inventory_efficiency"],
        }

        reward = float(fulfillment_rate) if self.config.task_difficulty == "easy" else compute_reward(step_data, self.config)
        total_cost = cost_summary["holding_cost"] + cost_summary["stockout_cost"] + order_summary["order_cost"]

        self.cumulative_reward += reward
        self.reward_history.append(reward)
        self.time_step += 1

        done = self.time_step >= self.config.max_episode_steps
        info = {
            "fulfillment_rate": fulfillment_rate,
            "total_cost": total_cost,
            "stockout_count": stockout_count,
            "holding_cost": cost_summary["holding_cost"],
            "order_cost": order_summary["order_cost"],
            "stockout_cost": cost_summary["stockout_cost"],
            "capacity_violation": cost_summary["capacity_violation"],
            "demand": demand,
            "fulfilled": fulfilled,
            "unmet": unmet,
            "inventory": list(self.current_inventory),
            "orders": order_summary["order_quantities"],
            "time_step": self.time_step,
            "disrupted": order_summary["disrupted"],
            "emergency_qty": order_summary["emergency_qty_total"],
            "inventory_efficiency": cost_summary["inventory_efficiency"],
            "discounted_reward": reward * (self.config.discount_factor ** max(self.time_step - 1, 0)),
        }

        return StepResult(observation=self._build_observation(), reward=reward, done=done, info=info)

    def _receive_pending_deliveries(self) -> None:
        for sku_idx in range(self.config.num_skus):
            incoming = self.pipeline_orders[sku_idx][self.time_step]
            if incoming > 0:
                self.current_inventory[sku_idx] += incoming

    def _record_demand(self, demand: List[int]) -> None:
        for sku_idx, value in enumerate(demand):
            self.demand_history[sku_idx].append(float(value))

    def _fulfill_demand(self, demand: List[int]) -> tuple[List[int], List[int], int]:
        fulfilled: List[int] = []
        unmet: List[int] = []
        stockout_count = 0

        for sku_idx, demand_qty in enumerate(demand):
            available = self.current_inventory[sku_idx]
            sold = min(available, demand_qty)
            shortage = max(0, demand_qty - sold)
            fulfilled.append(sold)
            unmet.append(shortage)
            self.current_inventory[sku_idx] = available - sold
            if shortage > 0:
                stockout_count += 1

        return fulfilled, unmet, stockout_count

    def _place_orders(self, action: ActionModel, unmet: List[int]) -> Dict[str, object]:
        order_cost = 0.0
        order_quantities = [max(0, int(qty)) for qty in action.order_quantities]

        disrupted = self._draw_disruption()
        self.disruptions.append(disrupted)

        for sku_idx, order_qty in enumerate(order_quantities):
            if order_qty <= 0:
                self.days_since_last_order[sku_idx] += 1
                continue

            lead_time = self._sample_lead_time(self.config.skus[sku_idx], disrupted)
            arrival_step = min(self.time_step + lead_time, self.pipeline_horizon - 1)
            self.pipeline_orders[sku_idx][arrival_step] += order_qty
            self.days_since_last_order[sku_idx] = 0
            order_cost += order_qty * self.config.skus[sku_idx].unit_cost

        emergency_qty_total = 0
        emergency_cost = 0.0
        if self.config.emergency_supply_enabled and any(value > 0 for value in unmet):
            for sku_idx, shortage in enumerate(unmet):
                if shortage <= 0:
                    continue
                arrival_step = min(self.time_step + 1, self.pipeline_horizon - 1)
                self.pipeline_orders[sku_idx][arrival_step] += shortage
                emergency_qty_total += shortage
                emergency_cost += (
                    shortage
                    * self.config.skus[sku_idx].unit_cost
                    * self.config.emergency_supply_cost_multiplier
                )

        order_cost += emergency_cost
        return {
            "order_cost": order_cost,
            "order_quantities": order_quantities,
            "disrupted": disrupted,
            "emergency_qty_total": emergency_qty_total,
        }

    def _compute_step_costs(self, unmet: List[int]) -> Dict[str, float]:
        holding_cost = 0.0
        stockout_cost = 0.0
        inventory_efficiency_scores: List[float] = []

        for sku_idx, sku in enumerate(self.config.skus):
            holding_cost += self.current_inventory[sku_idx] * sku.unit_cost * sku.holding_cost_rate
            stockout_cost += unmet[sku_idx] * sku.stockout_penalty

            target_stock = 0.5 * (sku.reorder_point + sku.max_stock)
            normalized_deviation = safe_divide(
                abs(self.current_inventory[sku_idx] - target_stock),
                max(target_stock, 1.0),
            )
            inventory_efficiency_scores.append(clamp(1.0 - normalized_deviation, 0.0, 1.0))

        capacity_violation = float(max(0, sum(self.current_inventory) - self.config.warehouse_capacity))
        inventory_efficiency = float(np.mean(inventory_efficiency_scores)) if inventory_efficiency_scores else 0.0
        return {
            "holding_cost": holding_cost,
            "stockout_cost": stockout_cost,
            "capacity_violation": capacity_violation,
            "inventory_efficiency": inventory_efficiency,
        }

    def state(self) -> FullStateModel:
        """Return complete internal environment state for diagnostics."""
        return FullStateModel(
            config=self.config,
            current_inventory=list(self.current_inventory),
            pipeline_orders=[list(schedule) for schedule in self.pipeline_orders],
            demand_history=[list(history) for history in self.demand_history],
            reward_history=list(self.reward_history),
            time_step=self.time_step,
            cumulative_reward=self.cumulative_reward,
            disruptions=list(self.disruptions),
        )

    def _validate_action(self, action: ActionModel) -> None:
        if len(action.order_quantities) != self.config.num_skus:
            raise ValueError(
                f"Action length {len(action.order_quantities)} does not match num_skus={self.config.num_skus}"
            )
        if any(quantity < 0 for quantity in action.order_quantities):
            raise ValueError("Action contains negative order quantity")

    def _build_observation(self) -> ObservationModel:
        max_stocks = [float(sku.max_stock) for sku in self.config.skus]
        inventory_levels = normalize_vector([float(v) for v in self.current_inventory], max_stocks)

        future_pipeline = []
        for sku_idx in range(self.config.num_skus):
            start = self.time_step
            end = min(self.pipeline_horizon, self.time_step + 7)
            future_pipeline.append(float(sum(self.pipeline_orders[sku_idx][start:end])))
        pipeline_inventory = normalize_vector(future_pipeline, max_stocks)

        forecast = self._forecast_demand_step(self.time_step + 1)
        demand_forecast = normalize_vector(
            [float(value) for value in forecast],
            [max(1.0, sku.max_stock * 0.5) for sku in self.config.skus],
        )

        capacity_utilization = safe_divide(sum(self.current_inventory), self.config.warehouse_capacity)

        return ObservationModel(
            time_step=self.time_step,
            inventory_levels=inventory_levels,
            pipeline_inventory=pipeline_inventory,
            demand_forecast=demand_forecast,
            days_since_last_order=list(self.days_since_last_order),
            capacity_utilization=float(capacity_utilization),
        )

    def _forecast_demand_step(self, step_index: int) -> List[int]:
        forecast: List[int] = []
        for sku in self.config.skus:
            base = sku.demand_mean + sku.demand_trend * step_index
            seasonal = seasonal_multiplier(step_index, sku.seasonality_amplitude, sku.seasonality_period)
            forecasted = max(0.0, base * seasonal)
            forecast.append(int(round(forecasted)))
        return forecast

    def _generate_demand(self, step_index: int) -> List[int]:
        demand: List[int] = []
        for sku in self.config.skus:
            base = sku.demand_mean + sku.demand_trend * step_index
            base = max(0.1, base)
            seasonal = seasonal_multiplier(step_index, sku.seasonality_amplitude, sku.seasonality_period)
            expected = max(0.1, base * seasonal)

            if self.config.stochastic_demand:
                poisson_draw = self.rng.poisson(expected)
                gaussian_noise = self.rng.normal(0.0, sku.demand_std)
                demand_qty = int(round(max(0.0, poisson_draw + gaussian_noise)))
            else:
                demand_qty = int(round(expected))

            if self.config.task_difficulty == "hard":
                # Model periodic promotions and sudden demand shocks.
                if (step_index + 1) % 14 == 0:
                    demand_qty = int(round(demand_qty * 1.5))
                if self.rng.uniform() < 0.05:
                    demand_qty = int(round(demand_qty * self.rng.uniform(1.8, 2.5)))

            demand.append(max(0, demand_qty))
        return demand

    def _sample_lead_time(self, sku: SKUConfig, disrupted: bool) -> int:
        if not self.config.stochastic_lead_times:
            lead_time = int(round(sku.supplier_lead_time_mean))
        else:
            sampled = self.rng.normal(sku.supplier_lead_time_mean, sku.supplier_lead_time_std)
            lead_time = int(round(sampled))

        lead_time = max(MIN_LEAD_TIME_DAYS, min(MAX_LEAD_TIME_DAYS, lead_time))

        if disrupted:
            multiplier = int(self.rng.integers(1, 4))
            lead_time = min(MAX_LEAD_TIME_DAYS, lead_time * multiplier)

        return lead_time

    def _draw_disruption(self) -> bool:
        if self.config.disruption_probability <= 0:
            return False
        return bool(self.rng.uniform() < self.config.disruption_probability)
