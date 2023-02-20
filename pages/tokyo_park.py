import streamlit as st
import pandas as pd
import json
import folium
from streamlit_folium import st_folium


def main():
    st.title('東京都の公園')
    
    
    display_parks = pd.read_csv("data/parks.csv")
    display_parks
    
    
    # center on Liberty Bell, add marker
    m = folium.Map(location=[35.6809591, 139.7673068], zoom_start=12, control_scale=True)
    feature_group = folium.FeatureGroup("Locations")
    for idx, park in display_parks.iterrows():
        lonlat = park['Coordinates'].split(',')
        latlon = [lonlat[1], lonlat[0]]
    
        message = f"【公園名】：{park['Name']}<br><br>"
        if str(park['Description']) != 'nan':
            message += f"【説明】：{park['Description']}<br><br>"
        message += f"【住所】：{park['Address']}<br><br>"
        message += f"【ジャンル】：{park['Genre']}"
        iframe = folium.IFrame(message)
        popup = folium.Popup(iframe, min_width=300, max_width=300)
        feature_group.add_child(folium.Marker(
            latlon, tooltip=park['Name'], popup=popup
        ))
    
    m.add_child(feature_group)
    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725, returned_objects=[])

if __name__ == '__main__':
    main()