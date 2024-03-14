import streamlit as st
import os
import pandas as pd
from openai import OpenAI


st.title("My Personal Doc Reader")
st.write("Upload the doc below:")


uploaded_file = st.file_uploader("Choose a document pdf file")
if uploaded_file is not None:

    pass
