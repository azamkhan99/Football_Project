from mplsoccer import Pitch
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import streamlit as st
import json

PITCH = Pitch(
    pitch_type="statsbomb",
    line_color="#ffffff",
    pitch_color="#444444",
    goal_type="box",
)


def create_shots_vis(team, period, shots_df):

    # Filter for shots in first half
    shots = shots_df[(shots_df["team"] == team) & (shots_df["period"] == period)]

    # Create figure and axis using pitch object
    fig, ax = PITCH.draw(figsize=(16, 11))

    # Create scatter plot with color coding by goals vs no goals
    colors = ["red" if x else "green" for x in shots["outcome"] == "Goal"]
    ax.scatter(
        shots["x"],
        shots["y"],
        c=colors,
        edgecolors="white",
        alpha=0.8,
        s=200,
        zorder=3,
    )

    # Add legend
    goal_patch = mpatches.Patch(color="red", label="Goal")
    no_goal_patch = mpatches.Patch(color="green", label="No Goal")
    ax.legend(
        handles=[goal_patch, no_goal_patch],
        loc="lower right",
        fontsize=14,
        facecolor="white",
        edgecolor="white",
    )

    # Set plot title
    ax.set_title(
        "Shots for Mancity-1st half",
        fontsize=26,
        fontweight="bold",
        y=1.08,
        color="white",
    )

    # Remove ticks and axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    st.pyplot(fig)


def create_pass_network(team, period, data, json):
    df = data

    df_all = json

    lineup1 = df_all[df_all["team.name"] == team]["tactics.lineup"].iloc[0]
    numbers = pd.json_normalize(lineup1)

    numbers = numbers[["player.name", "jersey_number"]]
    numbers.columns = ["player", "number"]

    mcfc = df_all.loc[(df_all["team.name"] == team) & (df_all["period"] == period)]
    mcfc2 = df.loc[(df["team"] == team) & (df["period"] == period)]

    m_pass = mcfc.loc[
        (mcfc["type.name"] == "Pass") & (mcfc["pass.recipient.name"].notna())
    ]
    m_avg_loc = mcfc2.groupby("player", as_index=False).agg(
        {"location_x": ["mean"], "location_y": ["mean"]}
    )

    m_player_pass = m_pass[["player.name", "pass.recipient.name"]]
    m_player_pass_count = m_player_pass.groupby(
        ["player.name", "pass.recipient.name"], as_index=False
    ).value_counts()
    m_per_player_pass_count = (
        m_pass[["player.name"]].groupby("player.name", as_index=False).value_counts()
    )
    m_player_pass_count.columns = ["player", "pass_recipient_name", "pass_count"]
    m_avg_loc.columns = ["player", "x", "y"]
    m_player_pass_count = m_player_pass_count.merge(m_avg_loc, on="player")
    m_avg_loc.columns = ["pass_recipient_name", "x_end", "y_end"]
    m_player_pass_count = m_player_pass_count.merge(m_avg_loc, on="pass_recipient_name")
    m_player_pass_count = m_player_pass_count.merge(numbers, on="player")

    m_player_pass_count.sort_values(by="pass_count", ascending=False).head(15)

    # Filter for shots in first half
    # shots = shots_df[(shots_df["team"] == team) & (shots_df["period"] == period)]

    # Create figure and axis using pitch object
    fig, ax = PITCH.draw(figsize=(16, 11))

    PITCH.arrows(
        m_player_pass_count.x,
        m_player_pass_count.y,
        m_player_pass_count.x_end,
        m_player_pass_count.y_end,
        alpha=0.3,
        ax=ax,
    )
    PITCH.scatter(
        m_player_pass_count.x,
        m_player_pass_count.y,
        alpha=1,
        s=600,
        color="#6CABDD",
        edgecolor="white",
        ax=ax,
    )

    for i in range(len(m_player_pass_count)):
        PITCH.annotate(
            m_player_pass_count.number[i],
            xy=(m_player_pass_count.x[i], m_player_pass_count.y[i]),
            size=14,
            va="center",
            ha="center",
            ax=ax,
        )
    # Create scatter plot with color coding by goals vs no goals
    # colors = ['red' if x else 'green' for x in shots['outcome'] == 'Goal']
    # ax.scatter(shots['x'], shots['y'], c=colors, edgecolors='white', alpha=0.8, s=200, zorder=3)

    # Add legend
    # goal_patch = mpatches.Patch(color='red', label='Goal')
    # no_goal_patch = mpatches.Patch(color='green', label='No Goal')
    # ax.legend(handles=[goal_patch, no_goal_patch], loc='lower right', fontsize=14, facecolor='white', edgecolor='white')

    # Set plot title
    ax.set_title(
        f"Pass network for {team} - Half-{period}",
        fontsize=26,
        fontweight="bold",
        y=1.08,
        color="black",
    )

    # Remove ticks and axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    st.pyplot(fig)


