"""Reusable UI components for warehouse operations dashboard."""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


COLORS = {
    "background": "#F8F9FA",
    "surface": "#FFFFFF",
    "surface_alt": "#E9ECEF",
    "accent_primary": "#0B5ED7",
    "accent_success": "#198754",
    "accent_warning": "#FFC107",
    "accent_danger": "#DC3545",
    "text_primary": "#212529",
    "text_secondary": "#6C757D",
    "grid_lines": "#DEE2E6",
}

NEON_SERIES = [
    "#0B5ED7",
    "#198754",
    "#FD7E14",
    "#DC3545",
    "#6F42C1",
    "#0DCAF0",
    "#20C997",
    "#D63384",
    "#495057",
    "#FFC107",
]

X_AXIS_TIME_STEP = "Time Step"
Y_AXIS_UNITS = "Units"
TABLE_COLUMNS = ["SKU ID", "Name", "Avg Stock", "Fulfillment %", "Stockout Days", "Cost"]
FULFILLMENT_COLUMN = "Fulfillment %"


def inject_global_css() -> None:
    """Apply professional light theme across Streamlit app."""
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Roboto+Mono:wght@400;500&display=swap');

:root {{
  --background: {COLORS['background']};
  --surface: {COLORS['surface']};
  --surface-alt: {COLORS['surface_alt']};
  --accent-primary: {COLORS['accent_primary']};
  --accent-success: {COLORS['accent_success']};
  --accent-warning: {COLORS['accent_warning']};
  --accent-danger: {COLORS['accent_danger']};
  --text-primary: {COLORS['text_primary']};
  --text-secondary: {COLORS['text_secondary']};
  --grid-lines: {COLORS['grid_lines']};
}}

html, body, [class*="css"], .stApp {{
  background: var(--background);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}

section[data-testid="stSidebar"] {{
  background: var(--surface);
  border-right: 2px solid var(--grid-lines);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}}

section[data-testid="stSidebar"] * {{
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}}

div[data-testid="stMetric"] {{
  background: var(--surface);
}}

.stButton > button {{
  background: var(--accent-primary);
  color: #FFFFFF;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  width: 100%;
  padding: 0.75rem 1.5rem;
  transition: all 0.2s ease;
}}

.stButton > button:hover {{
  background: #0a58ca;
  box-shadow: 0 4px 12px rgba(11, 94, 215, 0.3);
}}

div[data-testid="stExpander"] {{
  background: var(--surface);
  border: 1px solid var(--grid-lines);
  border-radius: 8px;
}}

div[data-testid="stDataFrame"] {{
  background: var(--surface);
  border: 1px solid var(--grid-lines);
  border-radius: 8px;
}}

.block-container {{
  padding-top: 2rem;
  padding-bottom: 2rem;
  max-width: 100%;
}}

.kpi-card {{
  background: var(--surface);
  border-radius: 8px;
  padding: 1.25rem;
  border: 1px solid var(--grid-lines);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
  min-height: 130px;
  transition: all 0.2s ease;
}}

.kpi-card:hover {{
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}}

.kpi-label {{
  font-size: 0.75rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
  font-weight: 600;
}}

.kpi-value {{
  font-size: 2.25rem;
  font-weight: 700;
  line-height: 1.2;
}}

.log-panel {{
  background: #F8F9FA;
  border: 1px solid var(--grid-lines);
  border-radius: 8px;
  padding: 1rem;
  font-family: 'Roboto Mono', 'Courier New', monospace;
  font-size: 0.75rem;
  max-height: 480px;
  overflow-y: auto;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
}}

.log-line {{
  margin-bottom: 8px;
  padding: 4px 0;
  border-bottom: 1px solid #E9ECEF;
}}

h1, h2, h3 {{
  color: var(--text-primary);
  font-weight: 700;
}}

h2 {{
  font-size: 1.5rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--grid-lines);
}}

#MainMenu, footer, header {{
  visibility: hidden;
}}
</style>
""",
        unsafe_allow_html=True,
    )


def render_kpi_card(label: str, value: str, accent_color: str) -> None:
    """Render a custom KPI card."""
    st.markdown(
        f"""
