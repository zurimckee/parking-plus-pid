# parkingplus python dashboard 


[![parkingplus dash img/link]("https://github.com/user-attachments/assets/af57828f-ed91-4cf6-aca2-a2e1eb87d9a9")](https://aggiebot.streamlit.app/)


### overview
a real-time parking management dashboard built with **streamlit** and **mysql**, designed to give parking administrators a live view of lot occupancy, sensor health, and historical trends — with full crud controls from the sidebar.

### features 
- displays total, available, and occupied spaces with 80% capacity alerts and automatic 60s refresh (with manual override).
- visualizes per-lot availability using stacked bar charts with near-capacity warnings and a filterable summary table.
– shows distribution of regular, handicapped, staff, and reserved spots across lots with alerts on restrictive reserved ratios.
- provides analytics including busiest hour (7-day window) and hourly/daily charts for arrival and departure patterns.
- enables full crud operations for lots, spots, and sensors with real-time database updates, cache invalidation, and automatic UI refresh within admin sidebar, and no coding necessary.
- admin sidebar password authentication for database security 

### tech stack
front-end
- [X] streamlit
- [X] plotly
- [X] pandas

back-end
- [X] mysql/sqlalchemy
- [X] railway (hosting)


   
