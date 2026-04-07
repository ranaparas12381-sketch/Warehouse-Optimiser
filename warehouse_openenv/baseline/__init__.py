"""Baseline package for heuristic policies."""

__all__ = ["run_simulation"]


def run_simulation(*args, **kwargs):
	"""Lazy proxy to avoid eager module import side effects."""
	from .run_baseline import run_simulation as _run_simulation

	return _run_simulation(*args, **kwargs)