<div class="kpi-card" style="border-top: 3px solid {accent_color};">
  <div class="kpi-label">{label}</div>
  <div class="kpi-value" style="color:{accent_color};">{value}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def _common_layout(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=COLORS["surface"],
        plot_bgcolor=COLORS["background"],
        font={"color": COLORS["text_primary"], "family": "Inter, sans-serif", "size": 12},
        legend={
            "bgcolor": COLORS["surface"],
            "bordercolor": COLORS["grid_lines"],
            "borderwidth": 1,
            "font": {"color": COLORS["text_primary"], "size": 11},
        },
        margin={"l": 40, "r": 30, "t": 50, "b": 40},
        hoverlabel={"bgcolor": COLORS["surface"], "font": {"color": COLORS["text_primary"]}},
    )
    fig.update_xaxes(
        color=COLORS["text_secondary"],
        gridcolor=COLORS["grid_lines"],
        zeroline=True,
        zerolinecolor=COLORS["grid_lines"],
        showline=True,
        linecolor=COLORS["grid_lines"],
    )
    fig.update_yaxes(
        color=COLORS["text_secondary"],
        gridcolor=COLORS["grid_lines"],
        zeroline=True,
        zerolinecolor=COLORS["grid_lines"],
        showline=True,
        linecolor=COLORS["grid_lines"],
    )
    return fig


def build_inventory_chart(trace: List[Dict[str, Any]], sku_count: int) -> go.Figure:
    """Build line chart for per-SKU inventory over time."""
    fig = go.Figure()
    x = [row["step"] for row in trace]

    for sku_idx in range(sku_count):
        y = [row["stock"][sku_idx] if sku_idx < len(row["stock"]) else 0 for row in trace]
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines+markers",
                name=f"SKU {sku_idx + 1}",
                line={"width": 2.5, "color": NEON_SERIES[sku_idx % len(NEON_SERIES)]},
                marker={"size": 6},
            )
        )

    fig.update_layout(
        title={"text": "Inventory Levels Over Time", "font": {"size": 16, "color": COLORS["text_primary"]}},
        xaxis_title=X_AXIS_TIME_STEP,
        yaxis_title=Y_AXIS_UNITS,
    )
    return _common_layout(fig)


def build_demand_fulfillment_chart(trace: List[Dict[str, Any]]) -> go.Figure:
    """Build demand vs fulfillment dual-line chart with gap highlighting."""
    x = [row["step"] for row in trace]
    demand = [float(np.sum(row.get("demand", []))) for row in trace]
    fulfilled = [float(np.sum(row.get("fulfilled", []))) for row in trace]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=demand,
            mode="lines+markers",
            name="Demand",
            line={"color": COLORS["accent_warning"], "width": 2.5},
            marker={"size": 6},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=fulfilled,
            mode="lines+markers",
            name="Fulfillment",
            line={"color": COLORS["accent_success"], "width": 2.5},
            marker={"size": 6},
            fill="tonexty",
            fillcolor="rgba(220, 53, 69, 0.15)",
        )
    )

    fig.update_layout(
        title={"text": "Demand vs Fulfillment", "font": {"size": 16, "color": COLORS["text_primary"]}},
        xaxis_title=X_AXIS_TIME_STEP,
        yaxis_title=Y_AXIS_UNITS,
    )
    return _common_layout(fig)


def build_reward_chart(trace: List[Dict[str, Any]]) -> go.Figure:
    """Build cumulative reward area chart."""
    x = [row["step"] for row in trace]
    rewards = [row["reward"] for row in trace]
    cumulative = np.cumsum(rewards)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=x,
            y=cumulative,
            mode="lines+markers",
            line={"color": COLORS["accent_primary"], "width": 3},
            marker={"size": 6},
            fill="tozeroy",
            fillcolor="rgba(11, 94, 215, 0.15)",
            name="Cumulative Reward",
        )
    )
    fig.add_hline(y=0.0, line_dash="dash", line_color=COLORS["text_secondary"], line_width=1.5)

    fig.update_layout(
        title={"text": "Cumulative Reward Over Time", "font": {"size": 16, "color": COLORS["text_primary"]}},
        xaxis_title=X_AXIS_TIME_STEP,
        yaxis_title="Reward",
    )
    return _common_layout(fig)


