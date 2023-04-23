import streamlit as st
import pandas as pd
import json
import pdb


from src.dataframe_transformations import DataFrameTransformations


class DataUploadPage:
    def __init__(self):

        self.events_json = None
        self.lineups_json = None
        self.meta_json = None

    def __call__(self):

        st.session_state["current_page_index"] = 0

        # Create a list of pages
        # pages = ["Data Upload", "Visualisations"]

        # Create a sidebar with a dropdown menu to select the page
        # page_number = st.sidebar.selectbox("Select a page", pages)

        st.title(self.title())
        st.write("Upload Matchday data files below")
        with st.expander("More info:"):
            st.markdown(
                "For this prototype, the events and lineups json files will be uploaded manually. In a production environment, this data would be streamed from some cloud service"
            )

        use_sample_data = st.radio(
            "", ("Use Sample Dataset for Demo", "Upload Matchday JSON Files"), index=1
        )

        if use_sample_data == "Upload Matchday JSON Files":

            col1, col2 = st.columns(2)
            dft = DataFrameTransformations()

            with col1:
                # Streamlit file uploader
                events_json = st.file_uploader(
                    "Upload the Event Data JSON file", type="json"
                )

                # Process JSON file:
                self.events_json = self.__upload_json_file(events_json)

                # Call transformation methods to create dataframes & preprocess:
                if self.events_json is not None:
                    events_df, normalized_events_df = dft.events_preprocessing(
                        self.events_json
                    )
                    # session_state.set("events", events_df)
                    if "events_df" not in st.session_state:
                        st.session_state["events_df"] = events_df

                    if "normalized_events_df" not in st.session_state:
                        st.session_state["normalized_events_df"] = normalized_events_df

                    if "events_json" not in st.session_state:
                        st.session_state["events_json"] = self.events_json

                    shots_df = dft.shots_preprocessing(self.events_json)
                    # session_state.set("shots", shots_df)
                    if "shots_df" not in st.session_state:
                        st.session_state["shots_df"] = shots_df

                    passes_df = dft.passes_preprocessing(events_df)
                    # session_state.set("passes", passes_df)
                    if "passes_df" not in st.session_state:
                        st.session_state["passes_df"] = passes_df

                    # Display Data:
                    st.write("Events Data Preview:")
                    st.write(events_df)

            with col2:
                lineups_json = st.file_uploader(
                    "Upload the Lineups Data JSON file", type="json"
                )

                # File to pandas:
                self.lineups_json = self.__upload_json_file(lineups_json)

                # Format df:
                if self.lineups_json is not None:
                    lineups_df = dft.lineups_preprocessing(self.lineups_json)
                    st.session_state["lineups"] = lineups_df

                    # Display Data:
                    st.write("Lineups Data Preview:")
                    st.write(lineups_df)
        elif use_sample_data == "Use Sample Dataset for Demo":

            dft = DataFrameTransformations()

            with open("Data_for_Upload/ManCity_Arsenal_events.json") as f:
                d = json.load(f)
            self.events_json = d

            # Call transformation methods to create dataframes & preprocess:
            if self.events_json is not None:
                events_df, normalized_events_df = dft.events_preprocessing(
                    self.events_json
                )
                # session_state.set("events", events_df)
                if "events_df" not in st.session_state:
                    st.session_state["events_df"] = events_df

                if "normalized_events_df" not in st.session_state:
                    st.session_state["normalized_events_df"] = normalized_events_df

                if "events_json" not in st.session_state:
                    st.session_state["events_json"] = self.events_json

                shots_df = dft.shots_preprocessing(self.events_json)
                # session_state.set("shots", shots_df)
                if "shots_df" not in st.session_state:
                    st.session_state["shots_df"] = shots_df

                passes_df = dft.passes_preprocessing(events_df)
                # session_state.set("passes", passes_df)
                if "passes_df" not in st.session_state:
                    st.session_state["passes_df"] = passes_df

            with open("Data_for_Upload/ManCity_Arsenal_lineups.json") as g:
                e = json.load(g)
            self.lineups_json = e

            if self.lineups_json is not None:
                lineups_df = dft.lineups_preprocessing(self.lineups_json)
                st.session_state["lineups"] = lineups_df

            col1, col2 = st.columns(2)

            with col1:
                # Display Data:
                st.write("Events Data Preview:")
                st.write(events_df)

            with col2:
                # Display Data:
                st.write("Lineups Data Preview:")
                st.write(lineups_df)

    def title(self):
        return "Data Upload"

    def __upload_json_file(self, uploaded_json):

        if uploaded_json is not None:
            json_file = json.load(uploaded_json)

        else:
            json_file = None
            print("Error in uploading the JSON file")

        return json_file

    def show_button_for_visualisations(self):

        if (
            self.events_json != None
            and self.lineups_json != None
            and self.meta_json != None
        ):
            return True

        else:
            return False


# Define the SessionState class
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get(self, key):
        return self.__dict__.get(key, None)

    def set(self, key, value):
        self.__dict__[key] = value
