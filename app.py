"""
This file contains the Plotly Dash app showing off some Boggle analytics. 
"""

# =====
# SETUP
# =====
# The code below will help to set up the rest of the app.

# General import statements
import pandas as pd

# Dash-related import statements
import dash
from dash import html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

# Importing different custom modules
from utils.visualizations import (
    percentage_of_total_points_scored_line_graph,
    win_loss_heatmap,
    round_score_distribution_boxplot,
    total_wins_bar_chart,
)

# Set up the app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

# Load in the data
round_level_stats_df = pd.read_excel("data/round-level-stats.xlsx")
game_level_stats_df = pd.read_excel("data/game-level-stats.xlsx")

# =======================
# DEFINING THE APP LAYOUT
# =======================
# Below, I'm going to define the layout of the app.

# Define some constants for the app layout
ROW_SPAING = "20px"
DEFAULT_ROLLING_AVG_WINDOW_SIZE = 15

# Assign the app layout
app.layout = dbc.Container(
    children=[
        # HEADER
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dmc.Text("Boggle Analytics", size="2rem", weight=700),
                        dmc.Text(
                            "Miscellaneous stats about our performance in Boggle",
                            size="1.25rem",
                            italic=True,
                        ),
                    ],
                    width=12,
                )
            ],
            style={
                "marginBottom": ROW_SPAING,
            },
        ),
        # TOTAL WINS
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dmc.Text(
                            "Total Wins",
                            size="1.5rem",
                            weight=600,
                        ),
                        dcc.Markdown(
                            """
                            This chart shows the total number of games won by each player. 
                            It's a good way to see who's been winning more games overall.
                            """,
                        ),
                        dcc.Graph(
                            id="total-wins-bar-chart",
                            figure=total_wins_bar_chart(
                                game_level_stats_df=game_level_stats_df
                            ),
                            config={"displayModeBar": False},
                        ),
                    ],
                    width=12,
                )
            ],
            style={"marginBottom": ROW_SPAING},
        ),
        # PERCENTAGE OF TOTAL POINTS SCORED
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dmc.Text(
                            "Percentage of Total Points Scored",
                            size="1.5rem",
                            weight=600,
                        ),
                        dcc.Markdown(
                            """
                            This chart normalizes the points scored in each round to the maximum possible points in that round. 
                            It's a good look at how well we're doing over time, and normalizes for the fact that some rounds are just harder than others.
                            """,
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    md=9,
                                    xs=12,
                                    children=[
                                        dcc.Graph(
                                            id="pct-points-scored-line-graph",
                                            figure=percentage_of_total_points_scored_line_graph(
                                                round_level_stats_df=round_level_stats_df,
                                                rolling_avg_window_size=DEFAULT_ROLLING_AVG_WINDOW_SIZE,
                                            ),
                                            config={"displayModeBar": False},
                                        ),
                                    ],
                                    style={"paddingRight": "5px"},
                                ),
                                dbc.Col(
                                    md=3,
                                    xs=12,
                                    children=[
                                        dmc.Text(
                                            "Controls",
                                            size="1.2rem",
                                            weight=500,
                                            style={"marginBottom": "10px"},
                                        ),
                                        html.Div(
                                            [
                                                dmc.Checkbox(
                                                    id="pct-points-scored-show-each-round",
                                                    label="Show Each Round",
                                                    checked=True,
                                                ),
                                            ],
                                            style={"marginBottom": "20px"},
                                        ),
                                        html.Div(
                                            [
                                                dmc.Checkbox(
                                                    id="pct-points-scored-show-dates",
                                                    label="Show Dates",
                                                    checked=False,
                                                ),
                                            ],
                                            style={"marginBottom": "20px"},
                                        ),
                                        html.Div(
                                            [
                                                dmc.Text(
                                                    "Rolling Avg. Window (Rounds)",
                                                    size="0.95rem",
                                                ),
                                                html.Div(
                                                    children=[
                                                        dmc.Slider(
                                                            id="pct-points-scored-rolling-avg-slider",
                                                            value=DEFAULT_ROLLING_AVG_WINDOW_SIZE,
                                                            min=1,
                                                            max=30,
                                                            step=1,
                                                            updatemode="drag",
                                                        ),
                                                    ],
                                                    style={"width": "50%"},
                                                ),
                                            ]
                                        ),
                                    ],
                                ),
                            ]
                        ),
                    ]
                )
            ],
            style={"marginBottom": ROW_SPAING},
        ),
        # WIN-LOSS HEATMAP
        dbc.Row(
            children=[
                dbc.Col(
                    children=[
                        dmc.Text(
                            "Win Streaks",
                            size="1.5rem",
                            weight=600,
                        ),
                        dcc.Markdown(
                            """
                            Below, I've mapped out each of our wins over time. You can see our longest streak of games won!
                            """,
                        ),
                        dbc.Row(
                            children=[
                                dbc.Col(
                                    md=9,
                                    xs=12,
                                    children=[
                                        dcc.Graph(
                                            id="win-loss-heatmap",
                                            figure=win_loss_heatmap(
                                                game_level_stats_df=game_level_stats_df
                                            ),
                                            config={"displayModeBar": False},
                                        ),
                                    ],
                                    style={"paddingRight": "5px"},
                                ),
                                dbc.Col(
                                    md=3,
                                    xs=12,
                                    children=[
                                        dmc.Text(
                                            "Controls",
                                            size="1.2rem",
                                            weight=500,
                                            style={"marginBottom": "10px"},
                                        ),
                                        html.Div(
                                            [
                                                dmc.Checkbox(
                                                    id="win-loss-heatmap-show-longest-streak",
                                                    label="Show Longest Streak",
                                                    checked=True,
                                                ),
                                            ],
                                            style={"marginBottom": "20px"},
                                        ),
                                        html.Div(
                                            [
                                                dmc.Checkbox(
                                                    id="win-loss-heatmap-show-dates",
                                                    label="Show Dates",
                                                    checked=False,
                                                ),
                                            ],
                                            style={"marginBottom": "20px"},
                                        ),
                                    ],
                                ),
                            ]
                        ),
                    ]
                )
            ],
            style={"marginBottom": ROW_SPAING},
        ),
        # SCORING DISTRIBUTION
        dbc.Row(
            children=[
                dbc.Col(
                    width=12,
                    children=[
                        dmc.Text(
                            "Scoring Distribution",
                            size="1.5rem",
                            weight=600,
                        ),
                        dcc.Markdown(
                            """
                            This chart shows the distribution of scores for each round. It's a good way to see how we're doing on average, and how consistent we are.
                            """,
                        ),
                    ],
                ),
                dbc.Col(
                    md=9,
                    xs=12,
                    children=[
                        dcc.Graph(
                            id="round-score-distribution-boxplot",
                            figure=round_score_distribution_boxplot(
                                round_level_stats_df=round_level_stats_df
                            ),
                            config={"displayModeBar": False},
                        ),
                    ],
                    style={"paddingRight": "5px"},
                ),
                dbc.Col(
                    md=3,
                    xs=12,
                    children=[
                        dmc.Text(
                            "Controls",
                            size="1.2rem",
                            weight=500,
                            style={"marginBottom": "10px"},
                        ),
                        html.Div(
                            [
                                dmc.Checkbox(
                                    id="round-score-distribution-boxplot-violin-plot",
                                    label="Violin Plot",
                                    checked=False,
                                ),
                            ],
                            style={"marginBottom": "20px"},
                        ),
                        html.Div(
                            [
                                dmc.Checkbox(
                                    id="round-score-distribution-boxplot-use-potential-points",
                                    label="Use Potential Points",
                                    checked=False,
                                ),
                            ],
                            style={"marginBottom": "20px"},
                        ),
                    ],
                ),
            ]
        ),
    ],
    fluid=True,
    style={
        "paddingLeft": "1.5rem",
        "paddingRight": "1.5rem",
    }
)

