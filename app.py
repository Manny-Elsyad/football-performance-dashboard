"""Interactive football performance dashboard.

This Streamlit app explores a sample football player dataset with filters,
comparison views, and analytical charts for recruiter-friendly storytelling.
"""

from pathlib import Path
from typing import Any, Optional, Union

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


def get_score_badge(score: float) -> tuple[str, str]:
    """Return a badge label and accent color based on the scouting score."""
    if score >= 85:
        return "Elite", "#22c55e"
    if score >= 70:
        return "Strong", "#38bdf8"
    return "Monitor", "#f59e0b"


def render_metric_card(label: str, value: Union[str, int, float], icon: str = "⚽", subtitle: str = "") -> None:
    """Render a premium-looking KPI card in the Streamlit app."""
    st.markdown(
        f"""
        <div class="scouting-card metric-card">
            <div style="display:flex; justify-content:space-between; align-items:center; gap:0.6rem; margin-bottom:0.45rem;">
                <div style="font-size:0.95rem; color:#cbd5e1; font-weight:600;">{label}</div>
                <div style="font-size:1.1rem;">{icon}</div>
            </div>
            <div style="font-size:1.5rem; font-weight:700; color:#f8fafc; margin-bottom:0.2rem;">{value}</div>
            <div style="font-size:0.8rem; color:#94a3b8;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(title: str, body: str, accent: str = "#2563eb") -> None:
    """Render a polished content card for the scouting experience."""
    st.markdown(
        f"""
        <div class="scouting-card" style="border-left:4px solid {accent};">
            <h4 style="margin:0 0 0.35rem 0; color:#f8fafc;">{title}</h4>
            <div style="color:#cbd5e1; line-height:1.5;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_scouting_report(profile: dict, similarity: list[dict]) -> bytes:
    """Create a polished scouting brief that can be downloaded as a text report."""
    strengths = ", ".join(profile.get("Strengths", [])) or "strong overall scouting indicators"
    weaknesses = ", ".join(profile.get("Weaknesses", [])) or "limited sample size"
    recommendation = profile.get("Recommendation", "Monitor closely")
    fit = profile.get("Fit", "Developing profile")
    comparable = "\n".join(
        [f"- {item.get('Player', 'Unknown')} ({item.get('SimilarityPercent', 0)}% similarity)" for item in similarity]
    ) or "- No comparable profiles available"
    report_text = f"""Scouting Report
================
Player Overview
- Player: {profile.get('Player', 'Unknown')}
- Team: {profile.get('Team', 'Unknown')}
- Position: {profile.get('Position', 'Unknown')}
- Minutes: {profile.get('Minutes', 0)}
- Goals: {profile.get('Goals', 0)}
- Assists: {profile.get('Assists', 0)}
- xG: {profile.get('xG', 0)}
- xA: {profile.get('xA', 0)}
- Winger Scouting Score: {profile.get('WingerScoutingScore', 0)}

Key Strengths
- {strengths}

Weaknesses / Development Areas
- {weaknesses}

Tactical Fit
- {profile.get('Player', 'This player')} profiles best as a {profile.get('Position', 'wide attacker').lower()} whose value is tied to direct participation in the attacking phase, especially in transition moments and in possession-driven build-up.
- The current profile suggests a strong fit for {fit.lower()}.

Recruitment Recommendation
- {recommendation}. The player presents a compelling mix of output and tactical utility, but the profile should be monitored closely to confirm whether the current trend is sustainable over a larger sample.

Comparable Profiles
{comparable}
"""
    return report_text.encode("utf-8")


st.set_page_config(page_title="Football Scouting Platform", page_icon="⚽", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "players.csv"


def get_tab_labels() -> list[str]:
    """Return the tab labels used for the scouting platform navigation."""
    return ["Dashboard", "Player Profile", "Compare Players", "Similarity Search", "Scouting Reports"]


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load and preprocess the bundled football player dataset."""
    if DATA_PATH.exists():
        df = pd.read_csv(DATA_PATH)
        if not df.empty:
            return df.sort_values(["Team", "Player"]).reset_index(drop=True)

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
    """Convert scouting metrics to percentile ranks for both raw and per-90 analysis."""
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
        "GoalsPer90",
        "AssistsPer90",
        "GoalContributionsPer90",
        "ProgressiveCarriesPer90",
        "SuccessfulDribblesPer90",
        "KeyPassesPer90",
        "xGPer90",
        "xAPer90",
    ]
    for metric in metrics:
        if metric in percentile_df.columns:
            percentile_df[metric] = pd.to_numeric(percentile_df[metric], errors="coerce")
            percentile_df[metric + "Percentile"] = percentile_df[metric].rank(pct=True) * 100
    percentile_columns = [col for col in percentile_df.columns if col.endswith("Percentile")]
    percentile_df["Percentile"] = percentile_df[percentile_columns].mean(axis=1).round(1) if percentile_columns else 0.0
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
    recommendation = "Monitor closely"
    fit = "Developing profile"
    if row.get("GoalsPer90", 0) >= 0.8:
        strengths.append("High goal threat")
        recommendation = "Strong attacking prospect"
        fit = "High-value profile for wide attacking roles"
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
    percentile_map = {
        "Goals": row.get("GoalsPercentile", 0),
        "Assists": row.get("AssistsPercentile", 0),
        "Goals/90": row.get("GoalsPer90Percentile", 0),
        "Assists/90": row.get("AssistsPer90Percentile", 0),
        "xG": row.get("xGPercentile", 0),
        "xA": row.get("xAPercentile", 0),
        "Progressive Carries": row.get("ProgressiveCarriesPercentile", 0),
        "Successful Dribbles": row.get("SuccessfulDribblesPercentile", 0),
        "Key Passes": row.get("KeyPassesPercentile", 0),
        "Winger Scouting Score": row.get("WingerScoutingScorePercentile", 0),
    }
    radar_metrics = [
        ("Goals/90", row.get("GoalsPer90", 0)),
        ("Assists/90", row.get("AssistsPer90", 0)),
        ("xG", row.get("xG", 0)),
        ("xA", row.get("xA", 0)),
        ("Successful Dribbles", row.get("SuccessfulDribblesPer90", 0)),
    ]
    return {
        "Player": row["Player"],
        "Team": row.get("Team", "Unknown"),
        "League": row.get("League", "Unknown"),
        "Position": row.get("Position", "Unknown"),
        "Age": row.get("Age", "Unknown"),
        "Nationality": row.get("Nationality", "Unknown"),
        "Minutes": int(row.get("MinutesPlayed", 0)),
        "Goals": int(row.get("Goals", 0)),
        "Assists": int(row.get("Assists", 0)),
        "xG": round(float(row.get("xG", 0)), 2),
        "xA": round(float(row.get("xA", 0)), 2),
        "GoalsPer90": round(float(row.get("GoalsPer90", 0)), 2),
        "AssistsPer90": round(float(row.get("AssistsPer90", 0)), 2),
        "xGPer90": round(float(row.get("xGPer90", 0)), 2),
        "xAPer90": round(float(row.get("xAPer90", 0)), 2),
        "ProgressiveCarries": round(float(row.get("ProgressiveCarries", 0)), 2),
        "SuccessfulDribbles": round(float(row.get("SuccessfulDribbles", 0)), 2),
        "KeyPasses": round(float(row.get("KeyPasses", 0)), 2),
        "WingerScoutingScore": round(float(row.get("WingerScoutingScore", 0)), 2),
        "Percentiles": percentile_map,
        "RadarMetrics": radar_metrics,
        "Strengths": strengths,
        "Weaknesses": weaknesses,
        "Recommendation": recommendation,
        "Fit": fit,
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
    if not ranked.empty:
        max_similarity = ranked["SimilarityScore"].max()
        ranked["SimilarityPercent"] = ((1 - ranked["SimilarityScore"] / max_similarity) * 100).clip(0, 100).round(1)
    else:
        ranked["SimilarityPercent"] = pd.Series(dtype=float)
    return ranked[["Player", "Team", "Position", "WingerScoutingScore", "SimilarityScore", "SimilarityPercent"]].to_dict("records")


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


def main() -> None:
    """Render the Streamlit dashboard."""
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1rem; padding-bottom: 2rem; max-width: 1450px;}
        div[data-testid="stMetric"] {background: linear-gradient(135deg, #0f172a 0%, #111827 100%); border: 1px solid #334155; border-radius: 0.9rem; padding: 0.8rem 0.9rem; box-shadow: 0 6px 20px rgba(15,23,42,0.16);}
        .stTabs [data-baseweb="tab-list"] {gap: 0.45rem; margin-bottom: 0.95rem;}
        .stTabs [data-baseweb="tab"] {border-radius: 999px; padding: 0.5rem 0.9rem; background: #0f172a; color: #cbd5e1; border: 1px solid #334155;}
        .stTabs [data-baseweb="tab"][aria-selected="true"] {background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%); color: white; border-color: #1d4ed8;}
        section[data-testid="stSidebar"] > div {background: linear-gradient(180deg, #020617 0%, #0f172a 100%); border-right: 1px solid #1e293b;}
        .scouting-card {background: linear-gradient(135deg, #111827 0%, #0f172a 100%); border: 1px solid #1f2937; border-radius: 1.05rem; padding: 1rem 1.1rem; box-shadow: 0 10px 30px rgba(2,6,23,0.35); margin-bottom: 0.95rem;}
        .metric-card {min-height: 7.2rem;}
        .dashboard-hero {background: linear-gradient(135deg, #020617 0%, #111827 45%, #1d4ed8 100%); border-radius: 1.2rem; padding: 1.25rem 1.35rem; border: 1px solid rgba(96,165,250,0.24); box-shadow: 0 16px 36px rgba(2,6,23,0.28); margin-bottom: 0.9rem;}
        .dashboard-card {background: linear-gradient(135deg, #111827 0%, #0f172a 100%); border: 1px solid #1f2937; border-radius: 1rem; padding: 0.95rem 1rem; box-shadow: 0 8px 24px rgba(2,6,23,0.28); height: 100%;}
        .report-card {background: linear-gradient(135deg, #111827 0%, #0f172a 100%); border: 1px solid #1e293b; border-radius: 1rem; padding: 1rem 1.1rem; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);}
        .section-kicker {font-size: 0.74rem; color: #60a5fa; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase; margin-bottom: 0.2rem;}
        .section-title {font-size: 1.05rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.25rem;}
        .section-copy {color: #94a3b8; font-size: 0.94rem; margin-bottom: 0.8rem;}
        .score-ring {width: 120px; height: 120px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%); color: white; font-size: 1.35rem; font-weight: 700; box-shadow: 0 8px 20px rgba(37, 99, 235, 0.24);}
        @media (max-width: 1100px) {
            .block-container {padding-left: 0.9rem; padding-right: 0.9rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    df = load_data()

    with st.sidebar:
        st.markdown("<div style='padding:0.1rem 0 0.4rem 0;'><div style='font-size:1.2rem; font-weight:700; color:#f8fafc;'>Scouting Filters</div><div style='color:#94a3b8; font-size:0.9rem; margin-top:0.2rem;'>Refine the player pool for comparison and recruitment analysis</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.8px; background:linear-gradient(90deg, rgba(96,165,250,0.2), rgba(96,165,250,0.75)); margin:0.4rem 0 0.8rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:0.8rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#60a5fa; margin-bottom:0.35rem;'>Profile filters</div>", unsafe_allow_html=True)
        position = st.selectbox("Position", ["All", "Forward", "Midfielder", "Defender"])
        team = st.selectbox("Team", ["All", *sorted(df["Team"].unique())])
        st.markdown("<div style='font-size:0.8rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#60a5fa; margin:0.7rem 0 0.35rem 0;'>Output thresholds</div>", unsafe_allow_html=True)
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

    dashboard_tab, profile_tab, compare_tab, similarity_tab, reports_tab = st.tabs(
        ["📊 Dashboard", "🧠 Player Profile", "⚖️ Compare Players", "🔎 Similarity Search", "📝 Scouting Reports"]
    )

    with dashboard_tab:
        st.markdown(
            """
            <div class="dashboard-hero">
                <div style="font-size:0.76rem; color:#bfdbfe; font-weight:700; letter-spacing:0.18em; text-transform:uppercase; margin-bottom:0.35rem;">Scouting control centre</div>
                <div style="font-size:1.65rem; font-weight:700; color:#ffffff; margin-bottom:0.25rem;">Football Scouting Platform</div>
                <div style="font-size:1.02rem; color:#dbeafe; font-weight:600;">Analyze • Compare • Recruit</div>
                <div style="color:#e2e8f0; margin-top:0.45rem; max-width: 58rem;">A compact executive workspace for reviewing wide-attacking profiles, comparing tactical styles, and identifying recruitment-ready matches.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        summary_items = [
            ("Players in View", len(filtered_df), "Current scouting pool", "👥"),
            ("Clubs Represented", len(filtered_df["Team"].unique()), "Cross-club comparison view", "🏟️"),
            ("Average Winger Score", round(filtered_df["WingerScoutingScore"].mean(), 1) if "WingerScoutingScore" in filtered_df.columns else 0, "Overall scouting benchmark", "📈"),
            ("Top Profile", filtered_df.sort_values("WingerScoutingScore", ascending=False)["Player"].iloc[0] if not filtered_df.empty else "N/A", "Highest-rated player", "⭐"),
            ("Goal Threat", round(kpis.get("GoalsPer90", 0), 2), "Average goals per 90", "⚽"),
        ]
        summary_cols = st.columns(5)
        for col, (label, value, subtitle, icon) in zip(summary_cols, summary_items):
            with col:
                render_metric_card(label, value, icon=icon, subtitle=subtitle)

        top_row_left, top_row_right = st.columns([1.0, 1.0], gap="medium")
        with top_row_left:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-kicker'>Top prospects</div><div class='section-title'>Highest winger scores</div><div class='section-copy'>A compact view of the strongest profiles in the current pool.</div>", unsafe_allow_html=True)
            top_players = filtered_df[["Player", "Team", "Position", "WingerScoutingScore", "Goals", "Assists"]].sort_values("WingerScoutingScore", ascending=False).head(8).reset_index(drop=True)
            for idx, row in top_players.iterrows():
                badge_label, badge_color = get_score_badge(float(row["WingerScoutingScore"]))
                st.markdown(
                    f"""
                    <div class="scouting-card" style="padding:0.8rem 0.9rem; margin-bottom:0.6rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:0.7rem; flex-wrap:wrap;">
                            <div>
                                <div style="font-size:0.8rem; color:#60a5fa; font-weight:700;">#{idx + 1}</div>
                                <div style="font-size:1rem; font-weight:700; color:#f8fafc;">{row['Player']}</div>
                                <div style="color:#94a3b8; font-size:0.9rem;">{row['Team']} • {row['Position']}</div>
                            </div>
                            <div style="display:flex; align-items:center; gap:0.55rem; flex-wrap:wrap;">
                                <div style="background:{badge_color}; color:white; border-radius:999px; padding:0.3rem 0.65rem; font-size:0.78rem; font-weight:700;">{badge_label}</div>
                                <div style="text-align:right; min-width:4.7rem;">
                                    <div style="font-size:0.82rem; color:#94a3b8;">Score</div>
                                    <div style="font-size:1rem; font-weight:700; color:#f8fafc;">{row['WingerScoutingScore']}</div>
                                </div>
                                <div style="text-align:right; min-width:3.9rem;">
                                    <div style="font-size:0.82rem; color:#94a3b8;">Goals</div>
                                    <div style="font-size:1rem; font-weight:700; color:#f8fafc;">{row['Goals']}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        with top_row_right:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-kicker'>Output profile</div><div class='section-title'>Goals vs Assists</div><div class='section-copy'>A quick view of offensive output and distribution across the selected pool.</div>", unsafe_allow_html=True)
            st.plotly_chart(build_overview_chart(filtered_df), use_container_width=True, height=320)
            st.markdown("</div>", unsafe_allow_html=True)

        bottom_row_left, bottom_row_right = st.columns([1.0, 0.95], gap="medium")
        with bottom_row_left:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-kicker'>Goal output</div><div class='section-title'>Top goal scorers</div><div class='section-copy'>The current leaders by goal output.</div>", unsafe_allow_html=True)
            st.plotly_chart(build_top_players_chart(filtered_df), use_container_width=True, height=320)
            st.markdown("</div>", unsafe_allow_html=True)

        with bottom_row_right:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-kicker'>Distribution</div><div class='section-title'>Position mix</div><div class='section-copy'>A quick read on the profile mix in the active scouting view.</div>", unsafe_allow_html=True)
            st.plotly_chart(build_position_distribution(filtered_df), use_container_width=True, height=320)
            st.markdown("</div>", unsafe_allow_html=True)

    with profile_tab:
        st.subheader("Player Profile")
        st.caption("The flagship page for a detailed scouting view of the selected player.")
        profile_player = st.selectbox("Open a scouting profile", options=sorted(filtered_df["Player"].tolist()), index=0)
        profile = build_player_profile(filtered_df, profile_player)
        if profile:
            profile_cols = st.columns([0.9, 1.1])
            with profile_cols[0]:
                st.markdown(
                    f"""
                    <div class="scouting-card" style="padding: 1.1rem 1.15rem; border-left: 5px solid #2563eb;">
                        <div style="display:flex; justify-content:center; margin-bottom:0.85rem;">
                            <div class="score-ring">{profile.get('WingerScoutingScore', 0)}</div>
                        </div>
                        <div style="text-align:center;">
                            <div class="section-kicker">Primary profile</div>
                            <h2 style="margin:0.2rem 0 0.2rem 0; color:#0f172a;">{profile['Player']}</h2>
                            <div style="color:#475569; font-size:0.98rem;">{profile['Team']} • {profile.get('League', 'Unknown')}</div>
                            <div style="color:#475569; font-size:0.95rem; margin-top:0.25rem;">{profile['Position']} • {profile.get('Nationality', 'N/A')}</div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                info_grid = st.columns(2)
                info_grid[0].markdown(f"<div class='scouting-card'><div style='color:#64748b;'>Minutes</div><div style='font-size:1.15rem; font-weight:700; color:#0f172a;'>{profile.get('Minutes', 0)}</div></div>", unsafe_allow_html=True)
                info_grid[1].markdown(f"<div class='scouting-card'><div style='color:#64748b;'>Age</div><div style='font-size:1.15rem; font-weight:700; color:#0f172a;'>{profile.get('Age', 'N/A')}</div></div>", unsafe_allow_html=True)

            with profile_cols[1]:
                st.markdown("<div class='section-kicker'>Key scouting metrics</div>", unsafe_allow_html=True)
                kpi_cols = st.columns(4)
                kpi_items = [
                    ("Goals", profile.get("Goals", 0), "⚽", "Output"),
                    ("Assists", profile.get("Assists", 0), "🎯", "Creativity"),
                    ("Goals/90", profile.get("GoalsPer90", 0), "📈", "Efficiency"),
                    ("Successful Dribbles", profile.get("SuccessfulDribbles", 0), "🌀", "Ball carrying"),
                ]
                for col, (label, value, icon, subtitle) in zip(kpi_cols, kpi_items):
                    with col:
                        render_metric_card(label, value, icon=icon, subtitle=subtitle)

            st.markdown("<div class='section-kicker' style='margin-top:0.4rem;'>Analytical view</div>", unsafe_allow_html=True)
            analysis_cols = st.columns([1.05, 0.95])
            with analysis_cols[0]:
                radar_df = pd.DataFrame(profile.get("RadarMetrics", []), columns=["Metric", "Value"])
                if not radar_df.empty:
                    radar_fig = px.line_polar(radar_df, r="Value", theta="Metric", line_close=True, template="plotly_white")
                    radar_fig.update_traces(fill="toself", line_color="#2563eb", marker_color="#1d4ed8")
                    st.plotly_chart(radar_fig, use_container_width=True, height=400)
            with analysis_cols[1]:
                st.markdown("<div class='scouting-card'><div class='section-title'>Percentile profile</div></div>", unsafe_allow_html=True)
                for label, value in profile.get("Percentiles", {}).items():
                    st.markdown(
                        f"""
                        <div class="scouting-card" style="padding: 0.8rem 0.9rem; margin-bottom: 0.55rem;">
                            <div style="display:flex; justify-content:space-between; margin-bottom:0.25rem; color:#334155; font-size:0.9rem;">
                                <span>{label}</span><span>{round(value, 1)}th</span>
                            </div>
                            <div style="height:0.5rem; background:#e2e8f0; border-radius:999px; overflow:hidden;">
                                <div style="height:100%; width:{min(value / 100, 1.0) * 100}%; background:linear-gradient(90deg, #2563eb 0%, #38bdf8 100%); border-radius:999px;"></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            summary_grid = st.columns(2)
            with summary_grid[0]:
                render_info_card("Strengths", "• " + "<br/>• ".join(profile["Strengths"]) if profile["Strengths"] else "• Strong overall scouting indicators", accent="#22c55e")
            with summary_grid[1]:
                render_info_card("Weaknesses", "• " + "<br/>• ".join(profile["Weaknesses"]) if profile["Weaknesses"] else "• No major concerns identified", accent="#f59e0b")
            fit_col, recommendation_col = st.columns(2)
            with fit_col:
                render_info_card("Tactical fit", profile.get("Fit", "Developing profile"), accent="#0f172a")
            with recommendation_col:
                render_info_card("Recommendation", profile.get("Recommendation", "Monitor closely"), accent="#1d4ed8")
            st.markdown(
                f"""
                <div class="scouting-card" style="border-left:4px solid #2563eb;">
                    <div class="section-title">Scouting note</div>
                    <div style="color:#475569; line-height:1.55;">{profile['Player']} is a {profile['Position'].lower()} whose profile is shaped by {', '.join(profile['Strengths'][:2]) if profile['Strengths'] else 'strong overall scouting indicators'}. The tactical fit is best described as {profile['Fit'].lower()}, with a recommendation of {profile['Recommendation'].lower()}.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with compare_tab:
        st.subheader("Player Comparison")
        st.caption("Compare players side by side using radar, scatter, and comparative table views.")
        st.markdown(
            """
            <div class="scouting-card" style="border-left:4px solid #2563eb;">
                <div class="section-kicker">Comparison workspace</div>
                <div class="section-title">Benchmark two or more players with the same premium layout used across the platform.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
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
            st.markdown("<div class='section-title'>Comparison table</div>", unsafe_allow_html=True)
            st.dataframe(compare_df, use_container_width=True, height=260)

        comparison_two = st.selectbox("Compare player A", options=sorted(filtered_df["Player"].tolist()), index=0)
        comparison_two_b = st.selectbox("Compare player B", options=sorted(filtered_df["Player"].tolist()), index=min(1, len(filtered_df) - 1))
        if comparison_two and comparison_two_b:
            radar_fig, scatter_fig = build_player_comparison_charts(
                filtered_df,
                [comparison_two, comparison_two_b],
            )
            radar_col, scatter_col = st.columns(2)
            with radar_col:
                st.plotly_chart(radar_fig, use_container_width=True, height=380)
            with scatter_col:
                st.plotly_chart(scatter_fig, use_container_width=True, height=380)

    with similarity_tab:
        st.subheader("Similarity Search")
        st.caption("Find the closest tactical and output-based matches for a selected scouting profile.")
        similarity_player = st.selectbox("Find similar players to", options=sorted(filtered_df["Player"].tolist()), index=0)
        similar_players = build_similarity_search(filtered_df, similarity_player)
        if similar_players:
            similarity_df = pd.DataFrame(similar_players)
            similarity_df["SimilarityPercent"] = similarity_df["SimilarityPercent"].astype(float).round(1)
            similarity_df["SimilarityLabel"] = similarity_df["SimilarityPercent"].apply(lambda value: f"{value:.1f}%")
            st.markdown(
                """
                <div class="scouting-card" style="border-left:4px solid #2563eb;">
                    <div class="section-kicker">Similarity intelligence</div>
                    <div class="section-copy">Comparison is based on per-90 goal threat, creative output, dribbling impact, and link-up play.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            top_match = similarity_df.iloc[0]
            st.markdown(
                f"""
                <div class="scouting-card" style="border-left:5px solid #1d4ed8; background:linear-gradient(135deg, #172554 0%, #0f172a 100%);">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;">
                        <div>
                            <div style="font-size:0.8rem; color:#60a5fa; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Top Match</div>
                            <h3 style="margin:0.2rem 0; color:#f8fafc;">{top_match['Player']}</h3>
                            <div style="color:#cbd5e1;">{top_match['Team']} • {top_match['Position']}</div>
                        </div>
                        <div style="background:#1d4ed8; color:white; border-radius:0.9rem; padding:0.75rem 0.95rem; text-align:center; min-width:7rem;">
                            <div style="font-size:0.8rem; opacity:0.9;">Similarity</div>
                            <div style="font-size:1.35rem; font-weight:700;">{top_match['SimilarityPercent']}%</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            match_cols = st.columns(2)
            for idx, (_, row) in enumerate(similarity_df.iloc[1:].iterrows()):
                with match_cols[idx % 2]:
                    st.markdown(
                        f"""
                        <div class="scouting-card">
                            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem; margin-bottom:0.45rem;">
                                <div>
                                    <strong style="color:#f8fafc;">{row['Player']}</strong>
                                    <div style="color:#94a3b8; font-size:0.9rem;">{row['Team']} • {row['Position']}</div>
                                </div>
                                <div style="font-weight:700; color:#60a5fa;">{row['SimilarityPercent']}%</div>
                            </div>
                            <div style="height:0.5rem; background:#1f2937; border-radius:999px; overflow:hidden;">
                                <div style="height:100%; width:{row['SimilarityPercent']}%; background:linear-gradient(90deg, #2563eb 0%, #38bdf8 100%); border-radius:999px;"></div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<div class='section-title'>Similarity comparison</div>", unsafe_allow_html=True)
            st.plotly_chart(
                px.bar(
                    similarity_df.sort_values("SimilarityPercent", ascending=False).head(5),
                    x="SimilarityPercent",
                    y="Player",
                    orientation="h",
                    color="Player",
                    title=f"Similarity to {similarity_player}",
                    template="plotly_white",
                    labels={"SimilarityPercent": "Similarity (%)", "Player": "Player"},
                ),
                use_container_width=True,
                height=320,
            )

    with reports_tab:
        st.subheader("Scouting Reports")
        st.caption("Generate a polished scouting brief for the selected player and download it as a report.")
        report_player = st.selectbox("Select a player for a written report", options=sorted(filtered_df["Player"].tolist()), index=0)
        report_profile = build_player_profile(filtered_df, report_player)
        report_similarities = build_similarity_search(filtered_df, report_player) if report_profile else []
        if st.button("Generate scouting report") and report_profile:
            st.session_state["generated_report"] = build_scouting_report(report_profile, report_similarities)
            st.session_state["generated_report_name"] = f"{report_profile['Player'].replace(' ', '_')}_scouting_report.txt"
        if report_profile and st.session_state.get("generated_report"):
            st.markdown(
                f"""
                <div class="scouting-card" style="border-left:5px solid #0f766e; padding: 1.1rem 1.15rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.8rem; margin-bottom:0.8rem;">
                        <div>
                            <div class="section-kicker">Report output</div>
                            <h3 style="margin:0.15rem 0; color:#0f172a;">{report_profile['Player']} • Scouting Brief</h3>
                            <div style="color:#64748b;">Professional report ready for internal review</div>
                        </div>
                        <div>
                            <a download="{st.session_state.get('generated_report_name', 'scouting_report.txt')}" href="data:text/plain;charset=utf-8,{st.session_state['generated_report'].decode('utf-8').replace(chr(10), '%0A')}" style="background:#0f766e; color:white; padding:0.55rem 0.9rem; border-radius:0.7rem; text-decoration:none; display:inline-block;">Download report</a>
                        </div>
                    </div>
                    <div class="report-card" style="white-space:pre-wrap; font-family:ui-monospace, SFMono-Regular, monospace; color:#0f172a; line-height:1.55;">{st.session_state['generated_report'].decode('utf-8')}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif report_profile:
            st.markdown(
                """
                <div class="scouting-card" style="border-left:4px solid #2563eb;">
                    <div class="section-kicker">Report status</div>
                    <div class="section-copy">Generate a written scouting report for the selected player to review and download it.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
