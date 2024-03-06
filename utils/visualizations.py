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
from utils.misc import abbreviate_month

# =====================
# VISUALIZATION METHODS
# =====================
# Each of the methods below will generate a different visualization.


def total_wins_bar_chart(
    game_level_stats_df: pd.DataFrame, height: int = 250, annotation_font_size: int = 22
):
    """
    This method will generate a Plotly bar chart showing who's won more games.

    Args:
        - game_level_stats_df: The game level stats dataframe
        - height: The height of the bar chart (default is 400)
        - annotation_font_size: The font size of the annotations (default is 18)

    Returns:
        - A Plotly bar chart
    """

    # First, we're going to transform the game level stats dataframe to show the total wins for each player
    total_wins_df = (
        game_level_stats_df.groupby("winner")
        .size()
        .reset_index(name="Wins")
        .rename(columns={"winner": "Player"})
    )
    
    # Order the players so that Trevor is first
    total_wins_df = total_wins_df.sort_values("Player", ascending=False)

    # Rename "Sarah" and "Trevor" to "<b>Sarah</b>" and "<b>Trevor</b>" to make them bold
    total_wins_df["Player"] = total_wins_df["Player"].apply(lambda x: f"<b>{x}</b>")

    # Now, with this in mind, we can create the bar chart
    total_wins_fig = px.bar(
        total_wins_df,
        x="Wins",
        y="Player",
        color="Player",
        color_discrete_map={"<b>Trevor</b>": TREVOR_COLOR, "<b>Sarah</b>": SARAH_COLOR},
        labels={"Wins": "Total Wins", "Player": ""},
        height=height,
    )

    # Remove the legend, and change the margins
    MARGIN_SIZE = 20
    total_wins_fig.update_layout(
        showlegend=False,
        margin=dict(l=MARGIN_SIZE, r=MARGIN_SIZE, t=MARGIN_SIZE, b=MARGIN_SIZE, pad=20),
    )

    # Outline each of the bars with a black line
    total_wins_fig.update_traces(marker_line_color="black", marker_line_width=1)

    # Make the plot background white
    total_wins_fig.update_layout(plot_bgcolor="white")

    # Remove the x-axis title and ticks
    total_wins_fig.update_xaxes(title=None, showticklabels=False)

    # Add annotation text in the middle of each bar to show the total wins
    for i, row in total_wins_df.iterrows():
        cur_wins = row["Wins"]

        # Determine the x-position of the annotation
        x_pos = cur_wins / 2

        # Add the annotation, using the center of the text as the x-anchor
        total_wins_fig.add_annotation(
            x=x_pos,
            y=row["Player"],
            text=f"<b>{str(cur_wins)} wins</b><br><sub>{cur_wins/sum(total_wins_df['Wins'])*100:.0f}% of total games</sub>",
            font=dict(size=annotation_font_size, color="white"),
            showarrow=False,
            xanchor="center",
        )

    # Make the y-axis labels a little bigger
    total_wins_fig.update_yaxes(tickfont=dict(size=16))

    # Disable hoverinfo
    total_wins_fig.update_traces(hoverinfo="skip", hovertemplate=None)

    # Return the figure
    return total_wins_fig


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
    # TODO: Fix the hovertext to be more detailed

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
    pct_of_total_df["month"] = pct_of_total_df["game_date"].dt.month
    pct_of_total_df["x_axis_label"] = pct_of_total_df.apply(
        lambda row: f"{abbreviate_month(row.game_date.strftime('%B'))} {row.game_date.year}",
        axis=1,
    )

    # Sort by the game_date and round_num
    pct_of_total_df = pct_of_total_df.sort_values(
        by=["game_date", "round_num"], ascending=[True, True]
    )

    # Make the Plotly figure
    pct_of_total_fig = go.Figure()

    # If the user wants to show each round, then add the data points
    if show_each_round:

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
        margin=dict(l=FIGURE_MARGIN, r=FIGURE_MARGIN, t=FIGURE_MARGIN, b=30),
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


