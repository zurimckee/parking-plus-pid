# 🛍️ Parking+ Python Dashboard 


<img width="1912" height="859" alt="image" src="https://github.com/user-attachments/assets/af57828f-ed91-4cf6-aca2-a2e1eb87d9a9" />

A real-time parking management dashboard built with **Streamlit** and **MySQL**, designed to give parking administrators a live view of lot occupancy, sensor health, and historical trends — with full CRUD controls from the sidebar.

## Features 
**Live Occupancy Overview**
- Total spaces, available spaces, and occupancy rate displayed as top-level metrics
- Alerts when lots exceed 80% capacity
- Auto-refreshes every 60 seconds (manual refresh also available)

**Lot-Level Occupancy**
- Stacked bar chart showing available vs. occupied spaces per lot
- Near-capacity warnings with a filterable summary table

**Spot Type Breakdown**
- Grouped bar chart visualizing Regular, Handicapped, Staff, and Reserved spots across all lots
- Warnings when reserved spot ratios may limit general availability

**Occupancy Trends**
- Busiest hour metric derived from the past 7 days of activity
- Hourly line chart: today's arrivals and departures by hour
- Daily line chart: this week's activity day-by-day

**Admin Control Panel (Sidebar)**
- **Lots** — activate/deactivate lots, add new lots, delete lots
- **Spots** — update spot status, add/delete spots, change spot type (Regular, Handicapped, Staff, Reserved)
- **Sensors** — mark sensors online or offline

All admin actions write directly to the database and trigger an automatic cache clear and page refresh.

## Tech Stack
- Frontend = Streamlit
- Database = MySQL (SqlAlchemy) hosted on Railway
- Charting = Plotly Express
- Data Visualization = Pandas
- Deployment = Railway

## Contact

- **Bug reports:** [zurimckee95@gmail.com](mailto:zurimckee95@gmail.com)
- **Help / live app:** [smartparkplus.vercel.app](https://smartparkplus.vercel.app/)

   
