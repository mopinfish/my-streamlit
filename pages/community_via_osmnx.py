import streamlit as st
import numpy as np
import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt
import contextily as cx
from community import community_louvain
import geopandas as gpd
ox.config(use_cache=True, log_console=True)
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geocoding-example")

st.title('OSMnxを使ったコミュニティの可視化')

address = st.text_input("表示したい場所を入力してください") # 引数に入力内容を渡せる
network_type = st.selectbox("network_type", ("all_private", "all", "bike", "drive", "drive_service", "walk")) #第一引数：リスト名、第二引数：選択肢、複数選択可
miles = st.selectbox("半径距離（マイル）", (0.5, 1, 2, 4)) #第一引数：リスト名、第二引数：選択肢、複数選択可

if st.button("表示", key=1):
    location = geolocator.geocode(address)
    latlon = (location.latitude, location.longitude)
    one_mile = 1609  # meters

    st.write("緯度経度：",location.latitude, location.longitude)
    st.write("住所：", location.address)
    st.write("表示する半径（m）：", miles * one_mile)

    G = ox.graph_from_point(latlon, dist=miles * one_mile, network_type=network_type)

    # グラフを無向グラフに変換
    G_undirected = G.to_undirected()

    # Fast Unfolding法によるコミュニティ抽出
    communities = community_louvain.best_partition(G_undirected)

    # コミュニティ情報をノードの属性として追加
    nx.set_node_attributes(G, communities, "community")

    # エッジにコミュニティ情報を追加
    for u, v, data in G.edges(data=True):
        data['community'] = communities[u]

    # グラフをGeoDataFrameに変換
    nodes, edges = ox.graph_to_gdfs(G)

    # コミュニティごとに色を割り当て
    unique_communities = set(communities.values())
    colors = plt.cm.rainbow(np.linspace(0, 1, len(unique_communities)))
    color_dict = dict(zip(unique_communities, colors))

    # エッジに色を割り当て
    edges['color'] = edges['community'].map(lambda x: color_dict[x])

    # 地図の作成
    fig, ax = plt.subplots(figsize=(30, 30))

    # エッジの描画
    edges.plot(ax=ax, column='community', cmap='rainbow', linewidth=2, alpha=0.7)

    # 背景地図の追加
    cx.add_basemap(ax, crs=edges.crs.to_string(), source=cx.providers.OpenStreetMap.Mapnik)

    # 地図のスタイル調整
    ax.set_axis_off()
    st.pyplot(ax.figure)