def win_loss_heatmap(
    game_level_stats_df: pd.DataFrame,
    show_dates: bool = False,
    plot_height: int = 180,
    show_longest_streak: bool = True,
    disabled_zoom: bool = True,
):
    """
    This function will generate a "win-loss heatmap", which will show the
    win-loss record for each month.

    Args:
        - game_level_stats_df (pd.DataFrame): A DataFrame containing game-level statistics.
        - show_dates (bool): Whether or not to show the dates on the x-axis.
        - plot_height (int): The height of the plot.
        - show_longest_streak (bool): Whether or not to show the longest win/loss streak.
        - disabled_zoom (bool): Whether or not to disable the zoom functionality.

    Returns:
        A Plotly figure.
    """
    # TODO: Add some hovertext that's more detailed

    # Transform the data into a 2D array, where the first one is Trevor's wins and the second one is Sarah's wins
    win_loss_2d_array = [
        [
            0 if row.winner == "Sarah" else None
            for row in game_level_stats_df.itertuples()
        ],
        [
            1 if row.winner == "Trevor" else None
            for row in game_level_stats_df.itertuples()
        ],
    ]

    # Create the heatmap
    win_loss_heatmap = go.Figure(
        data=go.Heatmap(
            z=win_loss_2d_array,
            # Make the x-axis the game number
            x=game_level_stats_df.id,
            y=["Sarah", "Trevor"],
            showscale=False,
        )
    )

    # Make the height of each cell 1
    win_loss_heatmap.update_layout(height=plot_height)

    # If we want to show the dates, then we'll update the x-axis to show the dates
    if show_dates:

        # Make a mapping between month/year and game number
        first_month_appearance_df = game_level_stats_df[["game_date", "id"]].copy()
        first_month_appearance_df["month"] = first_month_appearance_df[
            "game_date"
        ].dt.month
        first_month_appearance_df["year"] = first_month_appearance_df[
            "game_date"
        ].dt.year
        first_month_appearance_df["month_year_str"] = first_month_appearance_df.apply(
            lambda row: f"{abbreviate_month(row.game_date.strftime('%B'))} {row.game_date.year}",
            axis=1,
        )

        first_month_appearance_df = (
            first_month_appearance_df.groupby("month_year_str")
            .first()
            .reset_index()
            .drop(columns=["game_date"])
        )

        # Make the x-axis the month/year
        win_loss_heatmap.update_xaxes(
            tickmode="array",
            tickvals=first_month_appearance_df.id,
            ticktext=first_month_appearance_df.month_year_str,
            tickangle=45,
        )

        # Add dotted lines to separate the months
        for row in first_month_appearance_df.itertuples():
            game_id = row.id
            win_loss_heatmap.add_vline(
                x=game_id, line_dash="dot", line_color="black", line_width=1
            )

    # If we don't want to show dates, we'll hide the x-axis ticks and make the x-axis title "Game Number"
    else:
        win_loss_heatmap.update_xaxes(showticklabels=False)

    # Change the color of the cells so that Trevor's wins are green and Sarah's wins are red
    win_loss_heatmap.update_traces(
        colorscale=[[0, SARAH_COLOR], [1, TREVOR_COLOR]],
        colorbar=dict(title="Winner"),
    )

    # Remove the background color, and reduce the margins
    PLOT_MARGIN = 25
    win_loss_heatmap.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=PLOT_MARGIN, r=PLOT_MARGIN, b=40, t=PLOT_MARGIN, pad=10),
    )

    # If we want to show the longest streak, then we'll determine the longest streak for each player
    if show_longest_streak:

        # Determine the longest streak for each player, along with the game IDs
        trevor_streak = 0
        sarah_streak = 0
        trevor_streak_game_ids = []
        sarah_streak_game_ids = []
        trevor_current_streak_game_ids = []
        sarah_current_streak_game_ids = []
        for row in game_level_stats_df.sort_values(
            "game_date", ascending=True
        ).itertuples():
            cur_winner = row.winner
            if cur_winner == "Trevor":
                trevor_streak += 1
                trevor_current_streak_game_ids.append(row.id)
                if trevor_streak > len(trevor_streak_game_ids):
                    trevor_streak_game_ids = trevor_current_streak_game_ids.copy()
            else:
                trevor_streak = 0
                trevor_current_streak_game_ids = []

            if cur_winner == "Sarah":
                sarah_streak += 1
                sarah_current_streak_game_ids.append(row.id)
                if sarah_streak > len(sarah_streak_game_ids):
                    sarah_streak_game_ids = sarah_current_streak_game_ids.copy()
            else:
                sarah_streak = 0
                sarah_current_streak_game_ids = []

        # Outline the game IDs for the longest streaks
        win_loss_heatmap.add_shape(
            type="rect",
            x0=min(trevor_streak_game_ids) - 0.5,
            x1=max(trevor_streak_game_ids) + 0.5,
            y0=0.5,
            y1=1.5,
            yanchor="bottom",
            line=dict(color="black", width=3),
        )

        win_loss_heatmap.add_shape(
            type="rect",
            x0=min(sarah_streak_game_ids) - 0.5,
            x1=max(sarah_streak_game_ids) + 0.5,
            y0=-0.5,
            y1=0.5,
            yanchor="bottom",
            line=dict(color="black", width=3),
        )

        # Add an annotation for the longest streaks
        STREAK_FONT_SIZE = 16
        STREAK_FONT_COLOR = "black"
        win_loss_heatmap.add_annotation(
            x=(min(trevor_streak_game_ids) + max(trevor_streak_game_ids)) / 2,
            y=1,
            xref="x",
            yref="y",
            xanchor="center",
            yanchor="middle",
            text=f"<b>{len(trevor_streak_game_ids)}</b>",
            showarrow=False,
            font=dict(color=STREAK_FONT_COLOR, size=STREAK_FONT_SIZE),
        )

        # Add an annotation for the longest streaks
        win_loss_heatmap.add_annotation(
            x=(min(sarah_streak_game_ids) + max(sarah_streak_game_ids)) / 2,
            y=0,
            xref="x",
            yref="y",
            xanchor="center",
            yanchor="middle",
            text=f"<b>{len(sarah_streak_game_ids)}</b>",
            showarrow=False,
            font=dict(color=STREAK_FONT_COLOR, size=STREAK_FONT_SIZE),
        )

    # If we want to disable zoom, then we'll disable it
    if disabled_zoom:
        win_loss_heatmap.update_layout(
            xaxis=dict(fixedrange=True),
            yaxis=dict(fixedrange=True),
        )

    # Return the heatmap
    return win_loss_heatmap


