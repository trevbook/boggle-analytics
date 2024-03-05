"""
This file will run through a quick data pipeline to download data from Google Drive, 
and then prepare it for use in the app.
"""

# =====
# SETUP
# =====
# The code below will help to set up the rest of the file.

# General import statements
import pandas as pd
import json
from pathlib import Path

# Importing custom-built modules
from utils.google_drive import generate_credentials, download_google_sheet_as_excel

# ============================
# DEFINING THE PIPELINE METHOD
# ============================
# I'll declare the pipeline as a method, so that it can be run whenever we want to update the data.


def run_pipeline():
    """
    This method will run the data pipeline for the Boggle Analytics app, which downloads the data from Google Sheets
    and then prepares it for use in the app.
    """

    # Ensure that the data/ Path exists
    Path("data").mkdir(exist_ok=True, parents=True)

    # Indicate the spreadsheet ID and the save path
    spreadsheet_id = "1NQq_ZU5Sw4CX9-hP7OZbiVwLkVHE0fp7grb54cKgdTM"
    save_path = "data/boggle-game-records.xlsx"

    # Run the function to download the Google Sheet as an Excel file
    download_google_sheet_as_excel(spreadsheet_id, save_path)

    # Loading in the original data
    raw_boggle_data_df = pd.read_excel("data/boggle-game-records.xlsx")

    # Make a copy of the original data, which we'll add new columns to
    boggle_data_df = raw_boggle_data_df.copy()

    # Add a "point_overlap" column, which indicates how many points Trevor and Sarah have in common
    boggle_data_df["point_overlap"] = boggle_data_df.apply(
        lambda row: row.trevor_points_potential - row.trevor_points_scored, axis=1
    )

    # Add a "sarah_points_potential" column, which indicates how many points Sarah could have gotten
    boggle_data_df["sarah_points_potential"] = boggle_data_df.apply(
        lambda row: row.sarah_points_scored + row.point_overlap, axis=1
    )

    # Create a new DataFrame that aggregates game-level information
    game_level_stats_df = (
        boggle_data_df.groupby("game_date")
        .agg(
            trevor_total_points=("trevor_points_scored", "sum"),
            trevor_min_scoring_round=("trevor_points_scored", "min"),
            trevor_max_scoring_round=("trevor_points_scored", "max"),
            sarah_total_points=("sarah_points_scored", "sum"),
            sarah_min_scoring_round=("sarah_points_scored", "min"),
            sarah_max_scoring_round=("sarah_points_scored", "max"),
            trevor_points_list=("trevor_points_scored", list),
            sarah_points_list=("sarah_points_scored", list),
        )
        .reset_index()
    )

    # Add a column indicating the winner of each game
    game_level_stats_df["winner"] = game_level_stats_df.apply(
        lambda row: (
            "Trevor" if row.trevor_total_points > row.sarah_total_points else "Sarah"
        ),
        axis=1,
    )
    
    # Add an "id" column to the game-level stats (which is just a number from 0 to n-1)
    game_level_stats_df["id"] = range(len(game_level_stats_df))

    # Save both the round-level and game-level stats as Excel file
    boggle_data_df.to_excel("data/round-level-stats.xlsx", index=False)
    game_level_stats_df.to_excel("data/game-level-stats.xlsx", index=False)


# ====================
# RUNNING THE PIPELINE
# ====================
# If this file is run directly, then we'll run the pipeline.

if __name__ == "__main__":
    run_pipeline()
    print("Pipeline has been run successfully!")
