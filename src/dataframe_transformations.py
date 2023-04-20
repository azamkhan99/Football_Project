import pandas as pd
import numpy as np


class DataFrameTransformations:

    # def __call__(self):

    def events_preprocessing(self, events_json):
        """
        Input = JSON file
        Output = df
        """

        # extract event data and flatten nested columns
        events = []
        for event in events_json:
            flattened_event = {
                "id": event.get("id"),
                "index": event.get("index"),
                "period": event.get("period"),
                "timestamp": event.get("timestamp"),
                "minute": event.get("minute"),
                "second": event.get("second"),
                "type": event["type"].get("name"),
                "possession": event.get("possession"),
                "possession_team": event["possession_team"].get("name"),
                "play_pattern": event["play_pattern"].get("name"),
                "team": event["team"].get("name"),
                "player": event["player"].get("name") if "player" in event else None,
                "position": event["position"].get("name")
                if "position" in event
                else None,
                "location_x": event.get("location")[0] if "location" in event else None,
                "location_y": event.get("location")[1] if "location" in event else None,
                "duration": event.get("duration"),
                "under_pressure": event.get("under_pressure"),
                "off_camera": event.get("off_camera"),
                "out": event.get("out"),
                "related_events": event.get("related_events"),
                "tactics": event.get("tactics"),
                "obv_for_after": event.get("obv_for_after"),
                "obv_for_before": event.get("obv_for_before"),
                "obv_for_net": event.get("obv_for_net"),
                "obv_against_after": event.get("obv_against_after"),
                "obv_against_before": event.get("obv_against_before"),
                "obv_against_net": event.get("obv_against_net"),
                "obv_total_net": event.get("obv_total_net"),
            }
            events.append(flattened_event)

        df = pd.DataFrame(events)
        normalized_df = pd.json_normalize(events_json)

        return df, normalized_df

    def shots_preprocessing(self, events_json):

        # Extract data from nested 'shot' value
        shots = []
        for event in events_json:
            if event["type"]["name"] == "Shot":
                shot_data = {
                    "team": event["possession_team"]["name"],
                    "player": event["player"]["name"],
                    "x": event["location"][0],
                    "y": event["location"][1],
                    "outcome": event["shot"]["outcome"]["name"],
                    "statsbomb_xg": event["shot"]["statsbomb_xg"],
                    "aerial_won": event["shot"].get("aerial_won"),
                    "follows_dribble": event["shot"].get("follows_dribble"),
                    "first_time": event["shot"].get("first_time"),
                    "open_goal": event["shot"].get("open_goal"),
                    "one_on_one": event["shot"].get("one_on_one"),
                    "deflected": event["shot"].get("deflected"),
                    "technique": event["shot"]["technique"]["name"],
                    "shot_shot_assist": event["shot"].get("shot_assist"),
                    "shot_goal_assist": event["shot"].get("goal_assist"),
                    "body_part": event["shot"]["body_part"]["name"],
                    "type": event["type"]["name"],
                    "period": event["period"],
                }
                shots.append(shot_data)

        # Create DataFrame from extracted data
        shots_df = pd.DataFrame(shots)

        return shots_df

    def passes_preprocessing(self, events_df):

        passes_df = events_df[events_df["type"] == "Pass"]

        for i, row in passes_df.iterrows():
            team = row["team"]
            player = row["player"]
            start_x = row["location_x"]
            start_y = row["location_y"]
            end_x = np.nan
            end_y = np.nan
            for j in range(i + 1, len(events_df)):
                next_row = events_df.iloc[j]
                if next_row["team"] == team:
                    if next_row["type"] == "Ball Receipt*":
                        end_x = next_row["location_x"]
                        end_y = next_row["location_y"]
                        break
                else:
                    break
            passes_df.at[i, "pass_end_location_x"] = end_x
            passes_df.at[i, "pass_end_location_y"] = end_y

        return passes_df

    def lineups_preprocessing(self, lineups_json):

        lineup_df = pd.DataFrame(lineups_json)

        return lineup_df

    def meta_preprocessing(self, meta_json):

        df = pd.json_normalize(meta_json)

        meta_df = pd.DataFrame(columns=["name", "number", "ssiId"])

        # Iterate over each row in the original dataframe
        for _, row in df.iterrows():
            # Flatten the 'homePlayers' column
            for player in row["homePlayers"]:
                # Add a new row to the new dataframe with the flattened data
                meta_df = meta_df.append(
                    {
                        "name": player["name"],
                        "number": player["number"],
                        "ssiId": player["ssiId"],
                    },
                    ignore_index=True,
                )

        meta_df = meta_df.rename(columns={"ssiId": "playerID"})

        return meta_df

    """

    def match_stats(self, shots_df):

        shots_mcfc = len(shots_df.loc[shots_df['team'] == 'Manchester City WFC'])
        shots_opp = len(shots_df.loc[shots_df['team'] == opponent])
        xg_mcfc = shots_df.loc[shots_df['team'] == 'Manchester City WFC']['statsbomb_xg']
        xg_opp = shots_df.loc[shots_df['team'] == opponent]['statsbomb_xg']
        goals_mcfc = len(shots_df.loc[(shots_df['team'] == 'Manchester City WFC') & (shots_df['outcome'] == 'Goal')])
        goals_opp = len(shots_df.loc[(shots_df['team'] == opponent) & (shots_df['outcome'] == 'Goal')])
        sot_mcfc = len(shots_df.loc[((shots_df['team'] == 'Manchester City WFC') & (shots_df['outcome'] == 'Goal')) | ((shots_df['team'] == 'Manchester City WFC') & (shots_df['outcome'] == 'Blocked')) | ((shots_df['team'] == 'Manchester City WFC') & (shots_df['outcome'] == 'Saved'))])
        sot_opp = len(shots_df.loc[((shots_df['team'] == opponent) & (shots_df['outcome'] == 'Goal')) | ((shots_df['team'] == opponent) & (shots_df['outcome'] == 'Blocked')) | ((shots_df['team'] == opponent) & (shots_df['outcome'] == 'Saved'))])
        foul_mcfc = len(df.loc[(df['type'] == 'Foul Committed') & (df['team'] == 'Manchester City WFC')])
        foul_opp = len(df.loc[(df['type'] == 'Foul Committed') & (df['team'] == opponent)])

        #Match stats table
        stats = {
            'Goals': [goals_mcfc,goals_opp],
            'Expected Goals (XG)': [xg_mcfc.sum(),xg_opp.sum()],
            'Shots': [shots_mcfc,shots_opp],
            'Shots on Target': [sot_mcfc,sot_opp],
            'Shot Conversion (%)': [(100*sot_mcfc/shots_mcfc),(100*sot_opp/shots_opp)],
            'Fouls': [foul_mcfc, foul_opp],
            'Yellow Cards': [], # or bookings
            'Corners': [],
            'Offsides': [],
            'Possession': []

        }
        stats_df = df.from_dict(stats, orient='index', columns = ['Manchester City WFC',opponent])
        stats_df.round(2)

        return stats_df

    """
