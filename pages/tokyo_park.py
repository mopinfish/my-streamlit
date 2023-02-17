import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium



st.title('東京都の公園')

display_parks = pd.read_csv("data/parks.csv")
display_parks


# center on Liberty Bell, add marker
m = folium.Map(location=[35.6809591, 139.7673068], zoom_start=12)
feature_group = folium.FeatureGroup("Locations")
for idx, park in display_parks.iterrows():
    lonlat = park['Coordinates'].split(',')
    latlon = [lonlat[1], lonlat[0]]

    iframe = folium.IFrame(f"""
        【公園名】：{park['Name']}<br><br>
        【説明】：{park['Description']}<br><br>
        【住所】：{park['Address']}<br><br>
        【ジャンル】：{park['Genre']}
        """
    )
    popup = folium.Popup(iframe, min_width=300, max_width=300)
    feature_group.add_child(folium.Marker(
        latlon, tooltip=park['Name'], popup=popup
    ))

m.add_child(feature_group)
# call to render Folium map in Streamlit
st_data = st_folium(m, width=725)