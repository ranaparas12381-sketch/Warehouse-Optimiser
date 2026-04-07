# Contributing

Thank you for contributing to Warehouse Optimizer.

## Development Scope

High-value contributions include:

- simulation improvements in `warehouse_openenv/env`
- new task variants in `warehouse_openenv/tasks`
- better evaluation logic in `warehouse_openenv/graders`
- improved baseline policies in `warehouse_openenv/baseline`
- documentation and deployment reliability improvements at the repo root

## Local Setup

### Using `uv`

```bash
uv sync
```

### Using `pip`

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
uv run server
```

Or:

```bash
uvicorn app:app --host 0.0.0.0 --port 7860
```

## Running the Baseline Client

```bash
python inference.py --base-url http://127.0.0.1:7860 --task medium --seed 42
```

## Before Opening a Pull Request

Please make sure your change:

- fits the current repository structure
- keeps the environment endpoints working
- does not break deployment packaging
- updates documentation when behavior changes

## Coding Expectations

- Follow normal Python style conventions.
- Use clear names and keep public functions documented.
- Preserve the separation between root deployment files and simulation logic under `warehouse_openenv/`.
- Prefer small, reviewable commits over broad unrelated changes.

## Pull Request Notes

A useful pull request includes:

- a short problem statement
- the implementation summary
- any deployment or validation impact
- testing notes

## Documentation

If you change:

- API behavior
- deployment flow
- project structure

update the relevant root documentation in the same pull request.
