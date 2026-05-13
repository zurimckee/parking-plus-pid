from collections import defaultdict
from pathlib import Path

import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from sqlalchemy import text
import datetime 


def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    
    

is_admin = check_password()

# -- initialize session state for admin messages --
if "admin_message" not in st.session_state:
    st.session_state.admin_message = None
# -- maybe move this under overview if claude fixes dont work
if st.session_state.admin_message:
    st.success(st.session_state.admin_message)
    st.session_state.admin_message = None


#load database connection - and connect sqlalchemy engine
db = st.secrets["mysql"]
# Format: mysql+pymysql://user:password@host:port/database
database_url = f"mysql+pymysql://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}"
engine = create_engine(database_url)


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(
    page_title="ParkingPlus Dashboard",
    layout="wide",
    page_icon=":🚗",  # This is an emoji shortcode. Could be a URL too.
    menu_items={
        'Get help': 'https://smartparkingplus.lovable.app',
        'Report a bug': "mailto:zurimckee95@gmail.com"
    }
)

title_row = st.container(horizontal=True, vertical_alignment="top")
with title_row:
    st.title("Parking+ Dashboard", text_alignment="center", width="stretch")

refresh_row = st.container(horizontal=True, vertical_alignment="top")
with refresh_row:
    st.write("Auto-refreshes every 60 seconds. Click the button below to manually refresh.")
    if 'last_refresh' not in st.session_state:
        st.session_state['last_refresh'] = datetime.datetime.now()
    if st.button("🔄 Manual Refresh"):
        st.session_state['last_refresh'] = datetime.datetime.now()
st.caption(f"Last refreshed: {st.session_state['last_refresh'].strftime('%Y-%m-%d %H:%M:%S')}")


# --- Load Data ---
@st.cache_data(ttl=60)  # Cache data for 60 seconds


def load_all_data():
    with engine.connect() as conn:
        lot_summary = pd.read_sql("SELECT * FROM Lot_Status_Summary", conn)
        raw_lot_info = pd.read_sql("SELECT ls.*, l.Latitude, l.Longitude, l.Lot_Type FROM Lot_Status_Summary ls JOIN Lots l ON ls.Lot_ID = l.Lot_ID", conn)
        offline_sensors = pd.read_sql("SELECT COUNT(*) AS offline_count FROM Sensor_Health WHERE Is_Online = FALSE", conn)
        active_lots = pd.read_sql("SELECT COUNT(*) AS active_count FROM Lots WHERE Is_Active = TRUE", conn)
        spot_types = pd.read_sql("SELECT * FROM Spot_Status_Summary", conn)
        near_capacity = pd.read_sql("SELECT * FROM Near_Capacity", conn)
        hourly = pd.read_sql("SELECT * FROM Hourly_Occupancy", conn)
        daily = pd.read_sql("SELECT * FROM Daily_Occupancy", conn)
        peak =  pd.read_sql("SELECT * FROM Peak_Occupancy LIMIT 1", conn)
    hourly.columns = ["Hour", "Events", "Occupancies", "Departures"]
    daily.columns  = ["Day", "Events", "Occupancies", "Departures"]

    return lot_summary, raw_lot_info, offline_sensors, active_lots, spot_types, near_capacity, hourly, daily, peak


lot_summary, raw_lot_info, offline_sensors, active_lots, spot_types, near_capacity, hourly, daily, peak = load_all_data()

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



