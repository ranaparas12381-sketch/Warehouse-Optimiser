"""Task grader registry."""

from .easy_grader import EasyGrader
from .hard_grader import HardGrader
from .medium_grader import MediumGrader

GRADER_REGISTRY = {
    "easy": EasyGrader,
    "medium": MediumGrader,
    "hard": HardGrader,
}

__all__ = ["EasyGrader", "MediumGrader", "HardGrader", "GRADER_REGISTRY"]
