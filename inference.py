from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any, Dict, List

import requests


@dataclass
class WarehousePolicy:
    """Simple threshold policy for the OpenEnv warehouse server."""

    def act(self, observation: Dict[str, Any]) -> List[int]:
        inventory_levels = observation.get("inventory_levels", [])
        demand_forecast = observation.get("demand_forecast", [])
        if not inventory_levels:
            return []

        actions: List[int] = []
        for stock_ratio, forecast_ratio in zip(inventory_levels, demand_forecast):
            if stock_ratio < 0.35:
                actions.append(max(1, int(round(20 * max(forecast_ratio, 0.25)))))
            elif stock_ratio < 0.55:
                actions.append(int(round(8 * max(forecast_ratio, 0.2))))
            else:
                actions.append(0)
        return actions


def _emit_block(tag: str, payload: Dict[str, Any]) -> None:
    print(f"[{tag}] {json.dumps(payload, separators=(',', ':'))}", flush=True)


def run_episode(base_url: str, task: str, seed: int) -> Dict[str, Any]:
    policy = WarehousePolicy()
    reset_response = requests.post(
        f"{base_url.rstrip('/')}/reset",
        json={"task": task, "seed": seed},
        timeout=30,
    )
    reset_response.raise_for_status()
    payload = reset_response.json()
    session_id = payload["session_id"]
    observation = payload["observation"]
    reset_info = payload.get("info", {})

    total_reward = 0.0
    steps = 0
    done = False

    _emit_block(
        "START",
        {
            "task": task,
            "seed": seed,
            "session_id": session_id,
            "max_episode_steps": reset_info.get("max_episode_steps"),
            "num_skus": reset_info.get("num_skus"),
            "observation": observation,
        },
    )

    while not done:
        actions = policy.act(observation)
        step_response = requests.post(
            f"{base_url.rstrip('/')}/step",
            json={"session_id": session_id, "order_quantities": actions},
            timeout=30,
        )
        step_response.raise_for_status()
        payload = step_response.json()
        observation = payload["observation"]
        reward = float(payload.get("reward", 0.0))
        total_reward += reward
        done = bool(payload.get("done", False))
        steps += 1
        info = payload.get("info", {})

        _emit_block(
            "STEP",
            {
                "step": steps,
                "reward": reward,
                "done": done,
                "action": actions,
                "observation": observation,
                "info": {
                    "fulfillment_rate": info.get("fulfillment_rate"),
                    "total_cost": info.get("total_cost"),
                    "stockout_count": info.get("stockout_count"),
                    "inventory": info.get("inventory"),
                    "demand": info.get("demand"),
                    "fulfilled": info.get("fulfilled"),
                },
            },
        )

    result = {"task": task, "seed": seed, "steps": steps, "total_reward": total_reward}
    _emit_block("END", result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a baseline policy against the warehouse OpenEnv server.")
    parser.add_argument("--base-url", default="http://127.0.0.1:7860", help="Base URL of the environment server")
    parser.add_argument("--task", default="medium", choices=["easy", "medium", "hard"])
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    run_episode(args.base_url, args.task, args.seed)


if __name__ == "__main__":
    main()
