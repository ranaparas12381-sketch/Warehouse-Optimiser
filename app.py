from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent
WAREHOUSE_ROOT = PROJECT_ROOT / "warehouse_openenv"
if str(WAREHOUSE_ROOT) not in sys.path:
    sys.path.insert(0, str(WAREHOUSE_ROOT))

from env.models import ActionModel, ObservationModel  # noqa: E402
from env.warehouse_env import WarehouseEnv  # noqa: E402
from tasks.easy import make_config as make_easy_config  # noqa: E402
from tasks.hard import make_config as make_hard_config  # noqa: E402
from tasks.medium import make_config as make_medium_config  # noqa: E402


TASK_FACTORIES = {
    "easy": make_easy_config,
    "medium": make_medium_config,
    "hard": make_hard_config,
}


class ResetRequest(BaseModel):
    task: str = Field(default="medium")
    seed: Optional[int] = Field(default=None)


class StepRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)
    action: Optional[Dict[str, Any] | list[int]] = Field(default=None)
    order_quantities: Optional[list[int]] = Field(default=None)


class StateRequest(BaseModel):
    session_id: Optional[str] = Field(default=None)


class EnvSession:
    def __init__(self, env: WarehouseEnv, task: str):
        self.env = env
        self.task = task


app = FastAPI(title="Warehouse Optimization OpenEnv Server", version="1.0.0")
SESSIONS: Dict[str, EnvSession] = {}
DEFAULT_SESSION_ID = "default"


def _build_env(task: str) -> WarehouseEnv:
    normalized = task.lower()
    if normalized not in TASK_FACTORIES:
        raise HTTPException(status_code=400, detail=f"Unsupported task '{task}'. Choose from easy, medium, hard.")
    return WarehouseEnv(TASK_FACTORIES[normalized]())


def _serialize_observation(observation: ObservationModel) -> Dict[str, Any]:
    return observation.model_dump()


def _serialize_state(env: WarehouseEnv, session_id: str, task: str) -> Dict[str, Any]:
    state = env.state().model_dump()
    return {
        "session_id": session_id,
        "task": task,
        "state": state,
    }


def _resolve_session(session_id: Optional[str]) -> tuple[str, EnvSession]:
    resolved = session_id or DEFAULT_SESSION_ID
    session = SESSIONS.get(resolved)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found. Call /reset first.")
    return resolved, session


def _coerce_action(request: StepRequest, env: WarehouseEnv) -> ActionModel:
    if request.order_quantities is not None:
        return ActionModel(order_quantities=request.order_quantities)

    payload = request.action
    if isinstance(payload, list):
        return ActionModel(order_quantities=payload)
    if isinstance(payload, dict):
        if "order_quantities" in payload:
            return ActionModel(order_quantities=list(payload["order_quantities"]))
        if "actions" in payload:
            return ActionModel(order_quantities=list(payload["actions"]))

    return ActionModel(order_quantities=[0] * env.config.num_skus)


async def _read_json(request: Request) -> Dict[str, Any]:
    try:
        body = await request.json()
    except Exception:
        return {}
    return body if isinstance(body, dict) else {}


@app.get("/")
def root() -> Dict[str, Any]:
    return {
        "name": "warehouse-inventory-optimization",
        "status": "ok",
        "available_tasks": list(TASK_FACTORIES.keys()),
        "endpoints": ["/health", "/reset", "/step", "/state"],
    }


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/reset")
async def reset(request: Request) -> Dict[str, Any]:
    body = await _read_json(request)
    payload = ResetRequest(
        task=body.get("task") or body.get("task_id") or body.get("difficulty") or "medium",
        seed=body.get("seed"),
    )
    task = payload.task.lower()
    env = _build_env(task)
    observation = env.reset(seed=payload.seed)
    session_id = str(uuid.uuid4())
    session = EnvSession(env=env, task=task)
    SESSIONS[session_id] = session
    SESSIONS[DEFAULT_SESSION_ID] = session

    return {
        "session_id": session_id,
        "task": task,
        "observation": _serialize_observation(observation),
        "reward": 0.0,
        "done": False,
        "info": {
            "message": "Environment reset successful.",
            "max_episode_steps": env.config.max_episode_steps,
            "num_skus": env.config.num_skus,
        },
    }


@app.post("/step")
async def step(request: Request) -> Dict[str, Any]:
    body = await _read_json(request)
    payload = StepRequest(
        session_id=body.get("session_id") or body.get("episode_id"),
        action=body.get("action") or body.get("actions"),
        order_quantities=body.get("order_quantities"),
    )
    session_id, session = _resolve_session(payload.session_id)
    action = _coerce_action(payload, session.env)
    result = session.env.step(action)

    return {
        "session_id": session_id,
        "task": session.task,
        "observation": _serialize_observation(result.observation),
        "reward": result.reward,
        "done": result.done,
        "info": result.info,
    }


@app.get("/state")
def state(session_id: Optional[str] = None) -> Dict[str, Any]:
    resolved_session_id, session = _resolve_session(session_id)
    return _serialize_state(session.env, resolved_session_id, session.task)


@app.post("/state")
async def state_post(request: Request) -> Dict[str, Any]:
    body = await _read_json(request)
    payload = StateRequest(session_id=body.get("session_id") or body.get("episode_id"))
    resolved_session_id, session = _resolve_session(payload.session_id)
    return _serialize_state(session.env, resolved_session_id, session.task)
