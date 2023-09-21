import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import sys, os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(str(Path(__file__).resolve().parent.parent))
from lib import YolpSearch

def to_geometry(row):

    row['Coordinates'] = str(row['Geometry']['Coordinates'])
    return row

def main():
    st.title('浜松市マップ')
    
    appid = os.environ["YAHOO_CLIENT_ID"]
    ac = 22
    gc = '0301006'
    start = 0
    yolp = YolpSearch(appid)
    result = yolp.search(ac, gc, start)
    features = result['Feature']
    total = result['ResultInfo']['Total']

    print(total)
    print(type(features))
    while start + 100 < total:
        start += 100
        print(f"start is {start}")
        result = yolp.search(ac, gc, start)
        features.extend(result['Feature'])
    print(len(features))

    points = pd.DataFrame(features).sort_values('Id')
    points = points.apply(to_geometry, axis=1)

    points
    
    # center on Liberty Bell, add marker
    m = folium.Map(location=[34.70438265742628, 137.73444823876622], zoom_start=12, control_scale=True)
    feature_group = folium.FeatureGroup("Locations")
    for idx, point in points.iterrows():
        lonlat = point['Coordinates'].split(',')
        latlon = [lonlat[1], lonlat[0]]
    
        message = f"【施設名】：{point['Name']}<br><br>"
        if str(point['Description']) != 'nan':
            message += f"【説明】：{point['Description']}<br><br>"
        message += f"【住所】：{point['Property']['Address']}<br><br>"
        message += f"【ジャンル】：{point['Property']['Genre']}"
        iframe = folium.IFrame(message)
        popup = folium.Popup(iframe, min_width=300, max_width=300)
        feature_group.add_child(folium.Marker(
            latlon, tooltip=point['Name'], popup=popup
        ))
    
    m.add_child(feature_group)
    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725, returned_objects=[])

if __name__ == '__main__':
    main()