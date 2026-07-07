from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analytics import (
    build_advanced_metrics,
    build_kpi_summary,
    build_player_profile,
    build_winger_scoring,
    calculate_percentiles,
)
from src.clubs import get_best_club, get_club_recommendations, list_clubs
from src.data import DATA_PATH, filter_players, load_data
from src.reports import build_scouting_report
from src.similarity import build_similarity_search
from src.ui import get_score_badge, get_tab_labels
from src.visualizations import build_player_comparison_charts


def test_data_file_exists():
    assert Path(DATA_PATH).exists(), "The sample dataset should exist."


def test_load_data_returns_expected_columns():
    df = load_data()
    expected_columns = {
        "Player",
        "Team",
        "Position",
        "Age",
        "Matches",
        "Goals",
        "Assists",
        "PassesCompleted",
        "PassingAccuracy",
        "Tackles",
        "Interceptions",
        "DistanceCoveredKm",
        "MinutesPlayed",
        "Nationality",
    }
    assert expected_columns.issubset(set(df.columns))
    assert not df.empty


def test_load_data_supports_real_dataset():
    df = load_data("Real Dataset")
    assert not df.empty
    assert {"Player", "Team", "Position", "MinutesPlayed", "Goals", "Assists"}.issubset(set(df.columns))


def test_filter_players_applies_filters():
    df = load_data()
    filtered = filter_players(
        df,
        position="Forward",
        team="FC Barcelona",
        min_minutes=1500,
        min_goals=5,
    )
    assert not filtered.empty
    assert filtered["Position"].eq("Forward").all()
    assert filtered["Team"].eq("FC Barcelona").all()
    assert (filtered["MinutesPlayed"] >= 1500).all()
    assert (filtered["Goals"] >= 5).all()


def test_build_kpi_summary_returns_expected_metrics():
    df = load_data()
    summary = build_kpi_summary(df)
    assert set(summary.keys()) == {
        "Goals",
        "Assists",
        "GoalsPer90",
        "AssistsPer90",
        "GoalContributionsPer90",
    }
    assert summary["Goals"] >= 0
    assert summary["Assists"] >= 0


def test_build_advanced_metrics_returns_expected_columns():
    df = load_data()
    advanced_df = build_advanced_metrics(df)
    expected_columns = {
        "GoalsPer90",
        "AssistsPer90",
        "GoalContributionsPer90",
        "ProgressiveCarriesPer90",
        "SuccessfulDribblesPer90",
        "KeyPassesPer90",
        "xGPer90",
        "xAPer90",
    }
    assert expected_columns.issubset(set(advanced_df.columns))
    assert not advanced_df.empty


def test_build_winger_scoring_returns_expected_score_range():
    df = load_data()
    scored_df = build_winger_scoring(df)
    assert "WingerScoutingScore" in scored_df.columns
    assert scored_df["WingerScoutingScore"].between(0, 100).all()


def test_build_player_comparison_charts_returns_expected_objects():
    df = load_data()
    charts = build_player_comparison_charts(df, ["Lamine Yamal", "Vinicius Junior"])
    assert len(charts) == 2
    assert all(chart is not None for chart in charts)


def test_build_similarity_search_returns_five_players():
    df = load_data()
    similar = build_similarity_search(df, "Lamine Yamal")
    assert len(similar) == 5
    assert all("Player" in row for row in similar)


def test_calculate_percentiles_returns_expected_range():
    df = load_data()
    percentile_df = calculate_percentiles(df)
    assert "Percentile" in percentile_df.columns
    assert percentile_df["Percentile"].between(0, 100).all()


def test_get_tab_labels_returns_expected_tabs():
    assert get_tab_labels() == [
        "Dashboard",
        "Player Profile",
        "Compare Players",
        "Similarity Search",
        "Club Fit Engine",
        "Scouting Reports",
    ]


def test_get_score_badge_returns_expected_labels():
    assert get_score_badge(92) == ("Elite", "#22c55e")
    assert get_score_badge(74) == ("Strong", "#38bdf8")
    assert get_score_badge(48) == ("Monitor", "#f59e0b")


def test_build_player_profile_returns_expected_keys():
    df = load_data()
    profile = build_player_profile(df, "Lamine Yamal")
    assert profile["Player"] == "Lamine Yamal"
    assert "Strengths" in profile
    assert "Weaknesses" in profile


def test_build_player_profile_includes_recommendation_fields():
    df = load_data()
    profile = build_player_profile(df, "Lamine Yamal")
    assert "Recommendation" in profile
    assert "Fit" in profile


def test_build_player_profile_includes_demographics_and_percentiles():
    df = load_data()
    profile = build_player_profile(df, "Lamine Yamal")
    assert "Age" in profile
    assert "Nationality" in profile
    assert "Percentiles" in profile
    assert "RadarMetrics" in profile


def test_build_scouting_report_returns_bytes():
    df = load_data()
    profile = build_player_profile(df, "Lamine Yamal")
    similarity = build_similarity_search(df, "Lamine Yamal")
    report = build_scouting_report(profile, similarity)
    assert isinstance(report, bytes)
    assert b"Scouting Report" in report


def test_list_clubs_returns_expected_clubs():
    clubs = list_clubs()
    assert len(clubs) == 10
    expected_clubs = {
        "Manchester City",
        "Arsenal",
        "Liverpool",
        "Brighton",
        "Barcelona",
        "Real Madrid",
        "Bayer Leverkusen",
        "Bayern Munich",
        "Inter Milan",
        "Paris Saint-Germain",
    }
    assert set(clubs) == expected_clubs


def test_get_club_recommendations_returns_five_clubs():
    df = load_data()
    profile = build_player_profile(df, "Lamine Yamal")
    recommendations = get_club_recommendations(profile, df)
    assert len(recommendations) == 5
    assert all("club" in rec for rec in recommendations)
    assert all("fit_score" in rec for rec in recommendations)
    assert all("confidence" in rec for rec in recommendations)


def test_get_club_recommendations_fit_scores_valid_range():
    df = load_data()
    profile = build_player_profile(df, "Lamine Yamal")
    recommendations = get_club_recommendations(profile, df)
    assert all(0 <= rec["fit_score"] <= 100 for rec in recommendations)
    assert all(recommendations[i]["fit_score"] >= recommendations[i + 1]["fit_score"] for i in range(len(recommendations) - 1))


def test_get_best_club_returns_top_recommendation():
    df = load_data()
    profile = build_player_profile(df, "Lamine Yamal")
    best = get_best_club(profile, df)
    assert "club" in best
    assert "fit_score" in best
    assert best["fit_score"] >= 0
    assert best["fit_score"] <= 100


def test_club_fit_works_with_real_dataset():
    df = load_data("Real Dataset")
    profile = build_player_profile(df, df["Player"].iloc[0])
    recommendations = get_club_recommendations(profile, df)
    assert len(recommendations) == 5
    assert all(rec["fit_score"] >= 0 for rec in recommendations)
