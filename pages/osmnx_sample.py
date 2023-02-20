import streamlit as st
import networkx as nx
import osmnx as ox
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geocoding-example")

st.title('道路ネットワークの検索')

address = st.text_input("表示したい場所を入力してください") # 引数に入力内容を渡せる
network_type = st.selectbox("network_type", ("all_private", "all", "bike", "drive", "drive_service", "walk")) #第一引数：リスト名、第二引数：選択肢、複数選択可
if st.button("検索", key=0):
    location = geolocator.geocode(address)
    st.write("Lat, Long = ",location.latitude, location.longitude)
    st.write("full address = ", location.address)
    latlon = (location.latitude, location.longitude)
    one_mile = 1609  # meters
    G = ox.graph_from_point(latlon, dist=one_mile, network_type=network_type)
    # download/model a street network for some city then visualize it
    fig, ax = ox.plot_graph(G)
    # Matplotlib の Figure を指定して可視化する
    st.pyplot(fig)

    # what sized area does our network cover in square meters?
    G_proj = ox.project_graph(G)
    nodes_proj = ox.graph_to_gdfs(G_proj, edges=False)
    graph_area_m = nodes_proj.unary_union.convex_hull.area
    st.write("graph area m = ", graph_area_m)
    # show some basic stats about the network
    basic_stats = ox.basic_stats(G_proj, area=graph_area_m, clean_int_tol=15)
    st.write("basic stats = ", basic_stats)