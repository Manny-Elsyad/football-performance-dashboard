"""Chart and visualization creation functions"""

from typing import Any

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.analytics import build_winger_scoring, calculate_percentiles


def apply_dark_chart_style(fig: Any) -> Any:
    """Apply a consistent dark theme to Plotly charts for the premium scouting interface."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#020617",
        plot_bgcolor="#0f172a",
        font=dict(color="#f8fafc", family="Inter, Arial, sans-serif"),
        title=dict(font=dict(size=18, color="#f8fafc")),
        margin=dict(l=25, r=20, t=55, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#cbd5e1")),
    )
    fig.update_xaxes(
        title_font=dict(size=13, color="#cbd5e1"),
        tickfont=dict(size=12, color="#94a3b8"),
        gridcolor="#1e293b",
        zerolinecolor="#334155",
    )
    fig.update_yaxes(
        title_font=dict(size=13, color="#cbd5e1"),
        tickfont=dict(size=12, color="#94a3b8"),
        gridcolor="#1e293b",
        zerolinecolor="#334155",
    )
    return fig


def build_overview_chart(df: pd.DataFrame) -> px.scatter:
    """Create a scatter chart for goals versus assists by player."""
    fig = px.scatter(
        df,
        x="Goals",
        y="Assists",
        color="Position",
        size="MinutesPlayed",
        hover_name="Player",
        hover_data={
            "Team": True,
            "Position": True,
            "Goals": True,
            "Assists": True,
            "MinutesPlayed": True,
        },
        title="Goals vs Assists",
        template="plotly_dark",
    )
    return apply_dark_chart_style(fig)


def build_player_comparison_charts(df: pd.DataFrame, players: list[str]) -> list[go.Figure]:
    """Create radar and scatter charts for comparing two selected players with percentile-based values."""
    if len(players) < 2:
        return [go.Figure(), go.Figure()]
    comparison_df = df[df["Player"].isin(players)].copy()
    if comparison_df.empty:
        return [go.Figure(), go.Figure()]

    comparison_df = calculate_percentiles(build_winger_scoring(comparison_df))
    metrics = ["GoalsPercentile", "AssistsPercentile", "GoalContributionsPer90Percentile", "SuccessfulDribblesPer90Percentile", "KeyPassesPer90Percentile"]
    radar_df = comparison_df[["Player", *metrics]].copy()
    radar_df = radar_df.set_index("Player")
    radar_df = radar_df.T

    radar_fig = go.Figure()
    for player in players:
        values = [radar_df[player][metric] for metric in metrics]
        radar_fig.add_trace(
            go.Scatterpolar(
                r=[*values, values[0]],
                theta=[*metrics, metrics[0]],
                fill="toself",
                name=player,
            )
        )

    scatter_fig = px.scatter(
        comparison_df,
        x="GoalsPercentile",
        y="AssistsPercentile",
        color="Player",
        size="MinutesPlayed",
        hover_name="Player",
        title="Percentile Comparison: Goals vs Assists",
        template="plotly_dark",
    )
    radar_fig = apply_dark_chart_style(radar_fig)
    scatter_fig = apply_dark_chart_style(scatter_fig)
    return [radar_fig, scatter_fig]


def build_top_players_chart(df: pd.DataFrame) -> px.bar:
    """Create a bar chart showing the top scoring players."""
    top_df = df.sort_values("Goals", ascending=False).head(10)
    fig = px.bar(
        top_df,
        x="Player",
        y="Goals",
        color="Team",
        title="Top Goal Scorers",
        template="plotly_dark",
    )
    return apply_dark_chart_style(fig)


def build_position_distribution(df: pd.DataFrame) -> px.pie:
    """Create a pie chart for position distribution."""
    counts = df["Position"].value_counts().reset_index()
    counts.columns = ["Position", "Count"]
    fig = px.pie(
        counts,
        values="Count",
        names="Position",
        title="Position Distribution",
        template="plotly_dark",
    )
    return apply_dark_chart_style(fig)
