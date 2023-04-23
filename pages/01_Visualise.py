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
    lineup_df=lineup_df, shots_df=shots_df, df=events_df, json=events_json, period=0
)



opponent = lineup_df.iloc[1, 1]

TEAM_LOGOS = {
    "Manchester City WFC": "https://www.google.co.uk/url?sa=i&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FManchester_City_F.C.&psig=AOvVaw0zgK4-gW-T1YiIANBSewSj&ust=1682188967779000&source=images&cd=vfe&ved=0CBAQjRxqFwoTCIC80bDQu_4CFQAAAAAdAAAAABAE",
    "Liverpool WFC": "https://logos-world.net/wp-content/uploads/2020/06/Liverpool-Logo.png",
    "Arsenal WFC": "https://logos-world.net/wp-content/uploads/2020/05/Arsenal-Logo.png",
    "Tottenham Hotspur Women": "https://logos-world.net/wp-content/uploads/2020/05/Arsenal-Logo.png",
    "Aston Villa": "https://upload.wikimedia.org/wikipedia/en/thumb/f/f9/Aston_Villa_FC_crest_%282016%29.svg/1200px-Aston_Villa_FC_crest_%282016%29.svg.png",
    "Brighton & Hove Albion WFC": "https://upload.wikimedia.org/wikipedia/en/thumb/f/fd/Brighton_%26_Hove_Albion_logo.svg/1200px-Brighton_%26_Hove_Albion_logo.svg.png",
    "Leicester City WFC": "https://upload.wikimedia.org/wikipedia/en/thumb/2/2d/Leicester_City_crest.svg/1200px-Leicester_City_crest.svg.png"
    # Add more team names and logo URLs here
}
opp_image = TEAM_LOGOS[opponent]
left, col1, col2 , col3 = st.columns([2,1.3,7,3])
with col1:
    image = Image.open("Manchester_City_FC_badge.svg.webp")
    st.image(image, width=100)
with col2:
    st.title(f"Manchester City WFC [{goals_mcfc} - {goals_opp}] {opponent}")
with col3:
    st.image(opp_image, width=180)
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
        
        create_pass_network(
            team=opponent,
            period=1,
            data=events_df,
            json=events_json,
            detail=False
        )
        step_graph(events_json, opponent, period=1)

        

    with col2:
        plot_full_pass_network(
            team=opponent,
            period=1,
            events_df=events_df,
        )
        
        s = _.style.highlight_max(props='color:red', axis=1)\
            .set_precision(0)
        st.dataframe(s, use_container_width=True)

        

if result == "Win":
    with col1:
        create_pass_network(
            team="Manchester City WFC",
            period=1,
            data=events_df,
            json=events_json,
            detail=False
        )
        step_graph(events_json, opponent, period=1, detail=False)

       

    with col2:
        create_shots_vis(team="Manchester City WFC", period=1, shots_df=shots_df,detail=False)
        s = _.style.highlight_max(props='color:red', axis=1)\
                    .set_precision(0)
        st.subheader('Key Match Stats')
        st.dataframe(s, use_container_width=True)
       
        
