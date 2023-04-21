from mplsoccer import Pitch
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as path_effects
import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.cm as cm
import json
from src.spider import RadarChartMetrics

PITCH = Pitch(
    pitch_type="statsbomb",
    line_color="#ffffff",
    pitch_color="#567d46",
    goal_type="box",
)


def create_shots_vis(team, period, shots_df):

    # Filter for shots in first half
    if period == "FT":
        shots = shots_df[(shots_df["team"] == team)]
    else:
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
    goal_patch = mpatches.Patch(color="red", label="GOAL")
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

    if period == "FT":
        mcfc = df_all.loc[(df_all["team.name"] == team)]
        mcfc2 = df.loc[(df["team"] == team)]
    else:
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
    m_per_player_pass_count.columns = ["player", "pass_count"]
    m_per_player_pass_count = m_per_player_pass_count.merge(m_avg_loc, on="player")

    m_player_pass_count = m_player_pass_count.merge(m_avg_loc, on="player")
    m_avg_loc.columns = ["pass_recipient_name", "x_end", "y_end"]
    m_player_pass_count = m_player_pass_count.merge(m_avg_loc, on="pass_recipient_name")
    m_player_pass_count = m_player_pass_count.merge(numbers, on="player")

    m_player_pass_count.sort_values(by="pass_count", ascending=False).head(15)

    # Filter for shots in first half
    # shots = shots_df[(shots_df["team"] == team) & (shots_df["period"] == period)]

    # Create figure and axis using pitch object
    fig, ax = PITCH.draw(figsize=(16, 11))

    colormap = "magma"
    num_passes = m_player_pass_count.pass_count.values
    colors = cm.get_cmap(colormap)(num_passes / num_passes.max())

    PITCH.arrows(
        m_player_pass_count.x,
        m_player_pass_count.y,
        m_player_pass_count.x_end,
        m_player_pass_count.y_end,
        alpha=0.3,
        ax=ax,
        color=colors,
        cmap=colormap,
    )
    PITCH.scatter(
        m_per_player_pass_count.x,
        m_per_player_pass_count.y,
        alpha=1,
        s=100 * m_per_player_pass_count.pass_count,
        color="#6CABDD",
        edgecolor="white",
        ax=ax,
    )

    cax = fig.add_axes([0.95, 0.25, 0.03, 0.5])
    cb = plt.colorbar(cm.ScalarMappable(cmap=colormap), cax=cax)
    cb.ax.tick_params(labelsize=14)
    cb.set_label("Number of Passes", fontsize=16)

    for i in range(len(m_player_pass_count)):
        PITCH.annotate(
            m_player_pass_count.number[i],
            xy=(m_player_pass_count.x[i], m_player_pass_count.y[i]),
            size=14,
            va="center",
            ha="center",
            ax=ax,
        )

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


def plot_pass_network(selected_player, team, period, events_df):

    # Create a DataFrame from the data
    df = events_df

    # Filter the DataFrame to only include passes
    passes_df = df[df["type"] == "Pass"]

    for i, row in passes_df.iterrows():
        side = row["team"]
        player = row["player"]
        start_x = row["location_x"]
        start_y = row["location_y"]
        end_x = np.nan
        end_y = np.nan
        for j in range(i + 1, len(df)):
            next_row = df.iloc[j]
            if next_row["team"] == side:
                if next_row["type"] == "Ball Receipt*":
                    end_x = next_row["location_x"]
                    end_y = next_row["location_y"]
                    break
            else:
                break
        passes_df.at[i, "pass_end_location_x"] = end_x
        passes_df.at[i, "pass_end_location_y"] = end_y
    # Define pitch dimensions
    pitchLengthX = 120
    pitchWidthY = 80

    # Create figure and axis
    fig, ax = PITCH.draw(figsize=(16, 11))

    # Filter for selected team in the 1st half
    if period == "FT":
        man_city_passes = passes_df[
            (passes_df["team"] == team) & (passes_df["player"] == selected_player)
        ]
    else:
        man_city_passes = passes_df[
            (passes_df["team"] == team)
            & (passes_df["period"] == period)
            & (passes_df["player"] == selected_player)
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
                ec="black",
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
        f"Pass Map for {player} - Half: {period}",
        fontsize=30,
        fontweight="bold",
        y=1,
    )

    # Remove ticks and axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    # Show the plot
    st.pyplot(fig)


