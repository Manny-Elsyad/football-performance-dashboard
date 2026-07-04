"""Interactive football performance dashboard.

This Streamlit app explores a sample football player dataset with filters,
comparison views, and analytical charts for recruiter-friendly storytelling.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import streamlit as st

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
    st.set_page_config(page_title="Football Performance Dashboard", page_icon="⚽", layout="wide")
    st.title("Football Performance Dashboard")
    st.caption("A professional sports analytics portfolio project built with Python and Streamlit")

    df = load_data()

    with st.sidebar:
        st.header("Filters")
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

    st.subheader("Dashboard Overview")
    st.write(
        "Explore how players compare across clubs, positions, and key attacking and defensive metrics."
    )

    if filtered_df.empty:
        st.warning("No players match the current filters. Try adjusting the controls.")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Players Shown", len(filtered_df))
    with col2:
        st.metric("Total Goals", int(filtered_df["Goals"].sum()))
    with col3:
        st.metric("Average Minutes", round(filtered_df["MinutesPlayed"].mean(), 1))

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
            "PassingAccuracy",
            "Tackles",
            "Interceptions",
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
