"""Interactive football performance dashboard.

This Streamlit app explores a sample football player dataset with filters,
comparison views, and analytical charts for recruiter-friendly storytelling.
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from statsbombpy import sb


st.set_page_config(page_title="Football Scouting Dashboard", page_icon="⚽", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "players.csv"


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and preprocess the football player dataset, preferring a real-world source when available."""
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
        if not df.empty:
            return df.sort_values(["Team", "Player"]).reset_index(drop=True)

    try:
        competitions = sb.competitions()
        competition_ids = competitions[competitions["competition_gender"] == "male"]["competition_id"].tolist()[:5]
        rows = []
        for competition_id in competition_ids:
            try:
                matches = sb.matches(competition_id=competition_id, season_id=281)
                if matches.empty:
                    continue
                for _, match in matches.head(3).iterrows():
                    rows.append({"Competition": competition_id, "MatchID": match.get("match_id")})
            except Exception:
                continue
        if rows:
            return pd.DataFrame(rows)
    except Exception:
        pass

    return pd.DataFrame(columns=["Player", "Team", "Position", "MinutesPlayed", "Goals", "Assists", "xG", "xA", "ProgressiveCarries", "SuccessfulDribbles", "KeyPasses", "WingerScoutingScore"])


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


def calculate_percentiles(df: pd.DataFrame) -> pd.DataFrame:
    """Convert scouting metrics to percentile ranks."""
    percentile_df = df.copy()
    metrics = [
        "Goals",
        "Assists",
        "xG",
        "xA",
        "ProgressiveCarries",
        "SuccessfulDribbles",
        "KeyPasses",
        "WingerScoutingScore",
    ]
    for metric in metrics:
        if metric in percentile_df.columns:
            percentile_df[metric] = pd.to_numeric(percentile_df[metric], errors="coerce")
            percentile_df[metric + "Percentile"] = percentile_df[metric].rank(pct=True) * 100
    percentile_df["Percentile"] = percentile_df[[col for col in percentile_df.columns if col.endswith("Percentile")]].mean(axis=1).round(1)
    return percentile_df


def build_player_profile(df: pd.DataFrame, player_name: str) -> dict:
    """Create a structured player profile for the scouting detail page."""
    scored_df = build_winger_scoring(df)
    player_row = scored_df[scored_df["Player"] == player_name]
    if player_row.empty:
        return {}
    row = player_row.iloc[0]
    strengths = []
    weaknesses = []
    if row.get("GoalsPer90", 0) >= 0.8:
        strengths.append("High goal threat")
    else:
        weaknesses.append("Goal output needs growth")
    if row.get("AssistsPer90", 0) >= 0.7:
        strengths.append("Creative chance creation")
    else:
        weaknesses.append("Chance creation is inconsistent")
    if row.get("SuccessfulDribblesPer90", 0) >= 1.5:
        strengths.append("Elite dribbling impact")
    else:
        weaknesses.append("Dribbling volume is modest")
    if row.get("KeyPassesPer90", 0) >= 1.0:
        strengths.append("Strong link-up play")
    else:
        weaknesses.append("Link-up play is limited")
    return {
        "Player": row["Player"],
        "Team": row.get("Team", "Unknown"),
        "Position": row.get("Position", "Unknown"),
        "Minutes": int(row.get("MinutesPlayed", 0)),
        "Goals": int(row.get("Goals", 0)),
        "Assists": int(row.get("Assists", 0)),
        "xG": round(float(row.get("xG", 0)), 2),
        "xA": round(float(row.get("xA", 0)), 2),
        "ProgressiveCarries": round(float(row.get("ProgressiveCarries", 0)), 2),
        "SuccessfulDribbles": round(float(row.get("SuccessfulDribbles", 0)), 2),
        "KeyPasses": round(float(row.get("KeyPasses", 0)), 2),
        "WingerScoutingScore": round(float(row.get("WingerScoutingScore", 0)), 2),
        "Strengths": strengths,
        "Weaknesses": weaknesses,
    }


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


def build_similarity_search(df: pd.DataFrame, player_name: str) -> list[dict]:
    """Return the five most similar players based on scouting metrics."""
    scored_df = build_winger_scoring(df)
    if player_name not in scored_df["Player"].values:
        return []

    target = scored_df[scored_df["Player"] == player_name].iloc[0]
    similarity_columns = [
        "GoalsPer90",
        "AssistsPer90",
        "GoalContributionsPer90",
        "SuccessfulDribblesPer90",
        "KeyPassesPer90",
        "xGPer90",
        "xAPer90",
    ]
    base = scored_df[scored_df["Player"] != player_name].copy()
    base_numeric = base[similarity_columns].apply(pd.to_numeric, errors="coerce").fillna(0)
    target_numeric = pd.Series(target[similarity_columns]).apply(pd.to_numeric, errors="coerce").fillna(0)
    base["SimilarityScore"] = ((base_numeric - target_numeric).pow(2).sum(axis=1) ** 0.5).round(2)
    ranked = base.sort_values("SimilarityScore").head(5)
    return ranked[["Player", "Team", "Position", "WingerScoutingScore", "SimilarityScore"]].to_dict("records")


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


def build_player_comparison_charts(df: pd.DataFrame, players: list[str]) -> list[go.Figure]:
    """Create radar and scatter charts for comparing two selected players."""
    if len(players) < 2:
        return [go.Figure(), go.Figure()]
    comparison_df = df[df["Player"].isin(players)].copy()
    if comparison_df.empty:
        return [go.Figure(), go.Figure()]

    comparison_df = build_winger_scoring(comparison_df)
    metrics = ["GoalsPer90", "AssistsPer90", "GoalContributionsPer90", "SuccessfulDribblesPer90", "KeyPassesPer90"]
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
        x="GoalsPer90",
        y="AssistsPer90",
        color="Player",
        size="MinutesPlayed",
        hover_name="Player",
        title="Goals/90 vs Assists/90",
        template="plotly_white",
    )
    return [radar_fig, scatter_fig]


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
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); padding: 2rem; border-radius: 1rem; margin-bottom: 1.5rem;">
            <h1 style="color:white; margin-bottom:0.2rem;">Football Scouting & Winger Analytics Dashboard</h1>
            <p style="color:#cbd5e1; font-size:1.05rem; margin-top:0.3rem;">A portfolio-grade scouting workspace for evaluating winger profiles, comparing top talents, and uncovering similarity-based recruitment opportunities.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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

    st.subheader("Player Comparison Tools")
    comparison_two = st.selectbox("Compare player A", options=sorted(filtered_df["Player"].tolist()), index=0)
    comparison_two_b = st.selectbox("Compare player B", options=sorted(filtered_df["Player"].tolist()), index=min(1, len(filtered_df) - 1))
    if comparison_two and comparison_two_b:
        radar_fig, scatter_fig = build_player_comparison_charts(
            filtered_df,
            [comparison_two, comparison_two_b],
        )
        radar_col, scatter_col = st.columns(2)
        with radar_col:
            st.plotly_chart(radar_fig, use_container_width=True)
        with scatter_col:
            st.plotly_chart(scatter_fig, use_container_width=True)

    st.subheader("Similarity Search")
    similarity_player = st.selectbox("Find similar players to", options=sorted(filtered_df["Player"].tolist()), index=0)
    similar_players = build_similarity_search(filtered_df, similarity_player)
    if similar_players:
        st.dataframe(pd.DataFrame(similar_players), use_container_width=True)

    st.plotly_chart(build_position_distribution(filtered_df), use_container_width=True)


if __name__ == "__main__":
    main()