def create_base_stats(lineup_df, shots_df, df):

    lineup = pd.DataFrame(lineup_df)
    opponent = lineup.iloc[1, 1]

    shots_mcfc = len(shots_df.loc[shots_df["team"] == "Manchester City WFC"])
    shots_opp = len(shots_df.loc[shots_df["team"] == opponent])
    xg_mcfc = shots_df.loc[shots_df["team"] == "Manchester City WFC"]["statsbomb_xg"]
    xg_opp = shots_df.loc[shots_df["team"] == opponent]["statsbomb_xg"]
    goals_mcfc = len(
        shots_df.loc[
            (shots_df["team"] == "Manchester City WFC")
            & (shots_df["outcome"] == "Goal")
        ]
    )
    goals_opp = len(
        shots_df.loc[(shots_df["team"] == opponent) & (shots_df["outcome"] == "Goal")]
    )
    sot_mcfc = len(
        shots_df.loc[
            (
                (shots_df["team"] == "Manchester City WFC")
                & (shots_df["outcome"] == "Goal")
            )
            | (
                (shots_df["team"] == "Manchester City WFC")
                & (shots_df["outcome"] == "Blocked")
            )
            | (
                (shots_df["team"] == "Manchester City WFC")
                & (shots_df["outcome"] == "Saved")
            )
        ]
    )
    sot_opp = len(
        shots_df.loc[
            ((shots_df["team"] == opponent) & (shots_df["outcome"] == "Goal"))
            | ((shots_df["team"] == opponent) & (shots_df["outcome"] == "Blocked"))
            | ((shots_df["team"] == opponent) & (shots_df["outcome"] == "Saved"))
        ]
    )
    foul_mcfc = len(
        df.loc[(df["type"] == "Foul Committed") & (df["team"] == "Manchester City WFC")]
    )
    foul_opp = len(df.loc[(df["type"] == "Foul Committed") & (df["team"] == opponent)])

    # Match stats table
    stats = {
        "Goals": [goals_mcfc, goals_opp],
        "Expected Goals (XG)": [xg_mcfc.sum(), xg_opp.sum()],
        "Shots": [shots_mcfc, shots_opp],
        "Shots on Target": [sot_mcfc, sot_opp],
        "Shot Conversion (%)": [
            (100 * sot_mcfc / shots_mcfc),
            (100 * sot_opp / shots_opp),
        ],
        "Fouls": [foul_mcfc, foul_opp],
        "Yellow Cards": [],  # or bookings
        "Corners": [],
        "Offsides": [],
        "Possession": [],
    }
    stats_df = df.from_dict(
        stats, orient="index", columns=["Manchester City WFC", opponent]
    )

    def highlight_max(s):
        is_max = s == s.max()
        return ["background-color: yellow" if v else "" for v in is_max]

    stats_df = stats_df.round(1)
    s = stats_df.style.highlight_max(color="yellow", axis=1)
    st.dataframe(s, use_container_width=True)


# def plot_spider(team, period, shots_df, events_json, events_df):

#     radar_metrics = RadarChartMetrics(
#         player="Alex Greenwood",
#         period=period,
#         team=team,
#         shots_df=shots_df,
#         events_json=events_json,
#         events_df=events_df,
#     )
#     lineup = list(radar_metrics.get_lineup())
#     lineup = [l for l in lineup if l is not None]
#     print(lineup)

#     fig, ax = radar_metrics.generate_spider_chart()
#     return fig, ax, lineup
#     # st.pyplot(fig)


