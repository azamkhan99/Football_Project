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
)
from src.spider import RadarChartMetrics
from soccerplots import radar_chart
from soccerplots.radar_chart import Radar


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


st.title("Visualisations")

shots_df = st.session_state["shots_df"]
events_df = st.session_state["events_df"]
lineup_df = st.session_state["lineups"]
events_json = st.session_state["normalized_events_df"]
create_base_stats(lineup_df=lineup_df, shots_df=shots_df, df=events_df)


tab1, tab2, tab3, tab4 = st.tabs(
    ["Shot Analysis", "Passing Analysis", "Player Comparison", "Heatmap"]
)
with tab1:
    shots_df = st.session_state["shots_df"]

    # Define pitch object with desired dimensions and color scheme

    col1, col2 = st.columns(2)

    with col1:
        team_option = st.selectbox("Team", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox("Half", (np.unique(shots_df["period"])))

    create_shots_vis(team=team_option, period=period_option, shots_df=shots_df)


with tab2:
    events_df = st.session_state["events_df"]
    normalized_events_df = st.session_state["normalized_events_df"]

    col1, col2 = st.columns(2)

    with col1:
        team_option = st.selectbox("Select Team", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox("Select Half", (np.unique(shots_df["period"])))

    create_pass_network(
        team=team_option,
        period=period_option,
        data=events_df,
        json=normalized_events_df,
    )

    col1, col2 = st.columns(2)

    with col1:
        team_option = st.selectbox("Select Side", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox("Select Period", (np.unique(shots_df["period"])))
    plot_pass_network(
        player="s", team=team_option, period=period_option, events_df=events_df
    )

with tab3:
    events_df = st.session_state["events_df"]
    shots_df = st.session_state["shots_df"]
    events_json = st.session_state["events_json"]

    col1, col2, col3 = st.columns(3)

    with col1:
        team_option = st.selectbox("Select Club", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox(
            "Select Half period", (np.unique(shots_df["period"]))
        )

    radar_metrics = RadarChartMetrics(
        # player="Alex Greenwood",
        period=period_option,
        team=team_option,
        shots_df=shots_df,
        events_json=events_json,
        events_df=events_df,
    )
    lineup = list(radar_metrics.get_lineup())
    lineup = [l for l in lineup if l is not None]

    with col3:
        player_option = st.selectbox("Select Player", lineup)

    st.write("Single player viz")
    radar_metrics.generate_spider_chart_values(player=player_option)
    player_vals = radar_metrics.spider_values[0]
    fig, axis = radar_metrics.generate_spider_chart(player_vals)
    st.pyplot(fig)

    agree = st.checkbox("Player Comparison")

    if agree:

        st.write("Compare players")
        col1, col2, col3 = st.columns(3)
        with col1:
            team_option2 = st.selectbox(
                "Select Club for second player", (np.unique(shots_df["team"]))
            )
        with col2:
            period_option2 = st.selectbox(
                "Select which half", (np.unique(shots_df["period"]))
            )

        radar_metrics2 = RadarChartMetrics(
            # player="Alex Greenwood",
            period=period_option2,
            team=team_option2,
            shots_df=shots_df,
            events_json=events_json,
            events_df=events_df,
        )
        lineup2 = list(radar_metrics2.get_lineup())
        lineup2 = [l for l in lineup2 if l is not None]

        with col3:
            player_option2 = st.selectbox("Select Players", lineup2)

        radar_metrics2.generate_spider_chart_values(player=player_option2)
        player_vals2 = radar_metrics2.spider_values[0]
        fig2, ax2 = comparison_spider(
            player1_values=player_vals,
            team1=team_option,
            player2_values=player_vals2,
            team2=team_option2,
        )
        st.pyplot(fig2)


with tab4:
    events_json = st.session_state["normalized_events_df"]
    df_all = events_json

    col1, col2, col3 = st.columns(3)

    with col1:
        team_option = st.selectbox("Select Teams", (np.unique(shots_df["team"])))
    with col2:
        period_option = st.selectbox("Select Periods", (np.unique(shots_df["period"])))
    with col3:
        lineup1 = df_all.loc[df_all["team.name"] == team_option]["tactics.lineup"].iloc[
            0
        ]
        numbers = pd.json_normalize(lineup1)

        numbers = numbers[["player.name", "jersey_number"]]
        numbers.columns = ["player", "number"]

        lineup = np.array(numbers["player"])

        player_option_hm = st.selectbox("Select Player", lineup)

    create_heatmap(
        events_df, period=period_option, team=team_option, player=player_option_hm
    )
