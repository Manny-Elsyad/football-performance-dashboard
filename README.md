# Football Scouting & Winger Analytics Dashboard

A portfolio-quality football scouting dashboard built with Python, Streamlit, Pandas, and Plotly. It showcases how data can be used to evaluate winger-style attacking profiles, compare players, and surface similarity-based scouting insights.

## Screenshots

To make the project presentation-ready, add screenshots to an images folder once you have captured them locally.

Suggested screenshots:
- Dashboard overview with KPI cards and the hero section
- Player comparison charts with radar and scatter views
- Similarity search recommendations for scouting profiles

> No placeholder or fake screenshots are included in the repository. Capture real images from your local Streamlit run when you are ready to showcase the app visually.

## Project Overview

This project was designed to feel like a real scouting tool rather than a simple tutorial app. It combines clean UI design, interactive filters, advanced per-90 metrics, and a weighted scouting score to help users explore football performance with a recruitment mindset.

## Key Features

- Modern, professional Streamlit interface
- Top KPI cards for goals, assists, and goal contributions per 90
- Advanced per-90 metrics for winger-style scouting
- Weighted Winger Scouting Score
- Radar and scatter comparison charts for any two players
- Similarity search that returns the five closest player profiles
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

- `app.py` – main Streamlit application
- `data/players.csv` – sample football player dataset
- `tests/` – automated validation for the dashboard logic

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
