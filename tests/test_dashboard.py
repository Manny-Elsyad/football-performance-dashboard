from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import (
    DATA_PATH,
    build_advanced_metrics,
    build_kpi_summary,
    build_player_comparison_charts,
    build_player_profile,
    build_similarity_search,
    build_scouting_report,
    build_winger_scoring,
    calculate_percentiles,
    filter_players,
    get_tab_labels,
    load_data,
)


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
        "Scouting Reports",
    ]


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


def test_build_scouting_report_returns_bytes():
    df = load_data()
    profile = build_player_profile(df, "Lamine Yamal")
    similarity = build_similarity_search(df, "Lamine Yamal")
    report = build_scouting_report(profile, similarity)
    assert isinstance(report, bytes)
    assert b"Scouting Report" in report
