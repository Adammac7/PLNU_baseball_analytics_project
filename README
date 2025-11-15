⚾ PLNU Baseball Analytics Project

A lightweight toolkit for pitch-by-pitch data visualization and player performance analytics.
This repo helps analyze CSV datasets of pitch and plate data, building interactive strike zone plots, bar charts, and player summaries — perfect for exploratory baseball analysis.

📂 Repository Overview
File	Description
barchart.py	Core script defining Pitch, Batter, and Pitcher classes. Loads a master CSV, constructs objects, and generates Plotly visualizations (barchart.html, strikezone.html).
strikezone.py	Alternate implementation of strike-zone utilities. Includes get_zone_number, create_strike_zone_plot, and create_strike_zone_plot_from_pitches for pandas DataFrames and Batter objects.
🧠 How It Works

Read & Parse a pitch-by-pitch CSV (e.g. Regular Season Master CSV.csv)

Build Object Models for pitchers, batters, and individual pitches

Compute Per-Zone Metrics: AVG, SLG, Exit Velo, Whiff Rate

Render Visualizations: Interactive strike-zone heatmaps & bar charts

🧩 Key Classes & Functions
barchart.py

Pitch – Holds individual pitch data (location, type, speed, spin, outcome).

Batter – Aggregates stats across all pitches faced; computes AVG, OBP, SLG, OPS, wOBA (placeholder).

Methods: add_pitch(), calculate_stats(), get_stats()

Pitcher – Summarizes pitch mix, average velocity, spin, etc.

Common Utilities

get_zone_number(x, y, zone_width, zone_height_low, zone_height_high) → returns a 1–16 zone index (4×4 grid).

create_strike_zone_plot() / create_strike_zone_plot_from_pitches() → generate Plotly figures for zone analysis.

⚙️ Requirements

Install dependencies in a virtual environment:

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install pandas numpy plotly matplotlib


Required packages

pandas

numpy

plotly

Optional

matplotlib (for color map helpers in barchart.py)

▶️ How to Run

Place your CSV file (Regular Season Master CSV.csv) in the repo root.

Open barchart.py → edit the Battername variable (example: "Entrekin, Jake").

Run from PowerShell:

python barchart.py


Output:

barchart.html → Bar chart of hitter performance

strikezone.html → Strike zone heatmap visualization

🧾 Notes & Caveats

Ensure imports (pandas as pd, numpy as np, plotly.graph_objects as go, etc.) exist in your script to avoid NameErrors.

The CSV must contain the following headers:
Batter, Pitcher, TaggedPitchType, AutoPitchType, PitchCall, RelSpeed, SpinRate, InducedVertBreak, Angle, ExitSpeed, TaggedHitType, PlayResult, KorBB, PlateLocHeight, PlateLocSide.

wOBA currently uses placeholder weights — replace with league-specific constants for accuracy.

Debugging prints are included; replace with logging for production.

The strike zone uses an assumed coordinate system (PlateLocSide = horizontal, PlateLocHeight = vertical, both in feet).

Zone width ≈ 17 in × 0.0833 ft/in.
