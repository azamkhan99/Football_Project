import json
import pandas as pd
from mplsoccer import Pitch, FontManager, Sbopen
from matplotlib import rcParams
import matplotlib.pyplot as plt
from mplsoccer.pitch import Pitch
import seaborn as sns
from soccerplots import radar_chart
from soccerplots.radar_chart import Radar
import streamlit as st
import numpy as np


class RadarChartMetrics:
    def __init__(self, period, team, shots_df, events_json, events_df):
        # self.player = player
        self.period = period
        self.team = team
        self.events_json = events_json
        self.events_df = events_df
        self.shots_df = shots_df

        self.metrics = {}
        self.lineup = events_df["player"][events_df["team"] == self.team].unique()
        self.spider_values = []

    def run_all_metrics(self):
        self.get_shots_metrics()
        self.get_passes_metrics()
        self.get_dribble_metrics()
        self.get_duel_metrics()
        self.get_interceptions()

    def get_lineup(self):
        return self.lineup

    def get_player_positions(self, position_dict):
        df_all = pd.json_normalize(self.events_json)
        lineup1 = df_all.loc[df_all["team.name"] == self.team]["tactics.lineup"].iloc[0]
        numbers = pd.json_normalize(lineup1)
        numbers = numbers[["player.name", "position.name"]]

        lineup = numbers.apply(
            lambda row: f"{row['player.name']} - {position_dict.get(row['position.name'])}",
            axis=1,
        ).tolist()

        return lineup

    def get_shots_metrics(self):
        shots_df = self.shots_df
        # filter for shots with 'outcome' of 'Goal', 'period' of 1, and team of 'Manchester City WFC'
        if self.period == "FT":
            shots_filter = (shots_df["outcome"] == "Goal") & (
                shots_df["team"] == self.team
            )
        else:
            shots_filter = (
                (shots_df["outcome"] == "Goal")
                & (shots_df["period"] == self.period)
                & (shots_df["team"] == self.team)
            )

        # create a new DataFrame with the filtered data
        shots_success_df = shots_df.loc[
            shots_filter, ["player", "team", "period", "outcome"]
        ]
        shots_success_df = shots_success_df.loc[
            (shots_success_df["outcome"] == "Goal")
            & (shots_success_df["team"] == self.team)
        ]
        shots_success_df = (
            shots_success_df.groupby("player")
            .size()
            .reset_index(name="successful_shots")
        )

        # return shots_success_df
        self.metrics["shots_success"] = shots_success_df

    def get_passes_metrics(self):
        # pass metrics
        df = self.events_df
        passes_df = df[df["type"] == "Pass"]
        if self.period == "FT":
            passes_period1_mancity = passes_df[(passes_df["team"] == self.team)]
        else:
            passes_period1_mancity = passes_df[
                (passes_df["period"] == self.period) & (passes_df["team"] == self.team)
            ]

        passes_count = (
            passes_period1_mancity[passes_period1_mancity["type"] == "Pass"]
            .groupby("player")
            .count()["type"]
        )
        passes_count_df = passes_count.reset_index().rename(
            columns={"type": "successful_passes", "player": "player"}
        )

        # return passes_count_df
        self.metrics["passes_count"] = passes_count_df

    def get_dribble_metrics(self):

        data = self.events_json

        # Extract data from dribble events
        dribbles = []
        for event in data:
            if event["type"]["name"] == "Dribble":
                dribble_data = {
                    "team": event["possession_team"]["name"],
                    "player": event["player"]["name"],
                    "outcome": event["dribble"].get("outcome"),
                    "type": event["type"]["name"],
                    "period": event["period"],
                }
                dribbles.append(dribble_data)

        # Create DataFrame from extracted data
        dribbles_df = pd.DataFrame(dribbles)
        if self.period != "FT":
            dribbles_df = dribbles_df[(dribbles_df["period"]) == self.period]

        # Apply a lambda function to extract the "name" value from the "outcome" dictionary
        dribbles_df["outcome"] = dribbles_df["outcome"].apply(lambda x: x["name"])

        complete_dribbles_df = dribbles_df.loc[
            (dribbles_df["outcome"] == "Complete") & (dribbles_df["team"] == self.team)
        ]
        successful_dribbles = (
            complete_dribbles_df.groupby("player")
            .size()
            .reset_index(name="successful_dribbles")
        )

        # return successful_dribbles
        self.metrics["successful_dribbles"] = successful_dribbles

    def get_duel_metrics(self):
        # Extract data from dribble events

        data = self.events_json
        duels = []
        for event in data:
            if event["type"]["name"] == "Duel":
                duels_data = {
                    "team": event["possession_team"]["name"],
                    "player": event["player"]["name"],
                    "outcome": event["duel"].get("outcome"),
                    "type": event["type"]["name"],
                    "period": event["period"],
                }
                duels.append(duels_data)

        # Create DataFrame from extracted data
        duels_df = pd.DataFrame(duels)
        if self.period != "FT":
            duels_df = duels_df[(duels_df["period"]) == self.period]
        duels_df = duels_df.loc[duels_df["outcome"].notnull()]
        duels_df["outcome"] = duels_df["outcome"].apply(lambda x: x["name"])
        success_duels_df = duels_df.loc[
            duels_df["outcome"].str.contains("success|won", case=False)
            & (duels_df["team"] == "Manchester City WFC")
        ]
        success_duels = (
            success_duels_df.groupby("player")["outcome"]
            .size()
            .reset_index(name="successful_duels")
        )

        # return success_duels
        self.metrics["success_duels"] = success_duels

    def get_interceptions(self):

        # Extract data from interception events
        interceptions = []
        data = self.events_json
        for event in data:
            if event["type"]["name"] == "Interception":
                interception_data = {
                    "team": event["possession_team"]["name"],
                    "player": event["player"]["name"],
                    "outcome": event["interception"].get("outcome"),
                    "type": event["type"]["name"],
                    "period": event["period"],
                }
                interceptions.append(interception_data)

        # Create DataFrame from extracted data
        interceptions_df = pd.DataFrame(interceptions)
        if self.period != "FT":
            interceptions_df = interceptions_df[
                (interceptions_df["period"]) == self.period
            ]
        interceptions_df = interceptions_df.loc[interceptions_df["team"] != self.team]
        successful_interceptions = (
            interceptions_df.groupby("player")
            .size()
            .reset_index(name="successful_interceptions")
        )
        # return successful_interceptions
        self.metrics["successful_interceptions"] = successful_interceptions

    def get_data(self):

        shots_success_df = self.metrics["shots_success"]
        successful_dribbles = self.metrics["successful_dribbles"]
        passes_count_df = self.metrics["passes_count"]
        success_duels = self.metrics["success_duels"]
        successful_interceptions = self.metrics["successful_interceptions"]

        # Merge dataframes
        metrics_df = shots_success_df.merge(
            passes_count_df, on="player", how="outer"
        ).fillna(0)
        metrics_df = metrics_df.merge(
            successful_dribbles, on="player", how="outer"
        ).fillna(0)
        metrics_df = metrics_df.merge(success_duels, on="player", how="outer").fillna(0)
        metrics_df = metrics_df.merge(
            successful_interceptions, on="player", how="outer"
        ).fillna(0)
        metrics_df["total_actions"] = (
            metrics_df["successful_shots"]
            + metrics_df["successful_passes"]
            + metrics_df["successful_dribbles"]
            + metrics_df["successful_duels"]
            + metrics_df["successful_interceptions"]
        )
        metrics_df = metrics_df.sort_values(
            "total_actions", ascending=False
        ).reset_index(drop=True)

        return metrics_df

    class SpiderChartValues:
        def __init__(self, params, ranges, df, player) -> None:
            self.params = params
            self.ranges = ranges
            self.df = df
            self.player = player

    def generate_spider_chart_values_df(self):

        self.run_all_metrics()

        shots_success_df = self.metrics["shots_success"]
        successful_dribbles = self.metrics["successful_dribbles"]
        passes_count_df = self.metrics["passes_count"]
        success_duels = self.metrics["success_duels"]
        successful_interceptions = self.metrics["successful_interceptions"]

        # concatenate the dataframes using outer join on the 'player' column
        all_df = pd.concat(
            [
                passes_count_df,
                shots_success_df,
                successful_interceptions,
                success_duels,
                successful_dribbles,
            ],
            join="outer",
            sort=False,
        )

        # groupby the dataframe by the 'player' column and sum the values
        all_df = all_df.groupby("player", as_index=False).sum()

        # sort the dataframe by the 'player' column
        all_df = all_df.sort_values(by="player")

        float_cols = all_df.select_dtypes(include="float64").columns
        all_df[float_cols] = all_df[float_cols].astype(int)
        int32_cols = all_df.select_dtypes(include="int32").columns
        all_df[int32_cols] = all_df[int32_cols].round()
        # all_df.set_index("player", inplace=True)

        return all_df

    def generate_spider_chart_values(self, player):

        self.run_all_metrics()

        shots_success_df = self.metrics["shots_success"]
        successful_dribbles = self.metrics["successful_dribbles"]
        passes_count_df = self.metrics["passes_count"]
        success_duels = self.metrics["success_duels"]
        successful_interceptions = self.metrics["successful_interceptions"]

        # concatenate the dataframes using outer join on the 'player' column
        all_df = pd.concat(
            [
                passes_count_df,
                shots_success_df,
                successful_interceptions,
                success_duels,
                successful_dribbles,
            ],
            join="outer",
            sort=False,
        )
        all_df.rename(
            columns={
                "successful_passes": "Succesful Passes",
                "successful_shots": "Shot Success",
                "successful_interceptions": "Successful Interceptions",
                "successful_duels": "Duel Success",
                "successful_dribbles": "Successful Dribbles",
            },
            inplace=True,
        )

        # groupby the dataframe by the 'player' column and sum the values
        all_df = all_df.groupby("player", as_index=False).sum()

        # sort the dataframe by the 'player' column
        all_df = all_df.sort_values(by="player")

        float_cols = all_df.select_dtypes(include="float64").columns
        all_df[float_cols] = all_df[float_cols].astype(int)
        int32_cols = all_df.select_dtypes(include="int32").columns
        all_df[int32_cols] = all_df[int32_cols].round()
        # all_df.set_index("player", inplace=True)
        filter_all = all_df[all_df["player"] == player]
        filter_all.set_index("player", inplace=True)

        ## setting parameters
        params = filter_all.columns.tolist()
        ## setting range values
        # ranges = [(0, 50), (0, 5), (0, 5), (0, 5), (0, 5)]
        ranges = [
            (0, filter_all["Succesful Passes"].max().round(1) + 5),
            (0, 5),
            (0, 5),
            (0, 5),
            (0, 5),
        ]

        self.spider_values.append(
            self.SpiderChartValues(
                params=params, ranges=ranges, df=filter_all, player=player
            )
        )

    def generate_spider_chart(self, spider_chart_values: SpiderChartValues):

        filter_all = spider_chart_values.df
        values = filter_all.iloc[0]
        ## titles to make it pretty
        title = dict(
            title_name=f"{spider_chart_values.player} - Half: {self.period}",
            title_color="#000000",
            subtitle_name=f"{self.team}",
            subtitle_color="#D00027",
            title_fontsize=18,
            subtitle_fontsize=15,
        )
        ## instantiate object
        radar = Radar()
        ## plotting the radar chart
        fig, ax = radar.plot_radar(
            ranges=spider_chart_values.ranges,
            params=spider_chart_values.params,
            values=values,
            radar_color=["#6CADDF", "#FFFFFF"],
            title=title,
        )
        return fig, ax

    def generate_comparison_chart(self, player1, player2):

        self.run_all_metrics()

        shots_success_df = self.metrics["shots_success"]
        successful_dribbles = self.metrics["successful_dribbles"]
        passes_count_df = self.metrics["passes_count"]
        success_duels = self.metrics["success_duels"]
        successful_interceptions = self.metrics["successful_interceptions"]

        # concatenate the dataframes using outer join on the 'player' column
        all_df = pd.concat(
            [
                passes_count_df,
                shots_success_df,
                successful_interceptions,
                success_duels,
                successful_dribbles,
            ],
            join="outer",
            sort=False,
        )
        all_df.rename(
            columns={
                "successful_passes": "Succesful Passes",
                "successful_shots": "Shot Success",
                "successful_interceptions": "Successful Interceptions",
                "successful_duels": "Duel Success",
                "successful_dribbles": "Successful Dribbles",
            },
            inplace=True,
        )
        st.dataframe(all_df)

        # groupby the dataframe by the 'player' column and sum the values
        all_df = all_df.groupby("player", as_index=False).sum()

        # sort the dataframe by the 'player' column
        all_df = all_df.sort_values(by="player")

        float_cols = all_df.select_dtypes(include="float64").columns
        all_df[float_cols] = all_df[float_cols].astype(int)
        int32_cols = all_df.select_dtypes(include="int32").columns
        all_df[int32_cols] = all_df[int32_cols].round()
        # all_df.set_index("player", inplace=True)
        filter_all1 = all_df[all_df["player"] == player1]
        filter_all2 = all_df[all_df["player"] == player2]
        filter_all1.set_index("player", inplace=True)
        filter_all2.set_index("player", inplace=True)

        ## setting parameters
        params = filter_all1.columns.tolist()
        ## setting range values
        ranges = [(0, 50), (0, 5), (0, 5), (0, 5), (0, 5)]

        ## For Comparison. No need to add new ranges and params since it will be the same.
        ## setting parameter values of both players
        val_comp = filter_all1.iloc[0], filter_all2.iloc[0]
        ## titles for each players
        title_comp = dict(
            title_name=f"{player1}",
            title_color="#D00027",
            subtitle_name=f"{self.team}",
            subtitle_color="#000000",
            title_name_2=f"{player2}",
            title_color_2="#00A398",
            subtitle_name_2=f"team2",
            subtitle_color_2="#000000",
            title_fontsize=18,
            subtitle_fontsize=15,
        )
        ## plotting the radar chart
        radar = Radar()
        fig, ax = radar.plot_radar(
            ranges=ranges,
            params=params,
            values=val_comp,
            radar_color=["#D00027", "#00A398"],
            title=title_comp,
            compare=True,
        )
        return fig, ax

    # def comparison_spider(
    #     self, player1_values: SpiderChartValues, player2_values: SpiderChartValues
    # ):

    #     filter_all1 = player1_values.df
    #     filter_all2 = player2_values.df

    #     val_comp = filter_all1.iloc[0], filter_all2.iloc[0]
    #     ## titles for each players
    #     title_comp = dict(
    #         title_name=f"{player1_values.player}",
    #         title_color="#D00027",
    #         subtitle_name=f"{self.team}",
    #         subtitle_color="#000000",
    #         title_name_2=f"{player2_values.player}",
    #         title_color_2="#00A398",
    #         subtitle_name_2=f"team2",
    #         subtitle_color_2="#000000",
    #         title_fontsize=18,
    #         subtitle_fontsize=15,
    #     )
    #     ## plotting the radar chart
    #     radar = Radar()
    #     fig, ax = radar.plot_radar(
    #         ranges=player1_values.ranges,
    #         params=player2_values.params,
    #         values=val_comp,
    #         radar_color=["#D00027", "#00A398"],
    #         title=title_comp,
    #         compare=True,
    #     )
    #     return fig, ax
