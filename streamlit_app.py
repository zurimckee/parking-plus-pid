from collections import defaultdict
from pathlib import Path


import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import time #autorefresh every 60 secs

#load database connection - and connect sqlalchemy engine
engine = create_engine(st.secrets['dialect'] + '://' + st.secrets['username'] + ':' + st.secrets['password'] + '@' + st.secrets['host'] + '/' + st.secrets['database'])


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Parking Lot Inventory Tracker",
    page_icon=":automobile:",  # This is an emoji shortcode. Could be a URL too.
)


# -----------------------------------------------------------------------------
# Declare some useful functions.