def create_heatmap(df, period, team, player):

    # Set the color palette
    sns.set_palette("dark")

    # Filter for events in first half
    if period == "FT":
        events = df.loc[(df["possession_team"] == team) & (df["player"] == player)]
    else:
        events = df.loc[
            (df["period"] == period)
            & (df["possession_team"] == team)
            & (df["player"] == player)
        ]

    # Calculate average location per player
    # player_locs = events.groupby('player')['location_x', 'location_y'].reset_index()

    fig, ax = PITCH.draw(figsize=(16, 11))

    # Create heatmap
    pitch = sns.kdeplot(
        x=events["location_x"],
        y=events["location_y"],
        cmap="YlGnBu_r",
        shade=True,
        alpha=0.8,
        levels=50,
        zorder=2,
        ax=ax,
    )

    # Add arrow
    arrow = ax.annotate(
        "Attacking Direction",
        xy=(110, 40),
        xytext=(60, 40),
        arrowprops=dict(
            arrowstyle="-|>", color="white", linewidth=2, mutation_scale=20
        ),
        ha="center",
        va="center",
        fontsize=14,
        color="white",
    )

    # Add path effect to arrow
    arrow.set_path_effects(
        [path_effects.Stroke(linewidth=2, foreground="black"), path_effects.Normal()]
    )

    # Add colorbar
    cb = fig.colorbar(pitch.collections[0], ax=ax)
    cb.ax.set_facecolor("#202020")
    cb.ax.yaxis.set_tick_params(color="white")
    cb.outline.set_edgecolor("white")
    cb.ax.tick_params(
        labelsize=12, length=0, color="white", labelcolor="white", width=2
    )

    # Set plot title
    ax.set_title("Match Summary", fontsize=26, fontweight="bold", y=1.08, color="white")

    # Remove ticks and axis labels
    ax.set_xticks([])
    ax.set_yticks([])

    st.pyplot(fig)


def step_graph(json_file, opponent, period):

    df_all = json_file

    if period == "FT":
        mcfc_shots = df_all.loc[
            ((df_all["type.name"] == "Shot") | (df_all["type.name"] == "Half End"))
            # & (df_all["period"] == period)
        ]
    else:
        mcfc_shots = df_all.loc[
            ((df_all["type.name"] == "Shot") | (df_all["type.name"] == "Half End"))
            & (df_all["period"] == period)
        ]
    mcfc_shots = mcfc_shots[
        [
            "timestamp",
            "minute",
            "second",
            "team.name",
            "location",
            "player.name",
            "shot.statsbomb_xg",
            "shot.end_location",
            "shot.outcome.name",
        ]
    ]

    mcfc_sumxg = mcfc_shots.loc[mcfc_shots["team.name"] == "Manchester City WFC"][
        ["timestamp", "minute", "second", "shot.statsbomb_xg"]
    ]
    mcfc_sumxg = mcfc_sumxg.fillna(0)
    mcfc_sumxg["xg_sum"] = mcfc_sumxg["shot.statsbomb_xg"].cumsum()

    opp_sumxg = mcfc_shots.loc[mcfc_shots["team.name"] == opponent][
        ["timestamp", "minute", "second", "shot.statsbomb_xg"]
    ]
    opp_sumxg = opp_sumxg.fillna(0)
    opp_sumxg["xg_sum"] = opp_sumxg["shot.statsbomb_xg"].cumsum()

    zero_row = pd.DataFrame(
        [[0] * mcfc_sumxg.shape[1]], columns=mcfc_sumxg.columns, index=[0]
    )

    # simply concatenate both dataframes
    mcfc_sumxg = pd.concat([zero_row, mcfc_sumxg]).reset_index(drop=True)
    opp_sumxg = pd.concat([zero_row, opp_sumxg]).reset_index(drop=True)

    mcfc_sumxg
    fig, ax = plt.subplots()
    fig.set_facecolor("#444444")
    ax.patch.set_facecolor("#444444")
    mcfc_sumxg.plot(
        x="minute", y="xg_sum", drawstyle="steps", ax=ax, color="#6CABDD", linewidth=2
    )
    opp_sumxg.plot(
        x="minute", y="xg_sum", ax=ax, drawstyle="steps", color="red", linewidth=2
    )
    plt.xticks(color="white")
    plt.yticks(color="white")
    plt.ylabel("xG", color="white")
    plt.xlabel("Minute", color="white")
    plt.title(
        f"Expected Goals for Manchester City WFC vs {opponent}", color="white", y=1
    )
    ax.grid(lw=0.5, color="lightgrey", axis="y", zorder=1)
    plt.legend(["Manchester City WFC", opponent])

    # next annotate goals
    # for i in mcfc_shots.iterrows:
    st.pyplot(fig)

    # xg curve seems to be one period behind, ie first xg should be at 3 mins not 0 mins
