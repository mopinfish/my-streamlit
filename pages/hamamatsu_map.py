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
import requests
import json

def get_fiware_data():
    authorization= os.getenv("FIWARE_AUTHORIZATION")
    headers = {
      'Fiware-Service': 'make_our_city_data',
      'Fiware-ServicePath': '/',
      'Authorization': authorization,
    }
    orion_endpoint = os.getenv("FIWARE_ORION_ENDPOINT")
    path = "/v2/entities?\options=keyValues&limit=100&type=Room"
    response = requests.get(orion_endpoint + path, headers=headers)
    ret = response.json()
    print(ret)
    return ret

def to_geometry(row):

    row['Coordinates'] = str(row['Geometry']['Coordinates'])
    return row

def main():
    st.title('浜松市マップ')
    
    appid = os.environ["YAHOO_CLIENT_ID"]
    ac = 22131
    gc = '0301'
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

    st.markdown("## スポーツ施設一覧")
    points

    evacuations = pd.read_csv("data/evacuation.csv")
    st.markdown("## 避難所一覧")
    evacuations
    
    ret = get_fiware_data()
    temperature_value = ret[-1]['temperature']['value']
    humidity_value = ret[-1]['humidity']['value']

    # center on Liberty Bell, add marker
    st.markdown("## マップ")
    m = folium.Map(location=[34.70572632560328, 137.73013034232767], zoom_start=15, control_scale=True)
    feature_group = folium.FeatureGroup("Locations")
    for idx, point in points.iterrows():
        lonlat = point['Coordinates'].split(',')
        latlon = [lonlat[1], lonlat[0]]
    
        message = f"【施設名】：{point['Name']}<br>"
        message += f"【住所】：{point['Property']['Address']}<br>"
        if str(point['Description']) != '':
            message += f"【説明】：{point['Description']}<br>"
        message += f"【ジャンル】：{point['Property']['Genre'][0]['Name']}<br>"
        message += f"【現在の気温】：{temperature_value}度<br>"
        message += f"【現在の湿度】：{humidity_value}％<br>"
        iframe = folium.IFrame(message)
        popup = folium.Popup(iframe, min_width=300, max_width=300)
        feature_group.add_child(folium.Marker(
            latlon, tooltip=point['Name'], popup=popup
        ))

    for idx, point in evacuations.iterrows():
        latlon = [point['緯度'], point['経度']]
    
        message = f"【避難所名称】：{point['避難所名称']}<br>"
        message += f"【住所】：{point['所在地']}<br>"
        #if str(point['Description']) != '':
        #    message += f"【説明】：{point['Description']}<br>"
        message += f"【収容可能人員（屋内）】：{point['収容可能人員（屋内）']}人<br>"
        #message += f"【現在の気温】：{temperature_value}度<br>"
        #message += f"【現在の湿度】：{humidity_value}％<br>"
        iframe = folium.IFrame(message)
        popup = folium.Popup(iframe, min_width=300, max_width=300)
        feature_group.add_child(folium.Marker(
            latlon, tooltip=point['避難所名称'], popup=popup, icon = folium.Icon(color="red")
        ))
    
    m.add_child(feature_group)
    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725, returned_objects=[])

if __name__ == '__main__':
    main()