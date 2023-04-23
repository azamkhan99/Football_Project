import streamlit as st

from streamlit_app.st_data_upload import DataUploadPage
from streamlit_app.st_visualisations import DataVisualisations
from src.logos import TEAM_LOGOS, download_logo
from PIL import Image


def main():

    col1, col2 = st.columns((0.4, 3))

    with col1:
        image = Image.open("Manchester_City_FC_badge.svg.webp")

        st.image(image, use_column_width=True)

    with col2:
        st.title(":blue[Data Strikers]")
        st.title("Matchday Statistics & Visualisation App")

    data_upload_page = DataUploadPage()
    data_upload_page()

    if data_upload_page.show_button_for_visualisations():

        # st.button('Visualisations')
        visualisations_page = DataVisualisations()
        visualisations_page()


if __name__ == "__main__":
    main()
