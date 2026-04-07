from collections import defaultdict
from pathlib import Path

import streamlit as st
import altair as alt
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import datetime 

#load database connection - and connect sqlalchemy engine
conn = st.secrets["connections"]["sql"]
engine = create_engine(
    conn['dialect'] + '+' + conn['driver'] + '://' + 
    conn['username'] + ':' + conn['password'] + '@' + 
    conn['host'] + ':' + str(conn['port']) + '/' + conn['database'])


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="Parking Lot Inventory Tracker",
    layout="wide",
    page_icon=":automobile:",  # This is an emoji shortcode. Could be a URL too.
)

title_row = st.container(horizontal=True, vertical_alignment="top")
with title_row:
    st.title("Parking+ Dashboard", text_alignment="center", width="stretch")
    st.write("Auto-refreshes every 60 seconds. Click the button below to manually refresh.")
    if 'last_refresh' not in st.session_state:
        st.session_state['last_refresh'] = datetime.datetime.now()
    if st.button("🔄 Manual Refresh"):
        st.session_state['last_refresh'] = datetime.datetime.now()
    st.caption(f"Last refreshed: {st.session_state['last_refresh'].strftime('%Y-%m-%d %H:%M:%S')}")


# --- Load Data ---
@st.cache_data(ttl=60)  # Cache data for 60 seconds

# -- occupancy summary and kpi cards --
def get_occupancy_data():
    with engine.connect() as conn:
        lot_summary = pd.read_sql("SELECT * FROM Lot_Status_Summary", conn)

        offline_sensors = pd.read_sql("SELECT COUNT(*) AS offline_count FROM Sensor_Health WHERE Is_Online = FALSE", conn)

        active_lots = pd.read_sql("SELECT COUNT(*) AS active_count FROM Lots WHERE Is_Active = TRUE", conn)

    return lot_summary, offline_sensors, active_lots


lot_summary, offline_sensors, active_lots = get_occupancy_data()

total_spaces = lot_summary['Total_Spaces'].sum()
occupied = lot_summary['Occupied_Count'].sum()
available = lot_summary['Num_Spaces'].sum() 
occupancy_rate = round((occupied / total_spaces * 100), 1) if total_spaces > 0 else 0
num_offline = offline_sensors['offline_count'].iloc[0]
num_active = active_lots['active_count'].iloc[0]


st.subheader("Parking Lot Occupancy Overview")
col1, col2, col3, col4 = st.columns(4)
    
col1.metric(label ="Total Spaces", value = total_spaces)
col2.metric(label = "Available Spaces", value = available, delta = f"{occupancy_rate}% Occupied", delta_color="inverse")
col3.metric(label = "Active Lots", value = num_active)
col4.metric(label = "Offline Sensors", value = num_offline, delta = "Needs Attention" if num_offline > 0 else "All Online", delta_color = "inverse" if num_offline > 0 else "off")

# -- occupancy by lot bar chart --
def get_occupancy_by_lot():
    with engine.connect() as conn:
        summary_overall = pd.read_sql("SELECT * FROM Lot_Status_Summary", conn)

        spot_types = pd.read_sql("SELECT * FROM Spot_Status_Summary", conn)

        near_capacity = pd.read_sql("SELECT * FROM Near_Capacity", conn)
    return summary_overall, spot_types, near_capacity


st.subheader("Lot Level Occupancy")
summary, spot_types, near_capacity = get_occupancy_by_lot()

occupancy_perc = near_capacity['Occupancy_Perc']

summary["Occupancy"] = (
    summary["Occupied_Count"] / summary["Total_Spaces"] * 100
).round(1)
 
fig = px.bar(
    summary,
    x="Lot_Name",
    y=["Num_Spaces", "Occupied_Count"],
    title="Available vs Occupied by Lot",
    labels={"value": "Spaces", "variable": ""},
    color_discrete_map={
        "Num_Spaces": "#4CAF50",
        "Occupied_Count": "#F44336"
    },
    barmode="stack"
)
st.plotly_chart(fig, use_container_width=True)


if not occupancy_perc.empty:
    st.warning(f" {len(near_capacity)} lot(s) are over 80% capacity")
    st.dataframe(near_capacity[["Lot_Name", "Occupancy_Perc"]], use_container_width=True)
else:
    st.success("All lots are mostly available!")


# -- spot type details --

st.subheader("Spot Type Breakdown")
fig2 = px.bar(
    spot_types,
    x = "Lot_Name",
    y = "Count",
    color= "Spot_Type",
    title="Spot Types by Lot",
    barmode="group"
)
st.plotly_chart(fig2, use_container_width=True)

# -- collapsable tables for raw data -- 
with st.expander("Raw lot data"):
    st.dataframe(summary, use_container_width=True)

with st.expander("Raw spot data"):
    st.dataframe(spot_types, use_container_width=True)


def get_trend_data():
    with engine.connect() as conn:
        hourly = pd.read_sql("SELECT * FROM Hourly_Occupancy", conn)
        daily = pd.read_sql("SELECT * FROM Daily_Occupancy", conn)
        peak =  pd.read_sql("SELECT * FROM Peak_Occupancy LIMIT 1", conn)
    
    hourly.columns = ["Hour", "Events", "Occupancies", "Departures"]
    daily.columns  = ["Day", "Events", "Occupancies", "Departures"]

    return hourly, daily, peak

st.subheader("Occupancy Trends")
hourly, daily, peak = get_trend_data()

peak_hour_value = int(peak['Hour'].iloc[0]) if not peak.empty else None
peak_label = f"{peak_hour_value}:00 - {peak_hour_value + 1}:00" if peak_hour_value is not None else "N/A"

st.metric(label="Busiest Hour", value=peak_label)
col5, col6 = st.columns(2)

with col5:
    if not hourly.empty:
        hourly_melted = hourly.melt(
            id_vars="Hour",
            value_vars=["Occupancies", "Departures"],
            var_name="Events",
        )
        fig3 = px.line(
            hourly_melted,
            x="Hour",
            y="Events",
            title="Today's Activity by Hour",
            markers=True
        )
        fig3.update_layout(xaxis_title="Hour of Day", yaxis_title="Events")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No activity logged today.")

with col6:
    if not daily.empty:
        daily_melted = daily.melt(
            id_vars="Day",
            value_vars=["Occupancies", "Departures"],
            var_name="Events",
        )
        fig4 = px.bar(
            daily_melted,
            x="Day",
            y="Events",
            title="This Week's Daily Activity",
            barmode="group"
        )
        fig4.update_layout(xaxis_title="Date", yaxis_title="Events")
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No activity logged this week.")