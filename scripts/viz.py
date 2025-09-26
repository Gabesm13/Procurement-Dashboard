#!/usr/bin/env python3
"""
viz.py – Build Procurement Dashboard HTML
"""

from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# --- layout sizes (px) -------------------------------------------------------
KPI_W, KPI_H = 520, 250
BAR_W, BAR_H = 1000, 450
PIE_W, PIE_H = 520, 450
ROI_W, ROI_H = 1600, 350

PLOT_CONFIG = dict(
    responsive=False,
    displayModeBar=True,
    displaylogo=False,
)

# -----------------------------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------------------------
def load_data(project_root: Path | None = None):
    if project_root is None:
        project_root = Path(__file__).resolve().parent
    d = project_root / "data"
    kpi_s   = pd.read_json(d / "procurement_kpis.json", typ="series")
    sav_df  = pd.read_csv(d / "savings_by_department.csv")
    mon_df  = pd.read_csv(d / "monthly_savings_by_department.csv")
    roi_df  = pd.read_csv(d / "procurement_roi.csv")
    fcst_df = pd.read_csv(d / "procurement_forecast.csv")
    return kpi_s, sav_df, mon_df, roi_df, fcst_df


# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def fmtd(val) -> str:
    return f"${int(val):,}"

def fmtd_signed(val) -> str:
    """Currency w/ sign: -$21,172 style."""
    sign = "-" if val < 0 else ""
    return f"{sign}${abs(int(val)):,}"

def back_calc_previous(current: float, pct_change: float) -> float:
    denom = 1 + pct_change / 100.0
    return current / denom if denom else current


# -----------------------------------------------------------------------------
# GENERATE KPI DONUT FIGURES
# -----------------------------------------------------------------------------
def make_kpi_donut(title: str, current: float, pct_change: float, prev: float) -> go.Figure:
    """Single KPI donut (value in center; delta shown in card below; clean hover text)."""
    remainder = abs(prev - current)
    if remainder == 0:
        remainder = max(current * 0.05, 1)

    # Signed month-over-month change
    delta_val = current - prev
    verb = "reduction" if delta_val < 0 else "increase"

    hover_text = [
        f"{fmtd(current)} current",
        f"{fmtd_signed(delta_val)}<br>{verb} vs<br>last month"
    ]

    pie_trace = go.Pie(
        labels=["Current", "Delta"],
        values=[current, remainder],
        hole=0.7,
        sort=False,
        direction="clockwise",
        marker=dict(
            colors=["rgba(114,186,255,0.6)", "rgba(225,225,225,0.6)"],
            line=dict(color="darkgrey", width=1)
        ),
        showlegend=False,
        textinfo="none",
        # use our custom strings; no default trace info
        customdata=hover_text,
        hovertemplate="%{customdata}<extra></extra>",
        domain=dict(x=[0, 1], y=[0, 1])
    )

    fig = go.Figure(pie_trace)

    fig.add_annotation(
        text=f"<b>{fmtd(current)}</b>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=20, color="black")
    )

    fig.update_layout(
        autosize=False,
        width=KPI_W,
        height=KPI_H,
        title=dict(
            text=f"<b>{title}</b>",
            x=0.5, xanchor="center",
            y=0.98, yanchor="top",
            font=dict(size=18, color="black")
        ),
        margin=dict(l=10, r=10, t=50, b=30),
        template="plotly_white",
        paper_bgcolor="white",
        plot_bgcolor="white",
        uniformtext_minsize=12,
        uniformtext_mode="hide"
    )
    return fig


# -----------------------------------------------------------------------------
# GENERATE MONTHLY STACKED BAR CHART
# -----------------------------------------------------------------------------