tab3, tab4 = st.tabs(["Lot Level Occupancy", "Spot Type Breakdown"])
with tab3:
    st.subheader("Parking Lot Occupancy")

    occupancy_perc = near_capacity['Occupancy_Perc']

    lot_summary["Occupancy"] = (
        lot_summary["Occupied_Count"] / lot_summary["Total_Spaces"] * 100
    ).round(1).astype(str) + "%"
    
    fig = px.bar(
        lot_summary,
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
        st.warning(f" {len(near_capacity)} lot(s) are over 80% capacity.")
        st.dataframe(near_capacity[["Lot_Name", "Occupancy_Perc"]], use_container_width=False)
    else:
        st.success("All lots are mostly available!")


# -- spot type details --

with tab4:
    st.subheader("Parking Spot Type Breakdown")
    fig2 = px.bar(
        spot_types,
        x = "Lot_Name",
        y = "Count",
        color= "Spot_Type",
        title="Spot Types by Lot",
        barmode="group"
    )
    st.plotly_chart(fig2, use_container_width=True)

    if not spot_types.empty:
        st.warning("Some lots have a high number of handicapped, staff, or reserved spots which may limit availability for general users")
    

# -- collapsable tables for raw data -- 
with st.expander("Raw lot data"):
    st.dataframe(raw_lot_info, use_container_width=True)

with st.expander("Raw spot data"):
    st.dataframe(spot_types, use_container_width=True)




with st.container(border=True):
    st.subheader("Occupancy Trends")
    st.info("Trends are based on parking activity logged in the past 7 days. Hourly trends show today's activity by hour, while daily trends show the past week's activity by day.")

    peak_hour_value = int(peak['Hour'].iloc[0]) if not peak.empty else None
    peak_label = f"{peak_hour_value}:00 - {peak_hour_value + 1}:00" if peak_hour_value is not None else "N/A"

    st.metric(label="Busiest Hour", value=peak_label)
    tab1, tab2 = st.tabs(["Hourly", "Daily"])
    with tab1:
        if not hourly.empty:
            hourly_melted = hourly.melt(
                id_vars="Hour",
                value_vars=["Occupancies", "Departures"],
                var_name="Events",
                value_name="Count"
            )
            fig3 = px.line(
                hourly_melted,
                x="Hour",
                y="Count",
                color="Events",
                title="Today's Activity by Hour",
                markers=True
            )
            fig3.update_layout(xaxis_title="Hour of Day", yaxis_title="Count")
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No activity logged today.")

    with tab2:
        if not daily.empty:
            daily_melted = daily.melt(
                id_vars="Day",
                value_vars=["Occupancies", "Departures"],
                var_name="Events",
                value_name="Count"
            )
            fig4 = px.line(
                daily_melted,
                x="Day",
                y="Count",
                color="Events",
                title="This Week's Daily Activity",
                markers=True
            )
            fig4.update_layout(xaxis_title="Date", yaxis_title="Count")
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.info("No activity logged this week.")

# --- ADMIN CONTROLS PANEL ---


with st.sidebar:
    st.header("Admin Control Panel")

    # Login/logout widget
    if not st.session_state.authenticated:
        with st.expander("Admin Login"):
            password = st.text_input("Password", type="password", key="pw_input")
            if st.button("Login"):
                if password == st.secrets["auth"]["admin_password"]:
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Incorrect password")
    else:
        st.success("Logged in as Admin")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()


        lot_tab, spot_tab, sensor_tab = st.tabs(["Manage Lots", "Manage Spots", "Manage Sensors"])


        with lot_tab:
            st.subheader("Lot Management", help= "Manage parking lots (e.g. for maintenance or special events)")
            st.write("Use the controls below to update the status of existing lots, add new lots, or delete lots from the database. Changes will be reflected in the dashboard after refreshing.")
            active_lot, add_lot, delete_lot = st.tabs(["Update Lot Status", "Add New Lot", "Delete Lot"])
            # ------ LOTS ------
            with active_lot:
                st.subheader("Update Lot Status", help= "Manually activate or deactivate a parking lot")
                lot_options = lot_summary["Lot_Name"].tolist()
                selected_lot = st.selectbox("Select lot", lot_options)  
                new_status = st.toggle("Active")
                if st.button("Update Lot Status"):
                    if not st.session_state.authenticated:
                        st.warning("🔒 Login as admin to make changes.")
                    else:
                        with engine.connect() as conn:
                            conn.execute(
                                text("UPDATE Lots SET Is_Active = :status WHERE Lot_Name = :name"),
                                {"status": new_status, "name":selected_lot}
                            )
                            conn.commit()

                        st.session_state.admin_message = f"Updated {selected_lot} to {'Active' if new_status == True else 'Inactive'}"
                        st.cache_data.clear()
                        st.rerun()

            with add_lot:
                st.subheader("Add a new Parking Lot", help="Add a new parking lot to the database, new lots will be set to active by default")
                lot_id = st.text_input("Enter Lot ID", placeholder="Enter Lot ID (e.g. L002)")
                lot_name = st.text_input("Enter Lot Name", placeholder="Enter Lot Name (e.g. South Lot)")
                address = st.text_input("Enter Lot Address", placeholder="Enter Lot Address")
                lot_type = st.selectbox("Select Lot Type", ["Deck", "Lot", "Street"])


                if st.button("Add Lot"):
                    if not st.session_state.authenticated:
                        st.warning("🔒 Login as admin to make changes.")
                    else:
                        with engine.connect() as conn:
                            conn.execute(
                                text("INSERT INTO Lots(Lot_ID, Lot_Name, Address, Lot_Type) VALUES (:id, :name, :address, :type)"),
                                {"id": lot_id, 
                                "name": lot_name, 
                                "address": address, 
                                "type": lot_type}
                            )
                            conn.commit()
                        st.session_state.admin_message = f"New lot added: {lot_name} and status set to Active"
                        st.cache_data.clear() 
                        st.rerun()
                
            with delete_lot:
                st.subheader("Delete a Parking Lot", help="Delete a parking lot from the database, this will also delete all associated parking spots and sensors")
                deleted_lot = st.selectbox("Select lot to delete", lot_options)
                if st.button("Delete Lot"):
                    if not st.session_state.authenticated:
                        st.warning("🔒 Login as admin to make changes.")
                    else:
                        with engine.connect() as conn:
                            conn.execute(
                                text("DELETE FROM Lots WHERE Lot_Name = :name"),
                                {"name" : deleted_lot}
                            )
                            conn.commit()
                        st.session_state.admin_message = f"Lot deleted successfully: {deleted_lot}"
                        st.cache_data.clear()
                        st.rerun()

        # ------ SPOTS ------

        with spot_tab:
            st.subheader("Spot Management", help="Manage parking spots within each lot")
            st.write("Use the controls below to update the status of existing parking spots, add new spots, or delete spots from the database. Changes will be reflected in the dashboard after refreshing.")
            active_spot, add_spot, delete_spot, change_spot_type = st.tabs(["Update Spot Status", "Add New Spot", "Delete Spot", "Change Spot Type"])

            with active_spot:
                st.subheader("Update Spot Status", help="Manually set a parking spot to available or occupied")
            # -- UPDATE SPOT STATUS --
                spot_id = st.number_input("Spot ID", min_value=1, step=1, key="spot_id")
                spot_status = st.toggle("Available")
                if st.button("Update Spot Status"):
                    if not st.session_state.authenticated:
                        st.warning("🔒 Login as admin to make changes.")
                    else:
                        with engine.connect() as conn:
                            conn.execute(
                                text("UPDATE Spots SET Status = :status WHERE Spot_ID = :id"),
                                {"status": spot_status, "id": spot_id}

                            )
                            conn.commit()
                        
                        st.session_state.admin_message = f"Updated Spot {spot_id} to {"Available" if spot_status == True else "Occupied"}"
                        st.cache_data.clear()
                        st.rerun()


            with add_spot:
                st.subheader("Add a New Parking Spot", help="Add a new parking spot to the database, new spots will be set to available by default")
            # -- ADD SPOT --
                new_spot_id = st.number_input("Enter Spot ID", min_value=1, step=1, key="new_spot_id")
                spot_lot_ID = st.text_input("Enter Lot ID for New Spot")
                spot_type = st.selectbox("Select Spot Type", ["Regular (None)", "Handicapped", "Staff", "Reserved"])
                spot_level = st.number_input("Enter Level (if spot in a deck)", min_value=0, step=1, key="spot_level")

                spot_type_value = None if spot_type == "Regular (None)" else spot_type

                if st.button("Add Spot"):
                    if not st.session_state.authenticated:
                        st.warning("🔒 Login as admin to make changes.")
                    else:
                        with engine.connect() as conn:
                            conn.execute(
                                text("INSERT INTO Spots(Spot_ID, Lot_ID, Spot_Type, Level, Status) VALUES (:id, :lot_id, :type, :level, TRUE)"),
                                {"id": new_spot_id,
                                "lot_id": spot_lot_ID,
                                "type": spot_type_value,
                                "level": spot_level}
                            )
                            conn.commit()
                        st.session_state.admin_message = f"New spot added: ID {new_spot_id} in Lot {spot_lot_ID} and status set to Available"
                        st.cache_data.clear()
                        st.rerun()

            with delete_spot:
                st.subheader("Delete a Parking Spot", help="Delete a parking spot from the database, this will also delete all associated sensors")        
                # -- DELETE SPOT --
                deleted_spot = st.number_input("Enter Spot ID to Delete", min_value=1, step=1, key="deleted_spot")
                if st.button("Delete Spot"):
                    if not st.session_state.authenticated:
                        st.warning("🔒 Login as admin to make changes.")
                    else:
                        with engine.connect() as conn:
                            conn.execute(
                                text("DELETE FROM Spots WHERE Spot_ID = :id"),
                                {"id" : deleted_spot}
                            )
                            conn.commit()
                        st.session_state.admin_message = f"Spot deleted successfully: {deleted_spot}"
                        st.cache_data.clear()
                        st.rerun()

            # -- CHANGE SPOT TYPE --
            with change_spot_type:
                st.subheader("Change the type of a parking spot (e.g. from regular to reserved)")
                spot_id_type = st.number_input("Enter Spot ID to Update Type", min_value=1, step=1, key="spot_id_type")
                new_spot_type = st.selectbox("Select New Spot Type", ["Regular", "Handicapped", "Staff", "Reserved"])
                new_spot_type_value = None if new_spot_type == "Regular" else new_spot_type

                if st.button("Update Spot Type"):
                    if not st.session_state.authenticated:
                        st.warning("🔒 Login as admin to make changes.")
                    else:
                        with engine.connect() as conn:
                            conn.execute(
                                text("UPDATE Spots SET Spot_Type = :type WHERE Spot_ID = :id"),
                                {"type": new_spot_type_value, "id": spot_id_type}
                            )
                            conn.commit()
                        st.session_state.admin_message = f"Updated Spot {spot_id_type} to {'Regular' if new_spot_type_value is None else new_spot_type_value}"
                        #'Regular' if new_spot_type_value is None else 
                        st.cache_data.clear()
                        st.rerun()
        
        with sensor_tab:
            st.subheader("Sensor Management", help="Manage parking spot sensors")
            st.write("Report a sensor as down, or update its status when fixed")
            
            sensor_id = st.number_input("Enter Spot ID", min_value=1, step=1, key="sensor_id")
            sensor_status = st.toggle("Online")

            if st.button("Update Sensor Status"):
                    if not st.session_state.authenticated:
                        st.warning("🔒 Login as admin to make changes.")
                    else:
                        with engine.connect() as conn:
                            conn.execute(
                                text("UPDATE Sensor_Health SET Is_Online = :status WHERE Sensor_ID = :id"),
                                {"status": spot_status, "id": spot_id}
                            )
                            conn.commit()
                        st.session_state.admin_message = f"Updated Sensor {sensor_id} to {"Online" if sensor_status == True else "Offline"}"
                        st.cache_data.clear()
                        st.rerun()
                    



