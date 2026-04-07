"""Grader for medium task."""

from __future__ import annotations

from typing import Dict, List

from env.models import StepResult

from .base_grader import BaseGrader


class MediumGrader(BaseGrader):
    """Grade medium episodes with service and cost metrics."""

    def grade(self, episode_results: List[StepResult]) -> float:
        metrics = self.breakdown(episode_results)
        score = (
            0.5 * metrics["mean_fulfillment_rate"]
            + 0.3 * metrics["cost_efficiency"]
            + 0.2 * metrics["stockout_frequency_score"]
        )
        return max(0.0, min(1.0, score))

    def breakdown(self, episode_results: List[StepResult]) -> Dict[str, float]:
        if not episode_results:
            return {
                "mean_fulfillment_rate": 0.0,
                "cost_efficiency": 0.0,
                "stockout_frequency_score": 0.0,
                "actual_cost": 0.0,
                "worst_case_cost": 0.0,
            }

        total_steps = len(episode_results)
        mean_fulfillment = sum(float(step.info.get("fulfillment_rate", 0.0)) for step in episode_results) / total_steps

        actual_cost = sum(float(step.info.get("total_cost", 0.0)) for step in episode_results)
        peak_step_cost = max(float(step.info.get("total_cost", 0.0)) for step in episode_results)
        worst_case_cost = max(peak_step_cost * total_steps, 1.0)
        cost_efficiency = max(0.0, min(1.0, 1.0 - (actual_cost / worst_case_cost)))

        stockout_steps = sum(1 for step in episode_results if int(step.info.get("stockout_count", 0)) > 0)
        stockout_frequency_score = max(0.0, min(1.0, 1.0 - (stockout_steps / total_steps)))

        return {
            "mean_fulfillment_rate": float(mean_fulfillment),
            "cost_efficiency": float(cost_efficiency),
            "stockout_frequency_score": float(stockout_frequency_score),
            "actual_cost": float(actual_cost),
            "worst_case_cost": float(worst_case_cost),
        }
