"""Scouting metrics and analytics calculations"""

import pandas as pd


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
