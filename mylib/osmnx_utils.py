import networkx as nx
import osmnx as ox
import contextily as cx
import matplotlib.pyplot as plt

from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="geocoding-example")

import streamlit as st

def graph_from_place(address: str):
    location = geolocator.geocode(address)
    latlon = (location.latitude, location.longitude)
    dist = 800 #meters

    try:
        G = ox.graph_from_point(latlon, dist=dist, network_type='all')
        if G is None:
            return None
        G = ox.project_graph(G, to_crs='EPSG:3857')
        return G
    except nx.NetworkXPointlessConcept as e:
        print(e)
        print(f"Graph cannot retrieve for {address} ({latlon[0]}, {latlon[1]})")
        return None
    except ValueError as e:
        if str(e) == "Graph contains no edges.":
            print(f"グラフにエッジがありません。エッジを追加してください。")
            return None

# グラフオブジェクトを受け取り、背景地図とともに描画する
def plot_graph(G, title=''):
    # グラフを描画
    fig, ax = ox.plot_graph(G, show=False, close=False, edge_color='gray', edge_linewidth=2.0, node_size=20, node_color='darkblue')
    # 背景地図の追加
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)
    fig.tight_layout()
    # グラフを表示
    st.pyplot(fig)
    # メモリを解放するためにfigureを閉じる
    plt.close(fig)