---
title: Warehouse Optimizer
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# Warehouse Optimizer

Warehouse Optimizer is an OpenEnv-compatible warehouse inventory environment designed for evaluating replenishment strategies across deterministic, stochastic, and disruption-aware operating conditions.

The project combines a production-style simulation engine, a validator-compatible HTTP environment server, a baseline inference client, and a polished public-facing demo experience.

## Why This Project

Warehouse replenishment is a sequential decision problem with competing objectives:

- maintain service levels
- avoid stockouts
- control holding costs
- manage warehouse capacity
- respond to uncertainty in demand and supplier lead times

This repository packages that problem as a reusable environment that can be deployed, validated, and interacted with consistently across local development, Hugging Face Spaces, and external clients.

## Key Capabilities

- Multi-SKU warehouse simulation with configurable task difficulty
- Stochastic demand and lead-time behavior for non-trivial planning scenarios
- Disruption-aware hard mode with more realistic operational stress
- OpenEnv-compatible HTTP endpoints for reset, step, and state transitions
- Baseline client for quick interaction and debugging
- Root deployment packaging for multi-mode validation
- Separate simulation modules, tasks, graders, and dashboard assets for clean organization

## Demo and Deployment Targets

- GitHub repository: `https://github.com/ranaparas12381-sketch/Warehouse-Optimizer`
- Hugging Face Space: `https://huggingface.co/spaces/ParasRana/Warehouse_optimizer`
- Render dashboard: `https://warehouse-optimization-see0.onrender.com`

## Repository Structure

- `app.py`: root FastAPI/OpenEnv server
- `inference.py`: baseline client for HTTP interaction
- `openenv.yaml`: OpenEnv manifest
- `pyproject.toml`: project metadata and entry points
- `uv.lock`: locked dependency graph
- `server/app.py`: callable server entry point for validation
- `warehouse_openenv/env`: core simulation engine and models
- `warehouse_openenv/tasks`: task configurations
- `warehouse_openenv/graders`: evaluation logic
- `warehouse_openenv/baseline`: baseline simulation helpers
- `warehouse_openenv/dashboard`: dashboard assets retained for local visualization
- `Dockerfile`: root container entrypoint
- `render.yaml`: Render deployment blueprint

## Task Modes

- `easy`
  Single-SKU deterministic replenishment with simpler inventory dynamics.
- `medium`
  Multi-SKU stochastic replenishment with variability in demand and lead times.
- `hard`
  Disruption-aware warehouse optimization with tighter planning pressure.

## Runtime Interface

The environment server exposes the standard operational routes used by OpenEnv-style workflows:

- `GET /health`
- `POST /reset`
- `POST /step`
- `GET /state`
- `POST /state`

Example reset payload:

```json
{
  "task": "medium",
  "seed": 42
}
```

Example step payload:

```json
{
  "session_id": "<session-id>",
  "order_quantities": [10, 0, 5, 0, 2]
}
```

## Local Development

### Option 1: `uv`

```bash
uv sync
uv run server
```

### Option 2: `pip`

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

Run the baseline client:

```bash
python inference.py --base-url http://127.0.0.1:7860 --task medium --seed 42
```

## Docker

Build the container:

```bash
docker build -t warehouse-optimizer .
```

Run the container:

```bash
docker run -p 7860:7860 warehouse-optimizer
```

## Deployment Notes

### Hugging Face Spaces

The repository is configured as a Docker Space and serves the environment on port `7860`.

### Render

The repository also contains a Render blueprint in [render.yaml](render.yaml). The Render deployment uses the Streamlit-oriented Dockerfile under `warehouse_openenv/`.

## Project Design

This repo intentionally separates concerns:

- root-level files handle deployment, validation, and external integration
- `warehouse_openenv/env` contains the reusable simulation engine
- task modules define scenario complexity
- graders and baseline logic make evaluation reproducible

That split keeps the project suitable both for hackathon submission and for future extension.

## Submission Readiness

The repository includes the root artifacts commonly required for deployment and validation workflows:

- `Dockerfile`
- `inference.py`
- `openenv.yaml`
- `pyproject.toml`
- `uv.lock`
- `server/app.py`

## Contributing

Contribution guidance is available in [CONTRIBUTING.md](CONTRIBUTING.md).

## Security

Security reporting guidance is available in [SECURITY.md](SECURITY.md).
