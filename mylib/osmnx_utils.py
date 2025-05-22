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
    dist = 800  # meters

    try:
        G = ox.graph_from_point(
            latlon, dist=dist, network_type="drive", simplify=True, retain_all=True
        )
        if G is None:
            return None
        G = ox.project_graph(G, to_crs="EPSG:3857")
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
def plot_graph(G, title="", context=True):
    # グラフを描画
    fig, ax = ox.plot_graph(
        G,
        show=False,
        close=False,
        edge_color="gray",
        edge_linewidth=2.0,
        node_size=30,
        node_color="blue",
        bgcolor="w",
    )

    # 背景地図の追加
    if context:
        cx.add_basemap(
            ax,
            source=cx.providers.OpenStreetMap.Mapnik,
            zoom=15,
            crs=G.graph["crs"],
            attribution="Map data © OpenStreetMap contributors",
            alpha=0.8,
        )

    fig.tight_layout()

    # グラフを表示
    st.pyplot(fig)

    # メモリを解放するためにfigureを閉じる
    plt.close(fig)
