from streamlit_app.st_main import main
import streamlit as st
from PIL import Image

st.set_page_config(layout="wide", page_icon=Image.open("mnc.png"))  # page_title='Stroke Prediction',

main()