def plot_pass_network(player, team, period, events_df):

    # Create a DataFrame from the data
    df = events_df

    # Filter the DataFrame to only include passes
    passes_df = df[df["type"] == "Pass"]

    for i, row in passes_df.iterrows():
        team = row["team"]
        player = row["player"]
        start_x = row["location_x"]
        start_y = row["location_y"]
        end_x = np.nan
        end_y = np.nan
        for j in range(i + 1, len(df)):
            next_row = df.iloc[j]
            if next_row["team"] == team:
                if next_row["type"] == "Ball Receipt*":
                    end_x = next_row["location_x"]
                    end_y = next_row["location_y"]
                    break
            else:
                break
        passes_df.at[i, "pass_end_location_x"] = end_x
        passes_df.at[i, "pass_end_location_y"] = end_y
    st.write("TEST")
    st.write(passes_df)
    # Define pitch dimensions
    pitchLengthX = 120
    pitchWidthY = 80

    # Create figure and axis
    fig, ax = PITCH.draw(figsize=(16, 11))

    # Filter for Man City in the 1st half
    man_city_passes = passes_df[
        (passes_df["team"] == "Manchester City WFC") & (passes_df["period"] == 1)
    ]
    man_city_passes.reset_index(drop=True, inplace=True)

    # Group passes by player
    player_passes = man_city_passes.groupby("player").count()["id"].reset_index()
    player_passes.rename(columns={"id": "pass_count"}, inplace=True)

    # Merge player_passes with man_city_passes to get the locations of the passes
    player_passes = pd.merge(
        player_passes,
        man_city_passes[
            [
                "player",
                "location_x",
                "location_y",
                "pass_end_location_x",
                "pass_end_location_y",
                "possession_team",
            ]
        ],
        on="player",
        how="left",
    )
    player_passes.reset_index(drop=True, inplace=True)
    # Plot the passes for Manchester City
    # Create a dictionary to map players to colors
    # Create a dictionary to map each player to a unique color
    color_dict = {}
    for i, player in enumerate(player_passes["player"].unique()):
        color_dict[player] = plt.cm.get_cmap("tab20")(i)

    # Create a set to keep track of which players have already been added to the legend
    legend_players = set()

    # Loop through each player's passes and plot them
    for player in player_passes["player"].unique():
        player_passes_subset = player_passes[
            player_passes["player"] == player
        ].reset_index()
        color = color_dict[player]
        size = 80
        linewidth = 1.5
        for j in range(len(player_passes_subset)):
            x_start = player_passes_subset.loc[j, "location_x"]
            y_start = player_passes_subset.loc[j, "location_y"]
            x_end = player_passes_subset.loc[j, "pass_end_location_x"]
            y_end = player_passes_subset.loc[j, "pass_end_location_y"]

            # Determine arrow direction based on start and end locations
            dx, dy = x_end - x_start, y_end - y_start

            # Plot the pass with an arrow
            ax.arrow(
                x_start,
                y_start,
                dx,
                dy,
                head_width=2,
                head_length=2,
                fc=color,
                ec="gray",
                alpha=0.6,
                linewidth=linewidth,
                zorder=1,
            )

            # Plot the start and end nodes with different marker shapes
            ax.scatter(
                x_start,
                y_start,
                marker="s",
                color=color,
                edgecolors="black",
                linewidth=linewidth,
                alpha=0.7,
                s=size,
                zorder=2,
            )
            ax.scatter(
                x_end,
                y_end,
                marker="o",
                color="white",
                edgecolors="black",
                linewidth=linewidth,
                alpha=0.7,
                s=size,
                zorder=2,
            )

        # Add player name to legend with lower alpha
        if player not in legend_players:
            plt.scatter(
                [],
                [],
                marker="o",
                color=color,
                edgecolors="black",
                linewidth=0.5,
                alpha=0.3,
                s=100,
                label=player,
            )
            legend_players.add(player)

    # Add grid lines
    ax.grid(True, linestyle="--", alpha=0.5)
    # Invert the y-axis to match the top left origin
    # ax.invert_yaxis()

    # Add a legend with a readable font
    plt.legend(
        scatterpoints=1,
        loc="lower left",
        fontsize=12,
        framealpha=1,
        facecolor="white",
        frameon=True,
    )

    # Set plot title with a readable font
    ax.set_title(
        "Pass Network for Man City - 1st half", fontsize=20, fontweight="bold", y=1.08
    )

    # Remove ticks and axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Show the plot
    st.pyplot(fig)
