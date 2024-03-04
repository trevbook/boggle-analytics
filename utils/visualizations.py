"""
This app contains code for generating various visualizations. 
"""

# =====
# SETUP
# =====
# The code below will help to set up the rest of the app.

# General import statements
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Importing specific settings
from utils.settings import TREVOR_COLOR, SARAH_COLOR

# =====================
# VISUALIZATION METHODS
# =====================
# Each of the methods below will generate a different visualization.


def percentage_of_total_points_scored_line_graph(
    round_level_stats_df: pd.DataFrame,
    show_each_round: bool = False,
    show_dates: bool = False,
    show_rolling_avg: bool = True,
    rolling_avg_window_size: int = 15,
    hide_legend: bool = False,
    disabled_zoom: bool = True,
    plot_height: int = 350,
):
    """
    This method will generate a line graph comparing the percentage of total points scored by Trevor and Sarah.

    Args:
        - round_level_stats_df (pd.DataFrame): A DataFrame containing round-level statistics.
        - show_each_round (bool): Whether or not to show each round's data points.
        - show_dates (bool): Whether or not to show the dates on the x-axis.
        - show_rolling_avg (bool): Whether or not to show a rolling average line.
        - rolling_avg_window_size (int): The size of the window for the rolling average.
        - hide_legend (bool): Whether or not to hide the legend.
        - disabled_zoom (bool): Whether or not to disable the zoom functionality.
        - plot_height (int): The height of the plot.
    """

    # Make a copy of the round level stats, and add some important columns
    pct_of_total_df = round_level_stats_df.copy()
    pct_of_total_df["trevor_pct_total"] = (
        pct_of_total_df["trevor_points_scored"]
        / pct_of_total_df["total_points_scorable"]
    )
    pct_of_total_df["sarah_pct_total"] = (
        pct_of_total_df["sarah_points_scored"]
        / pct_of_total_df["total_points_scorable"]
    )
    pct_of_total_df["game_id"] = pct_of_total_df.apply(
        lambda row: f"{row.game_date}-round-{row.round_num}", axis=1
    )

    # Compute moving averages
    pct_of_total_df["trevor_pct_total_smooth"] = (
        pct_of_total_df["trevor_pct_total"]
        .rolling(window=rolling_avg_window_size, min_periods=1)
        .mean()
    )
    pct_of_total_df["sarah_pct_total_smooth"] = (
        pct_of_total_df["sarah_pct_total"]
        .rolling(window=rolling_avg_window_size, min_periods=1)
        .mean()
    )

    # Convert game_date to datetime and create a new column for x-axis labels
    pct_of_total_df["game_date"] = pd.to_datetime(pct_of_total_df["game_date"])
    pct_of_total_df["x_axis_label"] = pct_of_total_df["game_date"].dt.strftime("%B %Y")

    # Sort by the game_date and round_num
    pct_of_total_df = pct_of_total_df.sort_values(
        by=["game_date", "round_num"], ascending=[True, True]
    )

    # Make the Plotly figure
    pct_of_total_fig = go.Figure()

    # If the user wants to show each round, then add the data points
    if show_each_round:

        # Add Trevor's line
        pct_of_total_fig.add_trace(
            go.Scatter(
                x=pct_of_total_df["game_id"],
                y=pct_of_total_df["trevor_pct_total"],
                mode="lines",
                name="Trevor",
                line=dict(color=TREVOR_COLOR),
                opacity=0.3,
                showlegend=False,
            )
        )

        # Add Sarah's line
        pct_of_total_fig.add_trace(
            go.Scatter(
                x=pct_of_total_df["game_id"],
                y=pct_of_total_df["sarah_pct_total"],
                mode="lines",
                name="Sarah",
                line=dict(color=SARAH_COLOR),
                opacity=0.3,
                showlegend=False,
            )
        )

    # If the user wants to show the rolling average, then add the smoothed lines
    if show_rolling_avg:

        # Add Trevor's smoothed line
        pct_of_total_fig.add_trace(
            go.Scatter(
                x=pct_of_total_df["game_id"],
                y=pct_of_total_df["trevor_pct_total_smooth"],
                mode="lines",
                name="Trevor",
                line=dict(color=TREVOR_COLOR, width=4),
            )
        )

        # Add Sarah's smoothed line
        pct_of_total_fig.add_trace(
            go.Scatter(
                x=pct_of_total_df["game_id"],
                y=pct_of_total_df["sarah_pct_total_smooth"],
                mode="lines",
                name="Sarah",
                line=dict(color=SARAH_COLOR, width=4),
            )
        )

    # Update the styling to remove the backgoround grid
    FIGURE_MARGIN = 15
    pct_of_total_fig.update_layout(
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=FIGURE_MARGIN, r=FIGURE_MARGIN, t=FIGURE_MARGIN, b=75),
    )

    # Make the legend appear in the top-right corner of the graph
    pct_of_total_fig.update_layout(
        legend=dict(x=1, y=1, xanchor="right", yanchor="top")
    )

    # Determine the maximum y-value, and set the y-axis range to be between 0 and the maximum y-value
    max_y_value = pct_of_total_df[["trevor_pct_total", "sarah_pct_total"]].max().max()
    pct_of_total_fig.update_yaxes(range=[0, max_y_value])

    # Add the title of the y-axis ("% of Total Points Scored")
    pct_of_total_fig.update_yaxes(title_text="% of Total Points Scored")

    # Change the y-axis to be percentage with 0 decimal places
    pct_of_total_fig.update_yaxes(tickformat=".0%")

    # If the legend should be hidden, then hide it
    if hide_legend:
        pct_of_total_fig.update_layout(showlegend=False)

    # If we want to disable zoom, then disable it
    if disabled_zoom:
        pct_of_total_fig.update_layout(
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
        )

    # Make the plot height equal to the input
    pct_of_total_fig.update_layout(height=plot_height)

    # If the user wants to show the dates, then update the x-axis to show the dates
    if show_dates:

        # Get the first appearance of each month
        first_appearance_of_month_df = pct_of_total_df[
            ["game_id", "x_axis_label", "trevor_pct_total"]
        ].drop_duplicates(subset=["x_axis_label"], keep="first")

        # Update the x-axis to use the x_axis_label column
        pct_of_total_fig.update_xaxes(
            tickvals=first_appearance_of_month_df["game_id"],
            ticktext=first_appearance_of_month_df["x_axis_label"],
        )

        # Add a vertical line for each first appearance of a month
        for _, row in first_appearance_of_month_df.iterrows():
            pct_of_total_fig.add_shape(
                dict(
                    type="line",
                    x0=row["game_id"],
                    x1=row["game_id"],
                    y0=0,
                    y1=1,
                    line=dict(color="black", width=1, dash="dot"),
                )
            )

    # Otherwise, we'll hide the dates
    else:
        pct_of_total_fig.update_xaxes(showticklabels=False)

    # Return the figure
    return pct_of_total_fig
