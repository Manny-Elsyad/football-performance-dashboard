"""Club fit recommendation engine"""

import pandas as pd
import numpy as np

from src.analytics import build_advanced_metrics, build_winger_scoring
from src.clubs.profiles import CLUB_PROFILES, list_clubs


def normalize_metric(value: float, min_val: float = 0, max_val: float = 10) -> float:
    """Normalize a metric to 0-100 scale."""
    if max_val == min_val:
        return 50.0
    normalized = ((value - min_val) / (max_val - min_val)) * 100
    return max(0, min(100, normalized))


def calculate_club_fit_score(player_profile: dict, club_name: str, all_players_df: pd.DataFrame) -> dict:
    """Calculate club fit score for a player based on club tactical profile and player metrics.
    
    Returns a dict with fit_score, confidence, explanation, and weaknesses.
    """
    club_profile = CLUB_PROFILES.get(club_name)
    if not club_profile:
        return {"fit_score": 0, "confidence": 0, "explanation": "", "weaknesses": []}
    
    # Build advanced metrics on the full dataframe to get bounds
    df_with_metrics = build_advanced_metrics(all_players_df.copy())
    df_with_metrics = build_winger_scoring(df_with_metrics)
    
    # Compute normalization bounds from all players
    metric_bounds = {
        "goals_per_90": (df_with_metrics["GoalsPer90"].min(), df_with_metrics["GoalsPer90"].max()),
        "assists_per_90": (df_with_metrics["AssistsPer90"].min(), df_with_metrics["AssistsPer90"].max()),
        "progressive_carries": (df_with_metrics["ProgressiveCarries"].min(), df_with_metrics["ProgressiveCarries"].max()),
        "successful_dribbles": (df_with_metrics["SuccessfulDribbles"].min(), df_with_metrics["SuccessfulDribbles"].max()),
        "key_passes": (df_with_metrics["KeyPasses"].min(), df_with_metrics["KeyPasses"].max()),
        "xg": (df_with_metrics["xG"].min(), df_with_metrics["xG"].max()),
        "xa": (df_with_metrics["xA"].min(), df_with_metrics["xA"].max()),
    }
    
    # Normalize player metrics - player_profile is a dict with computed metrics
    player_metrics = {
        "goals_per_90": normalize_metric(
            float(player_profile.get("GoalsPer90", 0)),
            metric_bounds["goals_per_90"][0],
            metric_bounds["goals_per_90"][1],
        ),
        "assists_per_90": normalize_metric(
            float(player_profile.get("AssistsPer90", 0)),
            metric_bounds["assists_per_90"][0],
            metric_bounds["assists_per_90"][1],
        ),
        "progressive_carries": normalize_metric(
            float(player_profile.get("ProgressiveCarries", 0)),
            metric_bounds["progressive_carries"][0],
            metric_bounds["progressive_carries"][1],
        ),
        "successful_dribbles": normalize_metric(
            float(player_profile.get("SuccessfulDribbles", 0)),
            metric_bounds["successful_dribbles"][0],
            metric_bounds["successful_dribbles"][1],
        ),
        "key_passes": normalize_metric(
            float(player_profile.get("KeyPasses", 0)),
            metric_bounds["key_passes"][0],
            metric_bounds["key_passes"][1],
        ),
        "xg": normalize_metric(
            float(player_profile.get("xG", 0)),
            metric_bounds["xg"][0],
            metric_bounds["xg"][1],
        ),
        "xa": normalize_metric(
            float(player_profile.get("xA", 0)),
            metric_bounds["xa"][0],
            metric_bounds["xa"][1],
        ),
    }
    
    # Calculate fit score based on club preferences and player metrics
    club_metric_prefs = club_profile["metric_preferences"]
    fit_score = 0.0
    total_weight = 0.0
    
    for metric, preference_weight in club_metric_prefs.items():
        player_metric_value = player_metrics.get(metric, 50)
        fit_score += player_metric_value * preference_weight
        total_weight += preference_weight
    
    if total_weight > 0:
        fit_score = fit_score / total_weight
    
    # Calculate confidence based on how well player's strengths align with club's needs
    alignment_score = 0.0
    if player_metrics["progressive_carries"] > 70 and club_metric_prefs["progressive_carries"] > 0.15:
        alignment_score += 10
    if player_metrics["key_passes"] > 70 and club_metric_prefs["key_passes"] > 0.15:
        alignment_score += 10
    if player_metrics["successful_dribbles"] > 70 and club_metric_prefs["successful_dribbles"] > 0.12:
        alignment_score += 10
    if player_metrics["goals_per_90"] > 70 and club_metric_prefs["goals_per_90"] > 0.15:
        alignment_score += 10
    if player_metrics["assists_per_90"] > 70 and club_metric_prefs["assists_per_90"] > 0.12:
        alignment_score += 10
    
    confidence = min(100, 50 + alignment_score)
    
    # Generate explanation
    strengths_list = []
    if player_metrics["progressive_carries"] > 65:
        strengths_list.append("progressive carry excellence")
    if player_metrics["successful_dribbles"] > 65:
        strengths_list.append("elite dribbling")
    if player_metrics["key_passes"] > 65:
        strengths_list.append("creative playmaking")
    if player_metrics["goals_per_90"] > 65:
        strengths_list.append("goal-scoring threat")
    if player_metrics["assists_per_90"] > 65:
        strengths_list.append("assist-generating ability")
    
    explanation = f"{player_profile['Player']} aligns well with {club_name}'s {club_profile['philosophy'].lower()} through "
    if strengths_list:
        explanation += ", ".join(strengths_list[:2])
    else:
        explanation += "overall tactical profile"
    explanation += "."
    
    # Generate weaknesses
    weaknesses = []
    if player_metrics["progressive_carries"] < 40 and club_metric_prefs["progressive_carries"] > 0.15:
        weaknesses.append("Limited ball progression compared to club expectations")
    if player_metrics["key_passes"] < 40 and club_metric_prefs["key_passes"] > 0.15:
        weaknesses.append("Below-average creativity for this possession-focused system")
    if player_metrics["goals_per_90"] < 30 and club_metric_prefs["goals_per_90"] > 0.15:
        weaknesses.append("Lower goal output than typical for this club's attacking profile")
    if player_metrics["successful_dribbles"] < 35 and club_metric_prefs["successful_dribbles"] > 0.12:
        weaknesses.append("Less dribbling impact than ideal for this attacking model")
    
    return {
        "fit_score": round(fit_score, 1),
        "confidence": round(confidence, 1),
        "explanation": explanation,
        "weaknesses": weaknesses[:2],  # Top 2 weaknesses
    }


def get_club_recommendations(player_profile: dict, all_players_df: pd.DataFrame) -> list[dict]:
    """Get the top 5 club recommendations for a player.
    
    Returns a list of dicts with club name, fit score, confidence, etc.
    """
    recommendations = []
    clubs = list_clubs()
    
    for club in clubs:
        fit_data = calculate_club_fit_score(player_profile, club, all_players_df)
        recommendations.append({
            "club": club,
            "fit_score": fit_data["fit_score"],
            "confidence": fit_data["confidence"],
            "explanation": fit_data["explanation"],
            "weaknesses": fit_data["weaknesses"],
        })
    
    # Sort by fit score descending
    recommendations.sort(key=lambda x: x["fit_score"], reverse=True)
    return recommendations[:5]


def get_best_club(player_profile: dict, all_players_df: pd.DataFrame) -> dict:
    """Get the best club fit for a player."""
    recommendations = get_club_recommendations(player_profile, all_players_df)
    if recommendations:
        return recommendations[0]
    return {}
