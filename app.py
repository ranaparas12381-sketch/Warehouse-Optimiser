from __future__ import annotations

import sys
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent
WAREHOUSE_ROOT = PROJECT_ROOT / "warehouse_openenv"
if str(WAREHOUSE_ROOT) not in sys.path:
    sys.path.insert(0, str(WAREHOUSE_ROOT))

from env.models import ActionModel, ObservationModel  # noqa: E402
from env.warehouse_env import WarehouseEnv  # noqa: E402
from baseline.run_baseline import run_simulation  # noqa: E402
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


class SimulateRequest(BaseModel):
    task: str = Field(default="medium")
    seed: int = Field(default=42)
    episodes: int = Field(default=10)
    reward_weights: Optional[Dict[str, float]] = Field(default=None)


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


@app.get("/", response_class=HTMLResponse)
def root() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Warehouse Optimizer</title>
  <style>
    :root {
      --bg: #f4f7fb;
      --panel: #ffffff;
      --ink: #16202a;
      --muted: #5f6b76;
      --accent: #0b5ed7;
      --accent-2: #1f7a4d;
      --warn: #b7791f;
      --danger: #b42318;
      --line: #d6dde8;
      --surface: #eef4fb;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: "Segoe UI", Arial, sans-serif;
      background:
        radial-gradient(circle at top left, #dbeafe 0, transparent 28%),
        radial-gradient(circle at bottom right, #d1fae5 0, transparent 24%),
        var(--bg);
      color: var(--ink);
    }
    .wrap {
      max-width: 1180px;
      margin: 0 auto;
      padding: 32px 20px 56px;
    }
    .hero, .panel, .controls {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 18px;
      box-shadow: 0 10px 30px rgba(12, 23, 36, 0.06);
    }
    .hero {
      padding: 30px;
      margin-bottom: 18px;
      display: grid;
      grid-template-columns: 1.7fr 1fr;
      gap: 20px;
    }
    h1 {
      margin: 0 0 12px;
      font-size: 2.2rem;
      line-height: 1.1;
    }
    p {
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
      font-size: 1rem;
    }
    .status {
      display: inline-block;
      margin-bottom: 16px;
      padding: 8px 12px;
      border-radius: 999px;
      background: #e9f7ef;
      color: var(--accent-2);
      font-weight: 600;
      font-size: 0.92rem;
    }
    .hero-meta {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
      align-content: start;
    }
    .meta-card {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 14px;
    }
    .meta-label {
      font-size: 0.78rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 8px;
    }
    .meta-value {
      font-size: 1.05rem;
      font-weight: 700;
    }
    .layout {
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 18px;
      align-items: start;
    }
    .controls, .panel {
      padding: 22px;
    }
    h2 {
      margin: 0 0 12px;
      font-size: 1.05rem;
    }
    h3 {
      margin: 0 0 10px;
      font-size: 0.95rem;
    }
    ul {
      margin: 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.7;
    }
    code {
      background: #eef3f8;
      padding: 2px 6px;
      border-radius: 6px;
      font-family: Consolas, monospace;
      color: var(--accent);
    }
    label {
      display: block;
      font-size: 0.9rem;
      font-weight: 600;
      margin-bottom: 8px;
    }
    select, input {
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 0.95rem;
      margin-bottom: 14px;
      background: #fff;
    }
    button {
      width: 100%;
      border: none;
      border-radius: 12px;
      padding: 12px 14px;
      background: var(--accent);
      color: #fff;
      font-size: 0.96rem;
      font-weight: 700;
      cursor: pointer;
    }
    button:hover { filter: brightness(0.96); }
    button:disabled {
      opacity: 0.7;
      cursor: wait;
    }
    .stack {
      display: grid;
      gap: 18px;
    }
    .cards {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
    }
    .kpi {
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 16px;
    }
    .kpi-label {
      color: var(--muted);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 8px;
    }
    .kpi-value {
      font-size: 1.65rem;
      font-weight: 700;
    }
    .chart {
      display: grid;
      gap: 10px;
    }
    .bar-row {
      display: grid;
      grid-template-columns: 110px 1fr 64px;
      gap: 10px;
      align-items: center;
      font-size: 0.92rem;
    }
    .bar-track {
      width: 100%;
      height: 12px;
      background: #e7edf5;
      border-radius: 999px;
      overflow: hidden;
    }
    .bar-fill {
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent), #58a6ff);
    }
    .log {
      max-height: 360px;
      overflow: auto;
      background: #f8fafc;
      border: 1px solid var(--line);
      border-radius: 12px;
      padding: 14px;
      font-family: Consolas, monospace;
      font-size: 0.84rem;
      color: #314155;
    }
    .log-line {
      padding: 6px 0;
      border-bottom: 1px solid #e7edf5;
    }
    .subtle {
      color: var(--muted);
      font-size: 0.92rem;
    }
    .split {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }
    .badge {
      display: inline-block;
      padding: 4px 8px;
      border-radius: 999px;
      font-size: 0.8rem;
      font-weight: 700;
      background: #eef4fb;
      color: var(--accent);
      margin-right: 6px;
      margin-bottom: 6px;
    }
    .footer {
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.95rem;
    }
    @media (max-width: 900px) {
      .hero,
      .layout,
      .split,
      .cards {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div>
        <div class="status">Environment server online</div>
        <h1>Warehouse Optimizer</h1>
        <p>
          Interactive warehouse inventory optimization dashboard backed by the same OpenEnv-compatible
          API used for hackathon validation. Run a simulation, inspect task behavior, and review
          operational performance without losing the validator endpoints.
        </p>
      </div>
      <div class="hero-meta">
        <div class="meta-card">
          <div class="meta-label">Available Tasks</div>
          <div class="meta-value">easy, medium, hard</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">Deployment</div>
          <div class="meta-value">HTTP API + Dashboard</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">Validator Paths</div>
          <div class="meta-value">/reset /step /state</div>
        </div>
        <div class="meta-card">
          <div class="meta-label">Port</div>
          <div class="meta-value">7860</div>
        </div>
      </div>
    </section>

    <section class="layout">
      <aside class="controls">
        <h2>Simulation Controls</h2>
        <label for="task">Task difficulty</label>
        <select id="task">
          <option value="easy">Easy</option>
          <option value="medium" selected>Medium</option>
          <option value="hard">Hard</option>
        </select>

        <label for="seed">Random seed</label>
        <input id="seed" type="number" value="42" min="0" step="1" />

        <label for="episodes">Episodes</label>
        <input id="episodes" type="number" value="10" min="1" max="50" step="1" />

        <button id="runButton">Run Simulation</button>
        <div class="footer">The dashboard uses the same API routes consumed by the hackathon validator.</div>
      </aside>

      <main class="stack">
        <section class="panel">
          <h2>Overview</h2>
          <div class="cards">
            <div class="kpi">
              <div class="kpi-label">Task</div>
              <div class="kpi-value" id="kpiTask">Medium</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Episodes</div>
              <div class="kpi-value" id="kpiSteps">0</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Final Score</div>
              <div class="kpi-value" id="kpiReward">0.00</div>
            </div>
            <div class="kpi">
              <div class="kpi-label">Avg Fulfillment</div>
              <div class="kpi-value" id="kpiFulfillment">0%</div>
            </div>
          </div>
        </section>

        <section class="split">
          <section class="panel">
            <h2>Inventory Snapshot</h2>
            <div id="inventoryChart" class="chart">
              <div class="subtle">Run a simulation to populate inventory metrics.</div>
            </div>
          </section>
          <section class="panel">
            <h2>Current State</h2>
            <div id="stateBadges">
              <span class="badge">No active run</span>
            </div>
            <p class="subtle" id="stateText">The dashboard will summarize the latest environment state here.</p>
          </section>
        </section>

        <section class="panel">
          <h2>Episode Log</h2>
          <div id="log" class="log">
            <div class="log-line">Waiting for simulation run.</div>
          </div>
        </section>
      </main>
    </section>
  </div>
  <script>
    const runButton = document.getElementById("runButton");
    const taskInput = document.getElementById("task");
    const seedInput = document.getElementById("seed");
    const episodesInput = document.getElementById("episodes");
    const kpiTask = document.getElementById("kpiTask");
    const kpiSteps = document.getElementById("kpiSteps");
    const kpiReward = document.getElementById("kpiReward");
    const kpiFulfillment = document.getElementById("kpiFulfillment");
    const inventoryChart = document.getElementById("inventoryChart");
    const logEl = document.getElementById("log");
    const stateBadges = document.getElementById("stateBadges");
    const stateText = document.getElementById("stateText");

    function renderInventoryFromTrace(trace) {
      if (!trace.length) {
        inventoryChart.innerHTML = '<div class="subtle">No inventory data available.</div>';
        return;
      }
      const last = trace[trace.length - 1];
      const inventory = last.stock || [];
      const maxInventory = Math.max(...inventory, 1);
      const inventoryLevels = inventory.map(v => v / maxInventory);
      if (!inventoryLevels.length) {
        inventoryChart.innerHTML = '<div class="subtle">No inventory data available.</div>';
        return;
      }
      inventoryChart.innerHTML = inventoryLevels.map((value, index) => {
        const pct = Math.round(value * 100);
        return `
          <div class="bar-row">
            <div>SKU ${index + 1}</div>
            <div class="bar-track"><div class="bar-fill" style="width:${pct}%"></div></div>
            <div>${pct}%</div>
          </div>
        `;
      }).join("");
    }

    function renderState(task, results) {
      const trace = results.first_episode_trace || [];
      const steps = Number(results.episodes || 0);
      const avgFulfillment = trace.length
        ? trace.reduce((sum, row) => sum + Number(row.fulfillment_rate || 0), 0) / trace.length
        : 0;
      const last = trace.length ? trace[trace.length - 1] : null;

      kpiTask.textContent = task.charAt(0).toUpperCase() + task.slice(1);
      kpiSteps.textContent = String(steps);
      kpiReward.textContent = Number(results.score_mean || 0).toFixed(3);
      kpiFulfillment.textContent = `${(avgFulfillment * 100).toFixed(1)}%`;

      const badges = [];
      badges.push(`<span class="badge">trace length: ${trace.length}</span>`);
      badges.push(`<span class="badge">score std: ${Number(results.score_std || 0).toFixed(3)}</span>`);
      if (last) {
        badges.push(`<span class="badge">stockouts: ${Number(last.stockout_count || 0)}</span>`);
        badges.push(`<span class="badge">cost: ${Number(last.total_cost || 0).toFixed(2)}</span>`);
      }
      stateBadges.innerHTML = badges.join("");
      stateText.textContent = "Summary of the first episode trace returned by the simulation backend.";
      renderInventoryFromTrace(trace);
    }

    function appendLog(text) {
      const line = document.createElement("div");
      line.className = "log-line";
      line.textContent = text;
      logEl.prepend(line);
    }

    async function runSimulation() {
      runButton.disabled = true;
      runButton.textContent = "Running...";
      logEl.innerHTML = "";

      const task = taskInput.value;
      const seed = Number(seedInput.value || 42);
      const episodes = Number(episodesInput.value || 10);

      try {
        const response = await fetch("/simulate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ task, seed, episodes })
        });
        if (!response.ok) throw new Error("Simulation request failed.");
        const results = await response.json();

        renderState(task, results);
        logEl.innerHTML = "";
        const trace = results.first_episode_trace || [];
        if (!trace.length) {
          appendLog("Simulation completed with no trace rows.");
        } else {
          trace.slice().reverse().forEach((row) => {
            appendLog(
              `Step ${Number(row.step || 0)} | reward=${Number(row.reward || 0).toFixed(3)} ` +
              `| fulfillment=${(Number(row.fulfillment_rate || 0) * 100).toFixed(1)}% ` +
              `| stockouts=${Number(row.stockout_count || 0)}`
            );
          });
        }
      } catch (error) {
        appendLog(`Error: ${error.message}`);
      } finally {
        runButton.disabled = false;
        runButton.textContent = "Run Simulation";
      }
    }

    runButton.addEventListener("click", runSimulation);
  </script>
</body>
</html>
"""


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/simulate")
def simulate(request: Optional[SimulateRequest] = None) -> Dict[str, Any]:
    payload = request or SimulateRequest()
    task = payload.task.lower()
    if task not in TASK_FACTORIES:
        raise HTTPException(status_code=400, detail=f"Unsupported task '{task}'. Choose from easy, medium, hard.")
    return run_simulation(
        task=task,
        seed=int(payload.seed),
        episodes=int(payload.episodes),
        reward_weights=payload.reward_weights,
    )


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
