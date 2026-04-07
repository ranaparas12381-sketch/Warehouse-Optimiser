"""Task registry for warehouse OpenEnv."""

from .easy import make_env as make_easy_env
from .hard import make_env as make_hard_env
from .medium import make_env as make_medium_env

TASK_REGISTRY = {
    "easy": make_easy_env,
    "medium": make_medium_env,
    "hard": make_hard_env,
}

__all__ = ["TASK_REGISTRY", "make_easy_env", "make_medium_env", "make_hard_env"]
