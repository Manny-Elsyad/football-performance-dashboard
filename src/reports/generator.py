"""Scouting report generation logic"""


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