def round_score_distribution_boxplot(
    round_level_stats_df: pd.DataFrame,
    violin_plot: bool = False,
    hide_legend: bool = True,
    height: int = 400,
    use_potential_points: bool = False,
):
    """
    This method will generate a boxplot for the points scored per round
    by each player.

    Args:
        - round_level_stats_df (pd.DataFrame): The DataFrame with the round level stats
        - violin_plot (bool): Whether or not to generate a violin plot instead of a boxplot
        - hide_legend (bool): Whether or not to hide the legend
        - height (int): The height of the plot
        - use_potential_points (bool): Whether or not to use the potential points instead of the actual points

    Returns:
        A Plotly figure
    """
    # TODO: Make the hovertext more detailed

    # Create a DataFrame for the points scored per round
    score_distribution_boxplot_df_records = []
    for row in round_level_stats_df.itertuples():
        for player in ["Trevor", "Sarah"]:
            score_distribution_boxplot_df_records.append(
                {
                    "round_id": f"{row.game_date}_round_{row.round_num}",
                    "game_date": row.game_date,
                    "round_num": row.round_num,
                    "player": player,
                    "score": getattr(row, f"{player.lower()}_points_scored"),
                    "points_potential": getattr(
                        row, f"{player.lower()}_points_potential"
                    ),
                }
            )

    # Create the DataFrame
    score_distribution_boxplot_df = pd.DataFrame(score_distribution_boxplot_df_records)

    # Make the Plotly figure
    score_col_to_use = "score" if not use_potential_points else "points_potential"
    score_col_label = (
        "Points Scored" if not use_potential_points else "Potential Points"
    )
    score_distribution_fig = px.box(
        score_distribution_boxplot_df,
        x="player",
        y=score_col_to_use,
        color="player",
        labels={
            "round_id": "Round ID",
            score_col_to_use: score_col_label,
            "player": "",
        },
        color_discrete_map={"Trevor": TREVOR_COLOR, "Sarah": SARAH_COLOR},
        points="all",
        height=height,
    )

    # If the violin plot is requested, update the figure
    if violin_plot:
        score_distribution_fig = px.violin(
            score_distribution_boxplot_df,
            x="player",
            y=score_col_to_use,
            color="player",
            labels={
                "round_id": "Round ID",
                score_col_to_use: score_col_label,
                "player": "",
            },
            color_discrete_map={"Trevor": TREVOR_COLOR, "Sarah": SARAH_COLOR},
            points="all",
        )

    # Make the background white
    score_distribution_fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    # Make the legend horizontal, and move it to the top-right corner of the figure (using the top-right corner as an anchor)
    score_distribution_fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="top",
            y=1.1,
            xanchor="right",
            x=1,
        )
    )

    # Make the markers have a black border and a bit of transparency
    score_distribution_fig.update_traces(
        marker=dict(
            line=dict(width=1, color="black"),
            opacity=0.7,
        )
    )

    # Reduce the margins
    PLOT_MARGINS = 20
    score_distribution_fig.update_layout(
        margin=dict(
            l=PLOT_MARGINS, r=PLOT_MARGINS, b=PLOT_MARGINS, t=PLOT_MARGINS, pad=10
        )
    )

    # If the legend is requested to be hidden, hide it
    if hide_legend:
        score_distribution_fig.update_layout(showlegend=False)

    # Return the figure
    return score_distribution_fig
