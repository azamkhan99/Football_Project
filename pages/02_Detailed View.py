import streamlit as st

from mplsoccer import Pitch
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from src.visualisation_functions import (
    create_shots_vis,
    create_pass_network,
    plot_pass_network,
    create_base_stats,
    create_heatmap,
    step_graph,
)
from src.spider import RadarChartMetrics
from soccerplots import radar_chart
from soccerplots.radar_chart import Radar


POSITION_LABELS = {
    "Goalkeeper": "GK",
    "Right Back": "RB",
    "Right Center Back": "RCB",
    "Center Back": "CB",
    "Left Center Back": "LCB",
    "Left Back": "LB",
    "Right Wing Back": "RWB",
    "Left Wing Back": "LWB",
    "Right Defensive Midfield": "RDM",
    "Center Defensive Midfield": "CDM",
    "Left Defensive Midfield": "LDM",
    "Right Midfield": "RM",
    "Right Center Midfield": "RCM",
    "Center Midfield": "CM",
    "Left Center Midfield": "LCM",
    "Left Midfield": "LM",
    "Right Wing": "RW",
    "Right Attacking Midfield": "RAM",
    "Center Attacking Midfield": "CAM",
    "Left Attacking Midfield": "LAM",
    "Left Wing": "LW",
    "Right Center Forward": "RCF",
    "Striker": "ST",
    "Left Center Forward": "LCF",
    "Secondary Striker": "SS",
    "Center Forward": "CF",
}


def comparison_spider(player1_values, team1, player2_values, team2):

    filter_all1 = player1_values.df
    filter_all2 = player2_values.df

    val_comp = filter_all1.iloc[0], filter_all2.iloc[0]
    ## titles for each players
    title_comp = dict(
        title_name=f"{player1_values.player}",
        title_color="#D00027",
        subtitle_name=f"{team1}",
        subtitle_color="#000000",
        title_name_2=f"{player2_values.player}",
        title_color_2="#00A398",
        subtitle_name_2=f"{team2}",
        subtitle_color_2="#000000",
        title_fontsize=18,
        subtitle_fontsize=15,
    )
    ## plotting the radar chart
    radar = Radar()
    fig, ax = radar.plot_radar(
        ranges=player1_values.ranges,
        params=player2_values.params,
        values=val_comp,
        radar_color=["#D00027", "#00A398"],
        title=title_comp,
        compare=True,
    )
    return fig, ax


# st.title("Manchester City WFC visualisation")

shots_df = st.session_state["shots_df"]
events_df = st.session_state["events_df"]
lineup_df = st.session_state["lineups"]
opponent = lineup_df.iloc[1, 1]
events_json = st.session_state["normalized_events_df"]
stats_df, goals_mcfc, goals_opp = create_base_stats(
    lineup_df=lineup_df, shots_df=shots_df, df=events_df
)

st.title(f"Manchester City WFC {goals_mcfc} - {goals_opp} {opponent}")

s = stats_df.style.highlight_max(color="yellow", axis=1)
st.dataframe(s, use_container_width=True)


tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["XG", "Shot Analysis", "Passing Analysis", "Player Comparison", "Heatmap"]
)

with tab1:
    events_json = st.session_state["normalized_events_df"]

    # with col1:
    # team_option = st.selectbox("Select Teams", (np.unique(shots_df["team"])))

    period_option = period_option = st.selectbox("Choose Half - ", [1, 2, "FT"])

    step_graph(events_json, "Arsenal WFC", period=period_option)