def make_monthly_stacked(monthly_df: pd.DataFrame) -> go.Figure:
    order = [
        "Mar 2022", "Apr 2022", "May 2022", "Jun 2022", "Jul 2022",
        "Aug 2022", "Sep 2022", "Oct 2022", "Nov 2022", "Dec 2022",
        "Jan 2023", "Feb 2023", "Mar 2023",
    ]
    df = monthly_df.copy()
    df["MonthYear"] = pd.Categorical(df["MonthYear"], categories=order, ordered=True)
    df.sort_values("MonthYear", inplace=True)

    dept_order = ["Batteries", "Forklift", "Machine", "Other", "Sensors", "Transmissions"]
    DEPT_COLORS = {
        "Batteries": "rgba(66, 133, 244, 0.76)",
        "Forklift": "rgba(52, 168,  83, 0.80)",
        "Machine": "rgba(242,142,  43, 0.85)",
        "Other": "rgba(148,103, 189, 0.80)",
        "Sensors": "rgba(255,199,  44, 0.80)",
        "Transmissions": "rgba(233,  74, 126, 0.80)",
    }

    fig = go.Figure()
    for dept in dept_order:
        dfd = df.loc[df["Department"] == dept]
        fig.add_trace(
            go.Bar(
                x=dfd["MonthYear"],
                y=dfd["Savings"],
                name=dept,
                marker_color=DEPT_COLORS[dept],
                marker_line_width=0,
            )
        )

    short = [m.split()[0] for m in order]

    fig.update_layout(
        autosize=False,
        width=BAR_W,
        height=BAR_H,
        barmode="stack",
        template="plotly_white",
        showlegend=True,
        legend=dict(
            orientation="h",
            y=-0.22,
            x=0.5,
            xanchor="center",
            font=dict(size=14),
            bordercolor="lightgrey",
            borderwidth=1,
            bgcolor="white",
        ),
        margin=dict(l=10, r=10, t=80, b=60),
        title=dict(
            text="<b>Monthly Savings by Department</b>",
            x=0.01,
            xanchor="left",
            font=dict(size=18),
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=order,
        ticktext=short,
        showgrid=False,
        showline=True,
        linecolor="darkgrey",
    )

    monthly_totals = df.groupby("MonthYear", observed=True)["Savings"].sum()
    ymax = int(np.ceil(monthly_totals.max() / 10000.0) * 10000)
    ymax = max(ymax, 60000)
    tickvals = list(range(0, ymax + 1, 10000))

    fig.update_yaxes(
        title_text="Savings ($)",
        range=[0, ymax],
        tickvals=tickvals,
        tickprefix="$",
        tickformat=",d",
        showgrid=False,
        showticklabels=True,
        ticks="outside",
        ticklen=5,
        linecolor="darkgrey",
        automargin=True,
    )
    return fig

# -----------------------------------------------------------------------------
# GENERATE PIE CHART OF TOTAL SAVINGS
# -----------------------------------------------------------------------------

def make_totals_pie(totals_df: pd.DataFrame) -> go.Figure:
    DEPT_COLORS = {
        "Batteries": "rgba(66, 133, 244, 0.76)",
        "Forklift": "rgba(52, 168,  83, 0.80)",
        "Machine": "rgba(242,142,  43, 0.85)",
        "Other": "rgba(148,103, 189, 0.80)",
        "Sensors": "rgba(255,199,  44, 0.80)",
        "Transmissions": "rgba(233,  74, 126, 0.80)",
    }

    fig = go.Figure(
        go.Pie(
            labels=totals_df["Department"],
            values=totals_df["Savings"],
            marker=dict(colors=[DEPT_COLORS[d] for d in totals_df["Department"]]),
            sort=False,
            direction="clockwise",
            textinfo="percent+label",
            textposition="outside",
            insidetextorientation="radial",
            showlegend=False,
            pull=0.05,
            hovertemplate="%{label}: $%{value:,}<br>%{percent}<extra></extra>",
        )
    )

    fig.update_layout(
        autosize=False,
        width=PIE_W,
        height=PIE_H,
        template="plotly_white",
        margin=dict(l=10, r=10, t=80, b=40),
        title=dict(
            text="<b>Total Savings by Department</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=18),
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig

# -----------------------------------------------------------------------------
# GENERATE ROI & FORECAST GRAPH
# -----------------------------------------------------------------------------

def make_roi_forecast(roi_df: pd.DataFrame, fcst_df: pd.DataFrame) -> go.Figure:
    actual_months = roi_df["Month"].tolist()
    forecast_months = fcst_df["Month"].tolist()
    all_months = actual_months + forecast_months
    short = [m.split()[0] for m in all_months]

    last_roi_month = actual_months[-1]
    last_roi_value = roi_df["Procurement ROI"].iloc[-1]
    fcst_x = [last_roi_month] + forecast_months
    fcst_y = [last_roi_value] + fcst_df["Forecast"].tolist()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=actual_months,
            y=roi_df["Procurement ROI"],
            mode="lines+markers",
            name="Procurement ROI",
            line=dict(shape="spline", width=3, color="#636EFA"),
            marker=dict(size=6, color="#636EFA"),
            hovertemplate="%{x}: $%{y:,}<extra></extra>",
            fill="tozeroy",
            fillcolor="rgba(99,110,250,0.25)",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fcst_x,
            y=fcst_y,
            mode="lines+markers",
            name="Forecast",
            line=dict(shape="spline", width=3, color="blue", dash="dot"),
            marker=dict(symbol="circle-open", size=8, color="blue"),
            hovertemplate="%{x}: $%{y:,}<extra></extra>",
            fill="tozeroy",
            fillcolor="rgba(99,110,250,0.10)",
        )
    )

    data_max = max(roi_df["Procurement ROI"].max(), fcst_df["Forecast"].max(), last_roi_value)
    ymax = 40000 if data_max <= 40000 else int(np.ceil(data_max / 5000.0) * 5000)
    ymin = 10000
    tickvals = list(range(ymin, ymax + 1, 5000))

    fig.update_layout(
        autosize=False,
        width=ROI_W,
        height=ROI_H,
        template="plotly_white",
        margin=dict(l=80, r=10, t=80, b=60),
        title=dict(
            text="<b>Procurement ROI & Forecast</b>",
            x=0.01,
            xanchor="left",
            font=dict(size=18),
        ),
        legend=dict(
            orientation="h",
            y=-0.25,
            x=0.5,
            xanchor="center",
            font=dict(size=14),
            bordercolor="lightgrey",
            borderwidth=1,
            bgcolor="white",
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    fig.update_xaxes(
        tickmode="array",
        tickvals=all_months,
        ticktext=short,
        showgrid=False,
        showline=True,
        linecolor="darkgrey",
    )

    fig.update_yaxes(
        title_text="ROI ($)",
        range=[ymin, ymax],
        tickvals=tickvals,
        tickprefix="$",
        tickformat=",d",
        ticks="outside",
        ticklen=5,
        showgrid=False,
        showline=True,
        linecolor="darkgrey",
        automargin=True,
        showticklabels=True,
    )
    return fig


# -----------------------------------------------------------------------------
# DASHBOARD HTML
# -----------------------------------------------------------------------------
def create_dashboard(
    kpi_s: pd.Series,
    savings_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
    roi_df: pd.DataFrame,
    fcst_df: pd.DataFrame,
    output: str | Path = "../outputs/dashboard.html",
):
    prev_material = back_calc_previous(kpi_s["cost_of_material"], kpi_s["pct_change_material"])
    prev_avoid = back_calc_previous(kpi_s["cost_of_avoidance"], kpi_s["pct_change_avoidance"])
    prev_savings = back_calc_previous(kpi_s["savings"], kpi_s["pct_change_savings"])

    kpi_titles = ["Cost of Material", "Cost of Avoidance", "Savings"]
    kpi_curr = [kpi_s["cost_of_material"], kpi_s["cost_of_avoidance"], kpi_s["savings"]]
    kpi_pct = [kpi_s["pct_change_material"], kpi_s["pct_change_avoidance"], kpi_s["pct_change_savings"]]
    kpi_prev = [prev_material, prev_avoid, prev_savings]

    kpi_figs = [make_kpi_donut(kpi_titles[i], kpi_curr[i], kpi_pct[i], kpi_prev[i]) for i in range(3)]
    monthly_fig = make_monthly_stacked(monthly_df)
    totals_fig = make_totals_pie(savings_df)
    roi_fig = make_roi_forecast(roi_df, fcst_df)

    def kpi_delta_markup(idx: int) -> str:
        pct = kpi_pct[idx]
        return f"<span class='negative'>{pct:+.2f}% &#x25BC;</span> vs last month"

    style_css = """
<style>
body {
    margin:0;
    padding:0;
    background:#eef1f7;
    font-family:"Open Sans", verdana, arial, sans-serif;
}
.dashboard-wrapper {
    width:100%;
    max-width:1600px;
    margin:auto;
    padding:16px;
}
h1.dash-title {
    font-size:32px;
    font-weight:bold;
    margin:0 0 24px 0;
    color:#111;
    text-align:left;
}
.card {
    background:#fff;
    background:linear-gradient(#ffffff, #f7f9fc);
    border-radius:18px;
    box-shadow:0 2px 12px rgba(50,50,93,0.07), 0 1.5px 4px rgba(0,0,0,0.07);
    padding:18px;
    margin:2px;
    transition:box-shadow 0.2s;
}
.card:hover {
    box-shadow:0 4px 24px rgba(50,50,93,0.13), 0 3px 8px rgba(0,0,0,0.13);
}
.nested-card {
    background:#f4f4f4;
    border-radius:8px;
    padding:6px 10px;
    position:relative;
    font-size: 14px;
    text-align:center;
    color:#666;
    box-shadow:0 1px 3px rgba(0,0,0,0.08);
    margin-top:4px;
}
.positive {
    color:#27ae60;
    font-weight:bold;
}
.negative {
    color:#c0392b;
    font-weight:bold;
}
.dashboard-grid {
    display:grid;
    grid-template-columns:repeat(3, 1fr);
    grid-template-rows:0.20fr 0.50fr 0.40fr;
    gap:12px;
    width:100%;
}
.card .js-plotly-plot,
.card .plotly-graph-div {
    max-width:100% !important;
    margin:0 auto;
}
@media (max-width:900px){
    .dashboard-grid {
        grid-template-columns:1fr;
        grid-template-rows:auto;
    }
    .span-all { grid-column:1 !important; }
}
</style>
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Procurement Dashboard</title>
{style_css}
</head>
<body>
<div class="dashboard-wrapper">
  <h1 class="dash-title">Procurement Dashboard</h1>
  <div class="dashboard-grid">
    <div class="card" style="grid-row:1;grid-column:1;">
        {kpi_figs[0].to_html(full_html=False, include_plotlyjs='cdn', config=PLOT_CONFIG)}
        <div class="nested-card">{kpi_delta_markup(0)}</div>
    </div>
    <div class="card" style="grid-row:1;grid-column:2;">
        {kpi_figs[1].to_html(full_html=False, include_plotlyjs=False, config=PLOT_CONFIG)}
        <div class="nested-card">{kpi_delta_markup(1)}</div>
    </div>
    <div class="card" style="grid-row:1;grid-column:3;">
        {kpi_figs[2].to_html(full_html=False, include_plotlyjs=False, config=PLOT_CONFIG)}
        <div class="nested-card">{kpi_delta_markup(2)}</div>
    </div>
    <div class="card span-all" style="grid-row:2;grid-column:1/3;">
        {monthly_fig.to_html(full_html=False, include_plotlyjs=False, config=PLOT_CONFIG)}
    </div>
    <div class="card" style="grid-row:2;grid-column:3;">
        {totals_fig.to_html(full_html=False, include_plotlyjs=False, config=PLOT_CONFIG)}
    </div>
    <div class="card span-all" style="grid-row:3;grid-column:1/4;">
        {roi_fig.to_html(full_html=False, include_plotlyjs=False, config=PLOT_CONFIG)}
    </div>
  </div>
</div>
</body>
</html>
"""

    with open(output, "w", encoding="utf-8") as f:
        f.write(html)


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    kpi_s, sav_df, mon_df, roi_df, fcst_df = load_data(root)
    out_path = root / "outputs" / "dashboard.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    create_dashboard(kpi_s, sav_df, mon_df, roi_df, fcst_df, output=out_path)
    print(f"Dashboard created successfully! -> {out_path}")