# ==========================
# DEFINING THE APP CALLBACKS
# ==========================
# Below, I'm going to define the app callbacks.


@callback(
    output=Output("pct-points-scored-line-graph", "figure"),
    inputs=[
        Input("pct-points-scored-show-each-round", "checked"),
        Input("pct-points-scored-show-dates", "checked"),
        Input("pct-points-scored-rolling-avg-slider", "value"),
    ],
)
def update_pct_points_scored_line_graph(
    show_each_round: bool, show_dates: bool, rolling_avg_window_size: int
):
    """
    This callback will update the "Percentage of Total Points Scored" line graph.

    Args:
        - show_each_round (bool): Whether or not to show each round's data points.
        - show_dates (bool): Whether or not to show the dates on the x-axis.
        - rolling_avg_window_size (int): The size of the window for the rolling average.
    """
    return percentage_of_total_points_scored_line_graph(
        round_level_stats_df=round_level_stats_df,
        show_each_round=show_each_round,
        show_dates=show_dates,
        rolling_avg_window_size=rolling_avg_window_size,
    )


@callback(
    output=Output("win-loss-heatmap", "figure"),
    inputs=[
        Input("win-loss-heatmap-show-dates", "checked"),
        Input("win-loss-heatmap-show-longest-streak", "checked"),
    ],
)
def update_win_loss_heatmap(show_dates: bool, show_longest_streak: bool):
    """
    This callback will update the "Win-Loss Heatmap".

    Args:
        - show_dates (bool): Whether or not to show the dates on the x-axis.
        - show_longest_streak (bool): Whether or not to show the longest win/loss streak.
    """
    return win_loss_heatmap(
        game_level_stats_df=game_level_stats_df,
        show_dates=show_dates,
        show_longest_streak=show_longest_streak,
    )


@callback(
    output=Output("round-score-distribution-boxplot", "figure"),
    inputs=[
        Input("round-score-distribution-boxplot-violin-plot", "checked"),
        Input("round-score-distribution-boxplot-use-potential-points", "checked"),
    ],
)
def update_round_score_distribution_boxplot(
    violin_plot: bool, use_potential_points: bool
):
    """
    This callback will update the "Round Score Distribution" boxplot.

    Args:
        - violin_plot (bool): Whether or not to use a violin plot.
        - use_potential_points (bool): Whether or not to use the potential points for each round.
    """
    return round_score_distribution_boxplot(
        round_level_stats_df=round_level_stats_df,
        violin_plot=violin_plot,
        use_potential_points=use_potential_points,
    )


# ======================
# RUNNING THE APP SERVER
# ======================
# Below, I'm going to run the app server.

# If this file is being run directly, then run the app server
if __name__ == "__main__":
    app.run(debug=True, port=9096, host="0.0.0.0")
