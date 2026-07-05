from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import DATA_PATH, build_kpi_summary, filter_players, load_data


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
