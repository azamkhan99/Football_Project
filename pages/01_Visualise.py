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
    plot_full_pass_network,
)
from src.spider import RadarChartMetrics
from soccerplots import radar_chart
from soccerplots.radar_chart import Radar
from PIL import Image

with st.sidebar.container():
        image = Image.open("Manchester_City_FC_badge.svg.webp")
        st.image(image)


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


shots_df = st.session_state["shots_df"]
events_df = st.session_state["events_df"]
lineup_df = st.session_state["lineups"]
events_json = st.session_state["normalized_events_df"]
_, goals_mcfc, goals_opp = create_base_stats(
    lineup_df=lineup_df, shots_df=shots_df, df=events_df, json=events_json
)

opponent = lineup_df.iloc[1, 1]
st.title(f"Manchester City WFC [{goals_mcfc} - {goals_opp}] {opponent}")
pad1, title, pad2 = st.columns((1, 8, 1))
# with title:
#     st.title(f"Manchester City WFC {goals_mcfc} - {goals_opp} {opponent}")

col1, col2 = st.columns(2, gap="medium")
if goals_mcfc > goals_opp:
    result = "Win"
elif goals_mcfc == goals_opp:
    result = "Draw"
else:
    result = "Loss"
if result == "Loss":

    with col1:

        step_graph(events_json, opponent, period=1)

        create_pass_network(
            team=opponent,
            period=1,
            data=events_df,
            json=events_json,
            detail=False
        )

    with col2:

        st.dataframe(_.style.set_precision(0), use_container_width=True)

        plot_full_pass_network(
            team=opponent,
            period=1,
            events_df=events_df,
        )

if result == "Win":

    with col1:

        step_graph(events_json, opponent, period=1)

        create_pass_network(
            team="Manchester City WFC",
            period=1,
            data=events_df,
            json=events_json,
            detail=False
        )

    with col2:

        st.dataframe(_.style.set_precision(0), use_container_width=True)

        create_shots_vis(team="Manchester City WFC", period=1, shots_df=shots_df,detail=False)
