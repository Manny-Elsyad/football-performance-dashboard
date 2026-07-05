# Football Scouting Platform

A premium football scouting platform built with Python, Streamlit, Pandas, and Plotly. It brings together a polished dashboard experience, player profiling, side-by-side comparison tools, similarity search, and a scouting report generator for recruiter-style analysis.

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
- Tabbed platform structure for Dashboard, Player Profile, Compare Players, Similarity Search, and Scouting Reports
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

- `app.py` – main Streamlit application with the tabbed scouting platform
- `data/players.csv` – sample football player dataset
- `tests/` – automated validation for the dashboard logic and scouting workflows

## Recruiter-Friendly Notes

This project demonstrates:
- data preparation and transformation with Pandas
- dashboard design and user experience with Streamlit
- interactive analytics and storytelling with Plotly
- software engineering habits such as testing, documentation, and modular code

## Push to GitHub

```bash
git remote add origin https://github.com/mannyelsyad/football-performance-dashboard.git
git push -u origin main
```
