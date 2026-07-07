"""Data loading and filtering functions"""

from pathlib import Path
from typing import Optional

import pandas as pd
import streamlit as st


DATA_PATH = Path(__file__).parent.parent.parent / "data" / "players.csv"
REAL_DATA_PATH = Path(__file__).parent.parent.parent / "data" / "real_players.csv"


@st.cache_data
def load_data(dataset_source: str = "Sample Dataset") -> pd.DataFrame:
    """Load and preprocess the football player dataset.
    
    Args:
        dataset_source: Either "Sample Dataset" or "Real Dataset"
    """
    # Choose the data path based on the source
    if dataset_source == "Real Dataset":
        path = REAL_DATA_PATH
    else:
        path = DATA_PATH
    
    if path.exists():
        df = pd.read_csv(path)
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
