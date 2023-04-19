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
)


st.title("Visualisations")

tab1, tab2, tab3 = st.tabs(["Shot Analysis", "Passing Analysis", "Player Comparison"])
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

with tab3:
    events_df = st.session_state["events_df"]
    plot_pass_network(player="s", team="s", period=1, events_df=events_df)
