import streamlit as st

from streamlit_app.st_data_upload import DataUploadPage
from streamlit_app.st_visualisations import DataVisualisations
from src.logos import TEAM_LOGOS, download_logo
from PIL import Image


def main():

    st.title("DataStrikers Football Visualisation App")

    data_upload_page = DataUploadPage()
    data_upload_page()

    if data_upload_page.show_button_for_visualisations():

        # st.button('Visualisations')
        visualisations_page = DataVisualisations()
        visualisations_page()


if __name__ == "__main__":
    main()
