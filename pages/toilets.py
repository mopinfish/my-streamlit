import streamlit as st
import osmnx as ox
ox.config(use_cache=True, log_console=True)
from geopy.geocoders import Nominatim
import folium
from folium import plugins
from streamlit_folium import st_folium

geolocator = Nominatim(user_agent="geocoding-example")

st.title('OSMnx Tool')

address = st.text_input("場所を入力してください") # 引数に入力内容を渡せる

if st.button("検索", key=1):
    location = geolocator.geocode(address)
    st.write("Lat, Long = ",location.latitude, location.longitude)
    st.write("full address = ", location.address)
    latlon = (location.latitude, location.longitude)
    one_mile = 1609  # meters
    features = ox.features_from_point(latlon, tags={'amenity': True}, dist=one_mile).reset_index()
    toilets = features[(features['element_type'] == 'node') & (features['amenity'] == 'toilets')]

    # center on Liberty Bell, add marker
    m = folium.Map(location=[location.latitude, location.longitude], zoom_start=15, control_scale=True)
    iframe = folium.IFrame(location.address)
    popup = folium.Popup(iframe, min_width=300, max_width=300)
    # 読み込んだデータ(緯度・経度、ポップアップ用文字、アイコンを表示)
    for i, row in toilets.iterrows():
        # ポップアップの作成
        lat = row['geometry'].y
        lon = row['geometry'].x
        pop = f'<a href="https://www.google.com/maps/dir/{lat},{lon}" target="_blank">Google Mapで見る</a>'
        folium.Marker(
            # 緯度と経度を指定
            location=[row['geometry'].y, row['geometry'].x],
            # ポップアップの指定
            popup=folium.Popup(pop, max_width=300),
            # アイコンの指定(アイコン、色)
            icon=folium.Icon(icon="home",icon_color="white", color="red")
    ).add_to(m)
    folium.Marker([location.latitude, location.longitude], popup=popup).add_to(m)
    # 地図に画像を追加
    url = "https://cdn-ak.f.st-hatena.com/images/fotolife/c/chayarokurokuro/20210807/20210807120306.png"
    plugins.FloatImage(
        url, 
        bottom=45, # 数値を上げると上がる  ベストは bottom=65
        left=65,  # 数値を上げると右に移動  ベストは left=82
    ).add_to(m)

    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725, returned_objects=[])