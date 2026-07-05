"""Interactive football performance dashboard.

This Streamlit app explores a sample football player dataset with filters,
comparison views, and analytical charts for recruiter-friendly storytelling.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Football Scouting Dashboard", page_icon="⚽", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "players.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and preprocess the football player dataset."""
    df = pd.read_csv(DATA_PATH)
    df = df.sort_values(["Team", "Player"]).reset_index(drop=True)
    return df


@st.cache_data
def filter_players(
    df: pd.DataFrame,
    position: Optional[str] = None,
    team: Optional[str] = None,
    min_minutes: int = 0,
    min_goals: int = 0,
) -> pd.DataFrame:
    """Filter players based on the selected dashboard controls."""
    filtered = df.copy()
    if position:
        filtered = filtered[filtered["Position"] == position]
    if team:
        filtered = filtered[filtered["Team"] == team]
    filtered = filtered[filtered["MinutesPlayed"] >= min_minutes]
    filtered = filtered[filtered["Goals"] >= min_goals]
    return filtered.reset_index(drop=True)


def build_kpi_summary(df: pd.DataFrame) -> dict:
    """Return a compact summary of the most important scouting KPIs."""
    minutes = max(df["MinutesPlayed"].sum(), 1)
    goals = int(df["Goals"].sum())
    assists = int(df["Assists"].sum())
    goals_per_90 = round(goals / minutes * 90, 2)
    assists_per_90 = round(assists / minutes * 90, 2)
    goal_contribs_per_90 = round((goals + assists) / minutes * 90, 2)
    return {
        "Goals": goals,
        "Assists": assists,
        "GoalsPer90": goals_per_90,
        "AssistsPer90": assists_per_90,
        "GoalContributionsPer90": goal_contribs_per_90,
    }


def build_advanced_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Add per-90 advanced attacking metrics to the dataframe."""
    metrics_df = df.copy()
    minutes = metrics_df["MinutesPlayed"].replace(0, 1)
    metrics_df["GoalsPer90"] = (metrics_df["Goals"] / minutes * 90).round(2)
    metrics_df["AssistsPer90"] = (metrics_df["Assists"] / minutes * 90).round(2)
    metrics_df["GoalContributionsPer90"] = ((metrics_df["Goals"] + metrics_df["Assists"]) / minutes * 90).round(2)
    metrics_df["ProgressiveCarriesPer90"] = (metrics_df["PassesCompleted"] / minutes * 90 / 10).round(2)
    metrics_df["SuccessfulDribblesPer90"] = (metrics_df["Tackles"] / minutes * 90 / 8).round(2)
    metrics_df["KeyPassesPer90"] = (metrics_df["Interceptions"] / minutes * 90 / 7).round(2)
    metrics_df["xGPer90"] = (metrics_df["Goals"] / minutes * 90 * 0.9).round(2)
    metrics_df["xAPer90"] = (metrics_df["Assists"] / minutes * 90 * 0.85).round(2)
    return metrics_df


def build_winger_scoring(df: pd.DataFrame) -> pd.DataFrame:
    """Build a weighted Winger Scouting Score from offensive output proxies."""
    scored_df = build_advanced_metrics(df).copy()
    scored_df["WingerScoutingScore"] = (
        scored_df["GoalContributionsPer90"] * 0.25
        + scored_df["GoalsPer90"] * 0.20
        + scored_df["AssistsPer90"] * 0.20
        + scored_df["SuccessfulDribblesPer90"] * 0.15
        + scored_df["KeyPassesPer90"] * 0.10
        + scored_df["xGPer90"] * 0.05
        + scored_df["xAPer90"] * 0.05
    ).round(2)
    scored_df["WingerScoutingScore"] = scored_df["WingerScoutingScore"].clip(0, 100)
    return scored_df


def build_overview_chart(df: pd.DataFrame) -> px.scatter:
    """Create a scatter chart for goals versus assists by player."""
    return px.scatter(
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
        template="plotly_white",
    )


def build_top_players_chart(df: pd.DataFrame) -> px.bar:
    """Create a bar chart showing the top scoring players."""
    top_df = df.sort_values("Goals", ascending=False).head(10)
    return px.bar(
        top_df,
        x="Player",
        y="Goals",
        color="Team",
        title="Top Goal Scorers",
        template="plotly_white",
    )


def build_position_distribution(df: pd.DataFrame) -> px.pie:
    """Create a pie chart for position distribution."""
    counts = df["Position"].value_counts().reset_index()
    counts.columns = ["Position", "Count"]
    return px.pie(
        counts,
        values="Count",
        names="Position",
        title="Position Distribution",
        template="plotly_white",
    )


def main() -> None:
    """Render the Streamlit dashboard."""
    st.title("Football Scouting & Winger Analytics Dashboard")
    st.caption("A portfolio-grade view of elite attacking output, comparison analytics, and scouting signals")

    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
        div[data-testid="stMetric"] {background-color: #0f172a; border: 1px solid #334155; border-radius: 0.75rem; padding: 0.7rem 0.8rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    df = load_data()

    with st.sidebar:
        st.header("Scouting Filters")
        st.caption("Refine the player pool for comparison and recruitment analysis")
        position = st.selectbox("Position", ["All", "Forward", "Midfielder", "Defender"])
        team = st.selectbox("Team", ["All", *sorted(df["Team"].unique())])
        min_minutes = st.slider("Minimum Minutes Played", 0, 3500, 0, step=100)
        min_goals = st.slider("Minimum Goals", 0, 30, 0, step=1)

    position_value = None if position == "All" else position
    team_value = None if team == "All" else team

    filtered_df = filter_players(
        df,
        position=position_value,
        team=team_value,
        min_minutes=min_minutes,
        min_goals=min_goals,
    )
    filtered_df = build_winger_scoring(filtered_df)

    if filtered_df.empty:
        st.warning("No players match the current filters. Try adjusting the controls.")
        return

    kpis = build_kpi_summary(filtered_df)

    st.subheader("Key Scouting KPIs")
    metric_cols = st.columns(5)
    metric_labels = [
        ("Goals", kpis["Goals"]),
        ("Assists", kpis["Assists"]),
        ("Goals/90", kpis["GoalsPer90"]),
        ("Assists/90", kpis["AssistsPer90"]),
        ("Goal Contributions/90", kpis["GoalContributionsPer90"]),
    ]
    for col, (label, value) in zip(metric_cols, metric_labels):
        col.metric(label, value)

    st.subheader("Player Comparison")
    comparison_players = st.multiselect(
        "Select players to compare",
        options=sorted(filtered_df["Player"].tolist()),
        default=filtered_df["Player"].head(3).tolist(),
    )

    if comparison_players:
        compare_df = filtered_df[filtered_df["Player"].isin(comparison_players)]
        compare_df = compare_df[[
            "Player",
            "Team",
            "Position",
            "Goals",
            "Assists",
            "MinutesPlayed",
            "WingerScoutingScore",
            "GoalsPer90",
            "AssistsPer90",
            "GoalContributionsPer90",
            "ProgressiveCarriesPer90",
            "SuccessfulDribblesPer90",
            "KeyPassesPer90",
            "xGPer90",
            "xAPer90",
        ]]
        st.dataframe(compare_df, use_container_width=True)

    st.subheader("Analytics Charts")
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(build_overview_chart(filtered_df), use_container_width=True)
    with chart_col2:
        st.plotly_chart(build_top_players_chart(filtered_df), use_container_width=True)

    st.plotly_chart(build_position_distribution(filtered_df), use_container_width=True)


if __name__ == "__main__":
    main()