with tab2:
    shots_df = st.session_state["shots_df"]

    # Define pitch object with desired dimensions and color scheme

    col1, col2 = st.columns(2)

    with col1:
        team_option = st.selectbox("Team", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox("Half", [1, 2, "FT"])

    create_shots_vis(team=team_option, period=period_option, shots_df=shots_df)


with tab3:
    events_df = st.session_state["events_df"]
    normalized_events_df = st.session_state["normalized_events_df"]

    col1, col2 = st.columns(2)

    with col1:
        team_option = st.selectbox("Select Team", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox("Select Half", [1, 2, "FT"])

    create_pass_network(
        team=team_option,
        period=period_option,
        data=events_df,
        json=normalized_events_df,
    )

    net1, net2 = st.columns(2)

    with net1:

        df_all = events_json

        team_option = st.selectbox("Select Team:", (np.unique(shots_df["team"])))

        period_option = st.selectbox("Select Period:", [1, 2, "FT"])

        lineup1 = df_all.loc[df_all["team.name"] == team_option]["tactics.lineup"].iloc[
            0
        ]
        numbers = pd.json_normalize(lineup1)
        numbers = numbers[["player.name", "position.name"]]

        lineup = numbers.apply(
            lambda row: f"{row['player.name']} - {POSITION_LABELS.get(row['position.name'])}",
            axis=1,
        ).tolist()

        player_option_n = st.selectbox("Select Passer", lineup)

        plot_pass_network(
            selected_player=player_option_n.split(" -")[0],
            team=team_option,
            period=period_option,
            events_df=events_df,
        )

    with net2:

        df_all = events_json

        team_option = st.selectbox("Select Side 2", (np.unique(shots_df["team"])))

        period_option = st.selectbox("Select Period 2", [1, 2, "FT"])

        lineup1 = df_all.loc[df_all["team.name"] == team_option]["tactics.lineup"].iloc[
            0
        ]
        numbers = pd.json_normalize(lineup1)
        numbers = numbers[["player.name", "position.name"]]

        lineup = numbers.apply(
            lambda row: f"{row['player.name']} - {POSITION_LABELS.get(row['position.name'])}",
            axis=1,
        ).tolist()

        player_option_n = st.selectbox("Select Passer 2", lineup)

        plot_pass_network(
            selected_player=player_option_n.split(" -")[0],
            team=team_option,
            period=period_option,
            events_df=events_df,
        )

with tab4:
    events_df = st.session_state["events_df"]
    shots_df = st.session_state["shots_df"]
    events_json = st.session_state["events_json"]

    col1, col2, col3 = st.columns(3)

    with col1:
        team_option = st.selectbox("Select Club", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox("Select Half period", [1, 2, "FT"])

    radar_metrics = RadarChartMetrics(
        # player="Alex Greenwood",
        period=period_option,
        team=team_option,
        shots_df=shots_df,
        events_json=events_json,
        events_df=events_df,
    )

    lineup = radar_metrics.get_player_positions(POSITION_LABELS)

    with col3:
        player_option = st.selectbox("Select Player", lineup)

    # st.dataframe(
    #     radar_metrics.generate_spider_chart_values_df(), use_container_width=True
    # )
    radar_metrics.generate_spider_chart_values(player=player_option.split(" -")[0])
    player_vals = radar_metrics.spider_values[0]
    fig, axis = radar_metrics.generate_spider_chart(player_vals)
    st.pyplot(fig)

    agree = st.checkbox("Player Comparison")

    if agree:

        st.write("Compare players")
        col1, col2, col3 = st.columns(3)
        with col1:
            team_option2 = st.selectbox(
                "Select Club for Second Player", (np.unique(shots_df["team"]))
            )
        with col2:
            period_option2 = st.selectbox("Select Period to Analyse", [1, 2, "FT"])

        radar_metrics2 = RadarChartMetrics(
            # player="Alex Greenwood",
            period=period_option2,
            team=team_option2,
            shots_df=shots_df,
            events_json=events_json,
            events_df=events_df,
        )

        lineup2 = radar_metrics2.get_player_positions(POSITION_LABELS)

        with col3:
            player_option2 = st.selectbox("Select Second Player", lineup2)

        radar_metrics2.generate_spider_chart_values(
            player=player_option2.split(" -")[0]
        )
        player_vals2 = radar_metrics2.spider_values[0]
        fig2, ax2 = comparison_spider(
            player1_values=player_vals,
            team1=team_option,
            player2_values=player_vals2,
            team2=team_option2,
        )
        st.pyplot(fig2)


with tab5:
    events_json = st.session_state["normalized_events_df"]
    df_all = events_json

    col1, col2, col3 = st.columns(3)

    with col1:
        team_option = st.selectbox("Select Teams", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox("Select Periods", [1, 2, "FT"])
    with col3:
        lineup1 = df_all.loc[df_all["team.name"] == team_option]["tactics.lineup"].iloc[
            0
        ]
        numbers = pd.json_normalize(lineup1)

        numbers = numbers[["player.name", "position.name"]]

        lineup = numbers.apply(
            lambda row: f"{row['player.name']} - {POSITION_LABELS.get(row['position.name'])}",
            axis=1,
        ).tolist()

        player_option_hm = st.selectbox("Select Player HeatMap", lineup)

    create_heatmap(
        events_df,
        period=period_option,
        team=team_option,
        player=player_option_hm.split(" -")[0],
    )
