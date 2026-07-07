"""Interactive football performance dashboard.

This Streamlit app explores a football player dataset with filters,
comparison views, and analytical charts for recruiter-friendly storytelling.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from src.analytics import build_kpi_summary, build_player_profile, build_winger_scoring
from src.clubs import get_best_club, get_club_recommendations
from src.data import filter_players, load_data
from src.reports import build_scouting_report
from src.similarity import build_similarity_search
from src.ui import (
    get_navigation_options,
    get_score_badge,
    get_tab_labels,
    render_info_card,
    render_metric_card,
)
from src.visualizations import (
    build_overview_chart,
    build_player_comparison_charts,
    build_position_distribution,
    build_top_players_chart,
)

st.set_page_config(page_title="Football Scouting Platform", page_icon="⚽", layout="wide")


def main() -> None:
    """Render the Streamlit dashboard."""
    st.markdown(
        """
        <style>
        .block-container {padding-top: 0.55rem; padding-bottom: 1.4rem; max-width: 1480px;}
        div[data-testid="stMetric"] {background: linear-gradient(135deg, #0f172a 0%, #111827 100%); border: 1px solid #334155; border-radius: 0.95rem; padding: 0.8rem 0.9rem; box-shadow: 0 6px 20px rgba(15,23,42,0.16);}
        div[data-testid="stRadio"] > div[role="radiogroup"] {display: flex; flex-wrap: wrap; gap: 0.45rem; padding: 0.25rem; margin-bottom: 0.9rem; border-radius: 999px; background: rgba(15, 23, 42, 0.95); border: 1px solid #1e293b; position: relative; z-index: 10; overflow: visible;}
        div[data-testid="stRadio"] label {color: #e2e8f0 !important; opacity: 1 !important; visibility: visible !important; padding: 0.55rem 0.9rem; border-radius: 999px; border: 1px solid transparent; font-weight: 600;}
        div[data-testid="stRadio"] label:hover {background: rgba(30, 41, 59, 0.95); color: #f8fafc !important; border-color: #334155;}
        div[data-testid="stRadio"] label[data-checked="true"] {background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%); color: #ffffff !important; border-color: #3b82f6; box-shadow: 0 6px 16px rgba(37, 99, 235, 0.24); font-weight: 700;}
        section[data-testid="stSidebar"] > div {background: linear-gradient(180deg, #020617 0%, #0f172a 100%); border-right: 1px solid #1e293b;}
        .scouting-card {background: linear-gradient(135deg, #111827 0%, #0f172a 100%); border: 1px solid #1f2937; border-radius: 0.95rem; padding: 0.85rem 0.95rem; box-shadow: 0 10px 26px rgba(2,6,23,0.3); margin-bottom: 0.7rem;}
        .metric-card {min-height: 6.35rem; padding: 0.8rem 0.9rem;}
        .dashboard-hero {background: linear-gradient(135deg, #020617 0%, #111827 45%, #1d4ed8 100%); border-radius: 1rem; padding: 1rem 1.1rem; border: 1px solid rgba(96,165,250,0.24); box-shadow: 0 12px 28px rgba(2,6,23,0.24); margin-bottom: 0.7rem;}
        .dashboard-card {background: linear-gradient(135deg, #111827 0%, #0f172a 100%); border: 1px solid #1f2937; border-radius: 0.95rem; padding: 0.85rem 0.95rem; box-shadow: 0 8px 22px rgba(2,6,23,0.26); height: 100%;}
        .report-card {background: linear-gradient(135deg, #111827 0%, #0f172a 100%); border: 1px solid #1e293b; border-radius: 0.95rem; padding: 0.9rem 1rem; box-shadow: inset 0 1px 0 rgba(255,255,255,0.06);}
        .section-kicker {font-size: 0.72rem; color: #60a5fa; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; margin-bottom: 0.16rem;}
        .section-title {font-size: 1.0rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.2rem;}
        .section-copy {color: #94a3b8; font-size: 0.9rem; margin-bottom: 0.65rem;}
        .score-ring {width: 132px; height: 132px; border-radius: 50%; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #0f172a 0%, #2563eb 100%); color: white; font-size: 1.35rem; font-weight: 700; box-shadow: 0 8px 20px rgba(37, 99, 235, 0.24);}
        .sidebar-section {padding: 0.4rem 0 0.2rem 0;}
        .sidebar-title {font-size: 1.02rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.25rem;}
        .sidebar-subtitle {color: #94a3b8; font-size: 0.88rem; line-height: 1.35; margin-bottom: 0.45rem;}
        .sidebar-label {font-size: 0.74rem; color: #60a5fa; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; margin: 0.35rem 0 0.25rem 0;}
        .match-progress {height: 0.5rem; background: #1f2937; border-radius: 999px; overflow: hidden; margin-top: 0.25rem;}
        .match-progress > div {height: 100%; background: linear-gradient(90deg, #2563eb 0%, #38bdf8 100%); border-radius: 999px;}
        @media (max-width: 1100px) {
            .block-container {padding-left: 0.9rem; padding-right: 0.9rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    df = load_data()

    with st.sidebar:
        st.markdown("<div class='sidebar-section'><div class='sidebar-title'>Data Source</div><div class='sidebar-subtitle'>Choose between sample and real football data.</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.8px; background:linear-gradient(90deg, rgba(96,165,250,0.2), rgba(96,165,250,0.75)); margin:0.35rem 0 0.6rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-label'>Dataset selection</div>", unsafe_allow_html=True)
        dataset_choice = st.radio("Choose dataset", options=["Sample Dataset", "Real Dataset"], index=0, key="dataset_selector")
        
        # Reload data if dataset changed
        if dataset_choice != st.session_state.get("current_dataset", "Sample Dataset"):
            st.session_state["current_dataset"] = dataset_choice
            st.cache_data.clear()
            df = load_data(dataset_choice)
        else:
            df = load_data(dataset_choice)
        
        st.markdown("<div class='sidebar-section'><div class='sidebar-title'>Recruitment Filters</div><div class='sidebar-subtitle'>Refine the active scouting pool for comparison and shortlist building.</div></div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.8px; background:linear-gradient(90deg, rgba(96,165,250,0.2), rgba(96,165,250,0.75)); margin:0.35rem 0 0.6rem 0;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='sidebar-label'>Profile filters</div>", unsafe_allow_html=True)
        position = st.selectbox("Position", ["All", "Forward", "Midfielder", "Defender"])
        team = st.selectbox("Team", ["All", *sorted(df["Team"].unique())])
        st.markdown("<div class='sidebar-label'>Output thresholds</div>", unsafe_allow_html=True)
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

    nav_labels = get_navigation_options()
    nav_values = get_tab_labels()
    if "active_nav_tab" not in st.session_state:
        st.session_state.active_nav_tab = nav_labels[0]

    active_tab = st.radio(
        "Navigation",
        options=nav_labels,
        index=nav_labels.index(st.session_state.active_nav_tab),
        horizontal=True,
        label_visibility="visible",
        key="active_nav_tab",
    )

    if active_tab == "🏠 Dashboard":
        st.markdown(
            """
            <div class="dashboard-hero">
                <div style="font-size:0.72rem; color:#bfdbfe; font-weight:700; letter-spacing:0.16em; text-transform:uppercase; margin-bottom:0.25rem;">Scouting control centre</div>
                <div style="font-size:1.45rem; font-weight:700; color:#ffffff; margin-bottom:0.2rem;">Football Scouting Platform</div>
                <div style="font-size:0.95rem; color:#dbeafe; font-weight:600;">Analyze • Compare • Recruit</div>
                <div style="color:#e2e8f0; margin-top:0.35rem; max-width: 58rem; font-size:0.95rem;">A compact executive workspace for reviewing wide-attacking profiles, comparing tactical styles, and identifying recruitment-ready matches.</div>
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
            st.plotly_chart(build_overview_chart(filtered_df), use_container_width=True, height=270)
            st.markdown("</div>", unsafe_allow_html=True)

        bottom_row_left, bottom_row_right = st.columns([1.0, 0.95], gap="medium")
        with bottom_row_left:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-kicker'>Goal output</div><div class='section-title'>Top goal scorers</div><div class='section-copy'>The current leaders by goal output.</div>", unsafe_allow_html=True)
            st.plotly_chart(build_top_players_chart(filtered_df), use_container_width=True, height=270)
            st.markdown("</div>", unsafe_allow_html=True)

        with bottom_row_right:
            st.markdown("<div class='dashboard-card'>", unsafe_allow_html=True)
            st.markdown("<div class='section-kicker'>Distribution</div><div class='section-title'>Position mix</div><div class='section-copy'>A quick read on the profile mix in the active scouting view.</div>", unsafe_allow_html=True)
            st.plotly_chart(build_position_distribution(filtered_df), use_container_width=True, height=270)
            st.markdown("</div>", unsafe_allow_html=True)

    elif active_tab == "👤 Player Profile":
        st.subheader("Player Profile")
        st.caption("The flagship page for a detailed scouting view of the selected player.")
        profile_player = st.selectbox("Open a scouting profile", options=sorted(filtered_df["Player"].tolist()), index=0)
        profile = build_player_profile(filtered_df, profile_player)
        if profile:
            profile_cols = st.columns([0.9, 1.1])
            with profile_cols[0]:
                st.markdown(
                    f"""
                    <div class="scouting-card" style="padding: 1rem 1.05rem; border-left: 5px solid #2563eb;">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;">
                            <div>
                                <div class="section-kicker">Primary profile</div>
                                <h2 style="margin:0.2rem 0 0.25rem 0; color:#f8fafc; font-size:1.55rem;">{profile['Player']}</h2>
                                <div style="color:#cbd5e1; font-size:0.95rem;">{profile['Team']} • {profile.get('League', 'Unknown')}</div>
                                <div style="color:#cbd5e1; font-size:0.95rem; margin-top:0.2rem;">{profile['Position']} • {profile.get('Nationality', 'N/A')}</div>
                            </div>
                            <div style="display:flex; align-items:center; justify-content:center;">
                                <div class="score-ring">{profile.get('WingerScoutingScore', 0)}</div>
                            </div>
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
                    radar_fig = px.line_polar(radar_df, r="Value", theta="Metric", line_close=True, template="plotly_dark")
                    radar_fig.update_traces(fill="toself", line_color="#2563eb", marker_color="#1d4ed8")
                    radar_fig.update_layout(
                        polar=dict(bgcolor="#0f172a", radialaxis=dict(gridcolor="#334155", tickfont=dict(size=11, color="#94a3b8")), angularaxis=dict(gridcolor="#334155", tickfont=dict(size=12, color="#f8fafc"))),
                        margin=dict(l=25, r=25, t=30, b=25),
                        paper_bgcolor="#020617",
                        plot_bgcolor="#0f172a",
                    )
                    st.plotly_chart(radar_fig, use_container_width=True, height=340)
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

    elif active_tab == "📊 Compare Players":
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

    elif active_tab == "🔍 Similarity Search":
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
                <div class="scouting-card" style="border-left:5px solid #1d4ed8; background:linear-gradient(135deg, #172554 0%, #0f172a 100%); padding:0.95rem 1rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;">
                        <div>
                            <div style="font-size:0.8rem; color:#60a5fa; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">Best match</div>
                            <h3 style="margin:0.2rem 0; color:#f8fafc; font-size:1.1rem;">{top_match['Player']}</h3>
                            <div style="color:#cbd5e1; font-size:0.92rem;">{top_match['Team']} • {top_match['Position']}</div>
                        </div>
                        <div style="background:#1d4ed8; color:white; border-radius:0.9rem; padding:0.65rem 0.85rem; text-align:center; min-width:6.8rem;">
                            <div style="font-size:0.77rem; opacity:0.9;">Similarity</div>
                            <div style="font-size:1.2rem; font-weight:700;">{top_match['SimilarityPercent']}%</div>
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
                        <div class="scouting-card" style="padding:0.8rem 0.9rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.7rem; margin-bottom:0.35rem;">
                                <div>
                                    <strong style="color:#f8fafc;">{row['Player']}</strong>
                                    <div style="color:#94a3b8; font-size:0.88rem;">{row['Team']} • {row['Position']}</div>
                                </div>
                                <div style="font-weight:700; color:#60a5fa; font-size:0.95rem;">{row['SimilarityPercent']}%</div>
                            </div>
                            <div class="match-progress">
                                <div style="width:{row['SimilarityPercent']}%;"></div>
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

    elif active_tab == "🏟️ Club Fit Engine":
        st.subheader("Club Fit Engine")
        st.caption("Find the best clubs that match the selected player's statistical profile and playing style.")
        
        fit_player = st.selectbox("Select player for club fit analysis", options=sorted(filtered_df["Player"].tolist()), index=0)
        
        if st.button("Analyze Club Fit", key="analyze_fit_btn"):
            st.session_state["club_fit_analysis"] = True
        
        if st.session_state.get("club_fit_analysis") and fit_player:
            # Build player profile with advanced metrics
            player_profile = build_player_profile(filtered_df, fit_player)
            
            # Get club recommendations
            recommendations = get_club_recommendations(player_profile, filtered_df)
            best_club_fit = get_best_club(player_profile, filtered_df)
            
            if best_club_fit:
                # Display best club card
                st.markdown(
                    f"""
                    <div class="scouting-card" style="border-left:5px solid #dc2626; background:linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); padding:0.95rem 1rem; margin-bottom:1.5rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center; gap:1rem; flex-wrap:wrap;">
                            <div>
                                <div style="font-size:0.8rem; color:#fca5a5; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;">⭐ Best Match</div>
                                <h3 style="margin:0.2rem 0; color:#f8fafc; font-size:1.2rem;">{best_club_fit['club']}</h3>
                                <div style="color:#fecaca; font-size:0.92rem; margin-top:0.3rem;">{best_club_fit['explanation']}</div>
                            </div>
                            <div style="background:#dc2626; color:white; border-radius:0.9rem; padding:0.75rem 1rem; text-align:center; min-width:7rem;">
                                <div style="font-size:0.77rem; opacity:0.9;">Club Fit Score</div>
                                <div style="font-size:1.4rem; font-weight:700;">{best_club_fit['fit_score']}/100</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                # Display top 5 recommendations with horizontal bars
                st.markdown("<div class='section-title'>Top 5 Club Matches</div>", unsafe_allow_html=True)
                
                for idx, recommendation in enumerate(recommendations, 1):
                    col1, col2, col3 = st.columns([2, 3, 1])
                    
                    with col1:
                        st.markdown(
                            f"""
                            <div style="padding:0.5rem 0;">
                                <div style="font-weight:700; color:#f8fafc; font-size:0.95rem;">#{idx} {recommendation['club']}</div>
                                <div style="color:#94a3b8; font-size:0.85rem; margin-top:0.2rem; line-height:1.3;">{recommendation['explanation']}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    
                    with col2:
                        # Horizontal progress bar
                        fit_score = recommendation['fit_score']
                        bar_color = "#10b981" if fit_score >= 80 else "#f59e0b" if fit_score >= 65 else "#ef4444"
                        st.markdown(
                            f"""
                            <div style="margin-top:0.5rem;">
                                <div style="background:#1e293b; height:32px; border-radius:0.5rem; overflow:hidden; position:relative;">
                                    <div style="background:{bar_color}; height:100%; width:{fit_score}%; display:flex; align-items:center; justify-content:flex-end; padding-right:0.5rem;">
                                        <span style="color:white; font-weight:700; font-size:0.9rem;">{fit_score}%</span>
                                    </div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    
                    with col3:
                        confidence_color = "#10b981" if recommendation['confidence'] >= 75 else "#f59e0b" if recommendation['confidence'] >= 60 else "#ef4444"
                        st.markdown(
                            f"""
                            <div style="text-align:center; padding-top:0.5rem;">
                                <div style="color:{confidence_color}; font-weight:700; font-size:0.85rem;">Confidence</div>
                                <div style="color:{confidence_color}; font-weight:700; font-size:1rem;">{recommendation['confidence']:.0f}%</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    
                    # Display weaknesses if any
                    if recommendation['weaknesses']:
                        st.markdown(
                            f"""
                            <div style="background:#1e293b; border-left:3px solid #f59e0b; padding:0.6rem 0.8rem; border-radius:0.3rem; margin:0.6rem 0; font-size:0.85rem; color:#e2e8f0;">
                                <strong style="color:#fbbf24;">Potential Weaknesses:</strong><br/>
                                {f'<br/>'.join([f'• {w}' for w in recommendation['weaknesses']])}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                    
                    st.divider()

    elif active_tab == "📄 Scouting Reports":
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
