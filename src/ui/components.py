"""Reusable UI components and helpers"""

from typing import Union

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


def get_tab_labels() -> list[str]:
    """Return the internal tab labels used for the scouting platform navigation."""
    return ["Dashboard", "Player Profile", "Compare Players", "Similarity Search", "Club Fit Engine", "Scouting Reports"]


def get_navigation_options() -> list[str]:
    """Return the visible radio-button labels for the app navigation."""
    return ["🏠 Dashboard", "👤 Player Profile", "📊 Compare Players", "🔍 Similarity Search", "🏟️ Club Fit Engine", "📄 Scouting Reports"]
