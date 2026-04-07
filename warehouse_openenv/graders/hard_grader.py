"""Grader for hard task."""

from __future__ import annotations

from typing import Dict, List

from env.models import StepResult

from .base_grader import BaseGrader


class HardGrader(BaseGrader):
    """Grade hard episodes for long-horizon operational excellence."""

    def grade(self, episode_results: List[StepResult]) -> float:
        metrics = self.breakdown(episode_results)
        score = (
            0.4 * metrics["discounted_reward_score"]
            + 0.3 * metrics["service_level_score"]
            + 0.2 * metrics["inventory_turnover_efficiency"]
            + 0.1 * metrics["disruption_handling_score"]
        )
        return max(0.0, min(1.0, score))

    def breakdown(self, episode_results: List[StepResult]) -> Dict[str, float]:
        if not episode_results:
            return {
                "discounted_reward_score": 0.0,
                "service_level_score": 0.0,
                "inventory_turnover_efficiency": 0.0,
                "disruption_handling_score": 0.0,
                "discounted_reward": 0.0,
                "theoretical_max_reward": 0.0,
            }

        total_steps = len(episode_results)

        discounted_reward = sum(float(step.info.get("discounted_reward", 0.0)) for step in episode_results)
        theoretical_max_reward = sum(1.0 for _ in episode_results)
        discounted_reward_score = max(0.0, min(1.0, discounted_reward / max(theoretical_max_reward, 1.0)))

        high_service_steps = sum(
            1 for step in episode_results if float(step.info.get("fulfillment_rate", 0.0)) >= 0.95
        )
        service_level_score = high_service_steps / total_steps

        demand_total = sum(float(sum(step.info.get("demand", []))) for step in episode_results)
        avg_inventory = sum(float(sum(step.info.get("inventory", []))) for step in episode_results) / total_steps
        raw_turnover = demand_total / max(avg_inventory, 1.0)
        inventory_turnover_efficiency = max(0.0, min(1.0, raw_turnover / 4.0))

        disrupted_steps = [step for step in episode_results if bool(step.info.get("disrupted", False))]
        if disrupted_steps:
            disruption_fulfillment = sum(float(step.info.get("fulfillment_rate", 0.0)) for step in disrupted_steps)
            disruption_handling_score = max(0.0, min(1.0, disruption_fulfillment / len(disrupted_steps)))
        else:
            disruption_handling_score = 1.0

        return {
            "discounted_reward_score": float(discounted_reward_score),
            "service_level_score": float(service_level_score),
            "inventory_turnover_efficiency": float(inventory_turnover_efficiency),
            "disruption_handling_score": float(disruption_handling_score),
            "discounted_reward": float(discounted_reward),
            "theoretical_max_reward": float(theoretical_max_reward),
        }
