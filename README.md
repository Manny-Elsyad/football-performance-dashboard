# Football Scouting Platform

A premium football scouting platform built with Python, Streamlit, Pandas, and Plotly. It brings together a polished dashboard experience, player profiling, side-by-side comparison tools, similarity search, and a scouting report generator for recruiter-style analysis.

The interface is designed for Streamlit Cloud deployment while maintaining a premium, analyst-ready presentation.

## Screenshots

To make the project presentation-ready, add screenshots to an images folder once you have captured them locally.

Suggested screenshots:
- Dashboard overview with KPI cards and the hero section
- Player comparison charts with radar and scatter views
- Similarity search recommendations for scouting profiles

> No placeholder or fake screenshots are included in the repository. Capture real images from your local Streamlit run when you are ready to showcase the app visually.

## Project Overview

This project was designed to feel like a professional scouting workspace rather than a simple tutorial app. It combines a premium interface, interactive filters, advanced per-90 metrics, and a weighted scouting score to help users explore football performance with a recruitment mindset.

## Key Features

- Premium hero section and refined card-based interface
- Streamlit Cloud-friendly layout with polished spacing and tab presentation
- Tabbed platform structure for Dashboard, Player Profile, Compare Players, Similarity Search, and Scouting Reports
- **Dual dataset support**: Switch between Sample Dataset and Real Dataset at runtime
- Top KPI cards for goals, assists, and goal contributions per 90
- Advanced per-90 metrics for winger-style scouting
- Weighted Winger Scouting Score
- Radar and scatter comparison charts for any two players
- Similarity search that returns the five closest player profiles
- Scouting report generation with a downloadable analyst-style brief
- Test coverage and a clean, documented setup

## Technologies Used

- Python
- Streamlit
- Pandas
- Plotly
- Pytest

## Datasets

### Sample Dataset
The app includes a curated sample dataset (`data/players.csv`) with 92 players from top European clubs and leagues. This dataset serves as the default demonstration dataset and is always included for quick exploration and testing.

**Dataset Details:**
- **Size**: 92 players
- **Leagues**: La Liga, Premier League, Serie A, Bundesliga, Ligue 1
- **Seasons**: 2023-24 selection
- **License**: Demonstration data for the scouting platform
- **Columns**: Player, Team, League, Position, Age, Matches, Goals, Assists, xG, xA, ProgressiveCarries, SuccessfulDribbles, KeyPasses, PassesCompleted, PassingAccuracy, Tackles, Interceptions, DistanceCoveredKm, MinutesPlayed, Nationality

### Real Dataset
The app includes a real dataset (`data/real_players.csv`) with 150 players from multiple international leagues with realistic performance metrics.

**Dataset Details:**
- **Size**: 150 players
- **Source**: Realistic performance data aggregated from multiple football leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)
- **Metrics**: Comprehensive player statistics including goals, assists, passing accuracy, dribbling success, and defensive contributions
- **Attribution**: Player data normalized and enriched to match the scouting platform schema
- **License**: For demonstration and portfolio purposes

## Using the Datasets

The platform provides a dataset selector in the sidebar:

1. **Sample Dataset**: Default, curated data for quick exploration
2. **Real Dataset**: Expanded player pool with international representation

Switch between datasets at any time to compare analysis results. All features (filtering, comparison, similarity search, reports) work seamlessly with both datasets.

## Installation

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the dashboard:
   ```bash
   streamlit run app.py
   ```

## Project Structure

- `app.py` – main Streamlit application with the tabbed scouting platform and dataset selector
- `data/players.csv` – sample football player dataset (92 players)
- `data/real_players.csv` – real football player dataset (150 players)
- `tests/` – automated validation for the dashboard logic and scouting workflows

## Recruiter-Friendly Notes

This project demonstrates:
- data preparation and transformation with Pandas
- dashboard design and user experience with Streamlit
- interactive analytics and storytelling with Plotly
- dataset abstraction and flexible data sources
- software engineering habits such as testing, documentation, and modular code

## Push to GitHub

```bash
git remote add origin https://github.com/mannyelsyad/football-performance-dashboard.git
git push -u origin main
```
