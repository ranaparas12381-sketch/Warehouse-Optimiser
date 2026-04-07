"""Base grader interface for warehouse tasks."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List

from env.models import StepResult


class BaseGrader(ABC):
    """Abstract grader contract."""

    @abstractmethod
    def grade(self, episode_results: List[StepResult]) -> float:
        """Return normalized scalar score in [0.0, 1.0]."""

    @abstractmethod
    def breakdown(self, episode_results: List[StepResult]) -> Dict[str, float]:
        """Return per-metric diagnostic values."""
