from streamlit_app.st_main import main
import streamlit as st
from PIL import Image


        
st.set_page_config(layout="wide")  # page_title='Stroke Prediction',
with st.sidebar.container():
        image = Image.open("Manchester_City_FC_badge.svg.webp")
        st.image(image)

main()
