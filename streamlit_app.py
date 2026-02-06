from collections import defaultdict
from pathlib import Path
import sqlalchemy

import streamlit as st
import altair as alt
import pandas as pd


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Parking Lot Inventory Tracker",
    page_icon=":automobile:",  # This is an emoji shortcode. Could be a URL too.
)


# -----------------------------------------------------------------------------
# Declare some useful functions.


def connect_db():
    """Connects to the mysql database."""

    DB_FILENAME = Path(__file__).parent / "server.db"
    db_already_exists = DB_FILENAME.exists()

    conn = st.connection("sql")
    db_was_just_created = not db_already_exists

    return conn, db_was_just_created


if __name__ == "__main__":
    connect_db()

