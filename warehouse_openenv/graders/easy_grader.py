"""Grader for easy task."""

from __future__ import annotations

from typing import Dict, List

from env.models import StepResult

from .base_grader import BaseGrader


class EasyGrader(BaseGrader):
    """Grade easy episodes by fulfillment and stockout avoidance."""

    def grade(self, episode_results: List[StepResult]) -> float:
        metrics = self.breakdown(episode_results)
        raw_score = metrics["avg_fulfillment_rate"] - metrics["stockout_penalty"]
        return max(0.0, min(1.0, raw_score))

    def breakdown(self, episode_results: List[StepResult]) -> Dict[str, float]:
        if not episode_results:
            return {
                "avg_fulfillment_rate": 0.0,
                "stockout_events": 0.0,
                "stockout_penalty": 0.0,
            }

        fulfillment = [float(step.info.get("fulfillment_rate", 0.0)) for step in episode_results]
        stockout_events = sum(1 for step in episode_results if int(step.info.get("stockout_count", 0)) > 0)
        penalty = 0.1 * stockout_events

        return {
            "avg_fulfillment_rate": float(sum(fulfillment) / len(fulfillment)),
            "stockout_events": float(stockout_events),
            "stockout_penalty": float(penalty),
        }