def build_sku_table(trace: List[Dict[str, Any]], sku_configs: List[Dict[str, Any]]) -> pd.DataFrame:
    """Aggregate per-SKU operational KPIs into a table."""
    rows: List[Dict[str, Any]] = []
    if not trace:
        return pd.DataFrame(columns=TABLE_COLUMNS)

    for sku_idx, sku in enumerate(sku_configs):
        stocks = [row["stock"][sku_idx] if sku_idx < len(row["stock"]) else 0 for row in trace]
        demand = [row["demand"][sku_idx] if sku_idx < len(row["demand"]) else 0 for row in trace]
        fulfilled = [row["fulfilled"][sku_idx] if sku_idx < len(row["fulfilled"]) else 0 for row in trace]

        demand_total = float(np.sum(demand))
        fulfilled_total = float(np.sum(fulfilled))
        fulfillment_pct = 100.0 if demand_total <= 0 else (fulfilled_total / demand_total) * 100.0
        stockout_days = sum(1 for d, f in zip(demand, fulfilled) if d > f)

        unit_cost = float(sku.get("unit_cost", 0.0))
        holding_rate = float(sku.get("holding_cost_rate", 0.0))
        estimated_cost = float(np.mean(stocks) * unit_cost * holding_rate * len(trace))

        rows.append(
            {
                "SKU ID": sku.get("sku_id", f"SKU-{sku_idx + 1}"),
                "Name": sku.get("name", "Unknown"),
                "Avg Stock": round(float(np.mean(stocks)), 2),
                FULFILLMENT_COLUMN: round(fulfillment_pct, 2),
                "Stockout Days": stockout_days,
                "Cost": round(estimated_cost, 2),
            }
        )

    return pd.DataFrame(rows)


def style_sku_table(df: pd.DataFrame) -> pd.io.formats.style.Styler:
    """Apply dark industrial styling and fulfillment heat coloring."""

    def color_fulfillment(value: float) -> str:
        if value > 90:
            return f"color: {COLORS['accent_success']}; font-weight: 700;"
        if value >= 70:
            return f"color: {COLORS['accent_warning']}; font-weight: 700;"
        return f"color: {COLORS['accent_danger']}; font-weight: 700;"

    base = {
        "background-color": COLORS["surface"],
        "color": COLORS["text_primary"],
        "font-size": "0.85rem",
    }

    styled = df.style.map(color_fulfillment, subset=[FULFILLMENT_COLUMN]).set_properties(**base)

    styled = styled.set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("background-color", COLORS["surface_alt"]),
                    ("color", COLORS["text_primary"]),
                    ("border", f"1px solid {COLORS['grid_lines']}"),
                    ("font-size", "0.85rem"),
                ],
            },
            {
                "selector": "td",
                "props": [
                    ("border", f"1px solid {COLORS['grid_lines']}"),
                ],
            },
            {
                "selector": "tr:nth-child(even)",
                "props": [("background-color", COLORS["surface_alt"])],
            },
        ]
    )
    return styled


def render_episode_log(trace: List[Dict[str, Any]]) -> None:
    """Render a scrollable, color-coded episode log."""
    lines: List[str] = []
    for row in trace:
        reward = float(row.get("reward", 0.0))
        if reward > 0.2:
            color = COLORS["accent_success"]
        elif reward >= -0.1:
            color = COLORS["accent_warning"]
        else:
            color = COLORS["accent_danger"]

        text = (
            f"[Step {row.get('step', 0):02d}] reward: {reward:+.2f} | "
            f"stock: {row.get('stock', [])} | demand: {row.get('demand', [])}"
        )
        lines.append(f"<div class='log-line' style='color:{color};'>{text}</div>")

    html = "".join(lines) if lines else "<div class='log-line'>No episode data yet.</div>"
    st.markdown(f"<div class='log-panel'>{html}</div>", unsafe_allow_html=True)
