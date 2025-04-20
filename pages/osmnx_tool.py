import streamlit as st
import osmnx as ox

ox.config(use_cache=True, log_console=True)
from geopy.geocoders import Nominatim
import folium
from folium import plugins
from streamlit_folium import st_folium

geolocator = Nominatim(user_agent="geocoding-example")

st.title("OSMnx Tool")

address = st.text_input("表示したい場所を入力してください")  # 引数に入力内容を渡せる
network_type = st.selectbox(
    "network_type", ("all_private", "all", "bike", "drive", "drive_service", "walk")
)  # 第一引数：リスト名、第二引数：選択肢、複数選択可

if st.button("境界を取得", key=0):
    city = ox.geocode_to_gdf(address)
    city_proj = ox.project_gdf(city)
    ax = city_proj.plot(fc="gray", ec="none")
    _ = ax.axis("off")
    # Matplotlib の Figure を指定して可視化する
    st.pyplot(ax.figure)

if st.button("検索", key=1):
    location = geolocator.geocode(address)
    st.write("Lat, Long = ", location.latitude, location.longitude)
    st.write("full address = ", location.address)
    latlon = (location.latitude, location.longitude)
    one_mile = 1609  # meters
    G = ox.graph_from_point(latlon, dist=one_mile, network_type=network_type)
    # 元のグラフのエッジを線グラフの近さ中心性で色付けする
    fig, ax = ox.plot_graph(
        G, bgcolor="k", node_size=0, edge_linewidth=0.5, edge_alpha=1
    )
    # Matplotlib の Figure を指定して可視化する
    st.pyplot(fig)

    # center on Liberty Bell, add marker
    m = folium.Map(
        location=[location.latitude, location.longitude],
        zoom_start=15,
        control_scale=True,
    )
    iframe = folium.IFrame(location.address)
    popup = folium.Popup(iframe, min_width=300, max_width=300)
    folium.Marker([location.latitude, location.longitude], popup=popup).add_to(m)
    # 地図に画像を追加
    url = "https://cdn-ak.f.st-hatena.com/images/fotolife/c/chayarokurokuro/20210807/20210807120306.png"
    plugins.FloatImage(
        url,
        bottom=45,  # 数値を上げると上がる  ベストは bottom=65
        left=65,  # 数値を上げると右に移動  ベストは left=82
    ).add_to(m)

    # call to render Folium map in Streamlit
    st_data = st_folium(m, width=725, returned_objects=[])

    # what sized area does our network cover in square meters?
    G_proj = ox.project_graph(G)
    nodes_proj = ox.graph_to_gdfs(G_proj, edges=False)
    graph_area_m = nodes_proj.unary_union.convex_hull.area
    st.write("graph area m = ", graph_area_m)
    # show some basic stats about the network
    basic_stats = ox.basic_stats(G_proj, area=graph_area_m, clean_int_tol=15)
    st.write("basic stats = ", basic_stats)
