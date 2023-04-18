
import streamlit as st
import pandas as pd
import json
import pdb


from src.dataframe_transformations import DataFrameTransformations


class DataUploadPage():

    def __init__(self):

        self.events_json = None
        self.lineups_json = None
        self.meta_json = None

    def __call__(self):

        st.session_state['current_page_index'] = 0
        
        # Create a list of pages
        pages = ["Data Upload", "Visualisations"]

        # Create a sidebar with a dropdown menu to select the page
        page_number = st.sidebar.selectbox("Select a page", pages)


        st.title(self.title())
        st.write("WORK ON A BETTER DESCRIPTION: Upload Match data files below")
        with st.expander("View more information on the input data upload formats"):
            st.markdown("TO DO: write a more comprehensive guide to uploading data to the app here")

        col1, col2, col3 = st.columns(3)
        dft = DataFrameTransformations()

        with col1:
            # Streamlit file uploader
            events_json = st.file_uploader("Upload the Event Data JSON file", type="json")

            # Process JSON file:
            self.events_json = self.__upload_json_file(events_json)

            # Call transformation methods to create dataframes & preprocess:
            if self.events_json is not None:
                events_df = dft.events_preprocessing(self.events_json)
                # session_state.set("events", events_df)

                shots_df = dft.shots_preprocessing(self.events_json)
                # session_state.set("shots", shots_df)

                passes_df = dft.passes_preprocessing(events_df)
                # session_state.set("passes", passes_df)

                # Display Data:
                st.write("Events Data Preview:")
                st.write(events_df)

        with col2:
            lineups_json = st.file_uploader("Upload the Lineups Data JSON file", type="json")

            # File to pandas:
            self.lineups_json = self.__upload_json_file(lineups_json)

            # Format df:
            if self.lineups_json is not None:
                lineups_df = dft.lineups_preprocessing(self.lineups_json)

                # Display Data:
                st.write("Lineups Data Preview:")
                st.write(lineups_df)

        with col3:
            # Streanlit file upload:
            meta_json = st.file_uploader("Upload the Meta Data JSON file", type="json")

            # Process JSON file:
            self.meta_json = self.__upload_json_file(meta_json)

            # Format df:
            if self.meta_json is not None: 
                meta_df = dft.meta_preprocessing(self.meta_json)

                # Display Data:
                st.write("Meta Data Preview:")
                st.write(meta_df)            

    
    def title(self):
        return "Data Upload"


    def __upload_json_file(self, uploaded_json):

        if uploaded_json is not None:
            json_file = json.load(uploaded_json)

        else:
            json_file = None
            print('Error in uploading the JSON file')

        return json_file


    def show_button_for_visualisations(self):

        if self.events_json != None and self.lineups_json != None and self.meta_json != None:
            return True

        else:
            return False

    '''

    def __upload_nested_json_file(self, uploaded_json):

        if uploaded_json is not None:
            json_data = json.load(uploaded_json)
            df = pd.json_normalize(json_data)

        else:
            df = None
            print('Error in uploading the JSON file')
        
        return df

    '''


# Define the SessionState class
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def get(self, key):
        return self.__dict__.get(key, None)

    def set(self, key, value):
        self.__dict__[key] = value






