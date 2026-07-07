"""Player similarity search logic"""

import pandas as pd

from src.analytics import build_winger_scoring


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
