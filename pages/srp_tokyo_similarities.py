import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import contextily as cx
from sklearn.preprocessing import StandardScaler

# Set page configuration
st.set_page_config(
    page_title="SRP Tools | Tokyo Similarities",
    page_icon=":school:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.example.com/help",
        "Report a bug": "https://www.example.com/bug",
        "About": "# This is a header. This is an *extremely* cool app!",
    },
)
# Load data
tokyo_stations = pd.read_csv("data/srp_tools/tokyo_stations_with_stats.csv")
similarities_path = "data/srp_tools/cosine_similarity_tokyo.csv"
similarities = pd.read_csv(similarities_path)
similarities.columns = ["org-dest", "Similarity"]
similarities[["org", "dest"]] = similarities["org-dest"].str.split("-", expand=True)
similarities.drop(columns=["org-dest"], inplace=True)
similarities = similarities[["org", "dest", "Similarity"]]

# variables
columns = [
    "circuity_avg",
    "edge_density_km",
    "edge_length_avg",
    "edge_length_total",
    "intersection_count",
    "intersection_density_km",
    "k_avg",
    "m",
    "n",
    "node_density_km",
    "self_loop_proportion",
    "street_density_km",
    "street_length_avg",
    "street_length_total",
    "street_segment_count",
    "streets_per_node_avg",
    "Circuit Index (μ)",
    "Alpha Index",
    "Beta Index",
    "Gamma Index",
    "Road Density (km/km²)",
    "Intersection Density (nodes/km²)",
    "Average Circuitousness (A')",
    "Degree Centrality (Mean)",
    "Degree Centrality (Std Dev)",
    "Closeness Centrality (Mean)",
    "Closeness Centrality (Std Dev)",
    "Betweenness Centrality (Mean)",
    "Betweenness Centrality (Std Dev)",
    "Global Integration (Mean)",
    "Global Integration (Std Dev)",
    "Local Integration (Radius=3, Mean)",
    "Local Integration (Radius=3, Std Dev)",
]
tokyo_stations_std = tokyo_stations.copy()
scaler = StandardScaler()
tokyo_stations_std[columns] = scaler.fit_transform(
    tokyo_stations_std[columns]
)  # 標準化

# functions


def graph_from_df(data):
    wurster_hall = (data["lat"], data["lon"])
    one_mile = 800  # meters

    try:
        G = ox.graph_from_point(wurster_hall, dist=one_mile, network_type="all")
        if G is None:
            return None
        G = ox.project_graph(G, to_crs="EPSG:3857")
        return G
    except nx.NetworkXPointlessConcept as e:
        print(e)
        print(
            f"Graph cannot retrieve for {data['station_cd']}: {data['station_name']} ({data['lat']}, {data['lon']})"
        )
        return None
    except ValueError as e:
        if str(e) == "Graph contains no edges.":
            print(
                f"{data['station_cd']}: {data['station_name']} グラフにエッジがありません。エッジを追加してください。"
            )
            return None


# グラフオブジェクトを受け取り、背景地図とともに描画する
def plot_graph(G, title=""):
    # グラフを描画
    fig, ax = ox.plot_graph(
        G,
        show=False,
        close=False,
        edge_color="gray",
        edge_linewidth=2.0,
        node_size=20,
        node_color="darkblue",
    )
    # 背景地図の追加
    cx.add_basemap(ax, source=cx.providers.OpenStreetMap.Mapnik)
    fig.tight_layout()
    # グラフを表示
    st.pyplot(fig)
    # メモリを解放するためにfigureを閉じる
    plt.close(fig)


# ------------------------------------------------------------------
# 特徴量の寄与度を計算して可視化
def show_feature_contributions(org, dest):
    # 類似度の高いペアのベクトルを取得
    vec1 = (
        tokyo_stations_std[tokyo_stations_std["station_name"] == org]
        .iloc[0][columns]
        .values
    )
    vec2 = (
        tokyo_stations_std[tokyo_stations_std["station_name"] == dest]
        .iloc[0][columns]
        .values
    )
    # 寄与度の計算
    contributions = (vec1 * vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    # 寄与率の可視化
    contribution_df = pd.DataFrame(
        contributions, index=columns, columns=["Contribution"]
    )

    # Matplotlibでグラフを作成
    fig, ax = plt.subplots()
    ax.set_xlim(0, 0.8)  # X軸の範囲を0から0.8に固定
    plt.title("Feature Contributions to Cosine Similarity")
    plt.xlabel("Features")
    plt.ylabel("Contribution")
    plt.grid(axis="y")
    contribution_df.plot(ax=ax, kind="bar", legend=False)
    # StreamlitでMatplotlibのグラフを表示
    st.pyplot(fig)


# Contents of the page
def main():

    # components
    st.title("SRP Tools | Tokyo Similarities Analysis")
    # コサイン類似度の駅一覧
    st.write("駅のコサイン類似度対応表")
    similarities
    st.markdown("----")

    # テキスト入力フィールドを作成
    search_term = st.text_input("検索")
    options = np.unique(tokyo_stations["station_name"].values)
    options = (
        [option for option in options if search_term.lower() in option.lower()]
        if search_term
        else options
    )
    target = st.selectbox(
        "対象駅を選択：",
        options,
    )

    if target:
        st.write("You can show dataframes, charts, and other content.")
        similar_stations = similarities.query(
            f'org == "{target}" | dest == "{target}"'
        ).sort_values(by="Similarity", ascending=False)
        top_10 = similar_stations.head(10)
        bottom_10 = similar_stations.tail(10)
        st.write("Top 10 Similarities")
        st.write(top_10)
        st.write("Bottom 10 Similarities")
        st.write(bottom_10)

        # Show feature contributions
        st.write("Feature Contributions")
        dest = st.selectbox(
            "寄与率を可視化する対象駅を選択：",
            pd.concat([top_10["org"], top_10["dest"]]).unique(),
        )
        if dest:
            show_feature_contributions(target, dest)
            st.markdown(
                """
| 指標 | 説明 | 値が大きいほど... |
|------|------|------|
| n | グラフのノード（交差点）の数 |  |
| m | グラフのエッジ（道路区間）の数 |  |
| k_avg | 平均次数。ノードあたりの平均エッジ数（2m / n） |  |
| edge_length_total | 全エッジの長さの合計 |  |
| edge_length_avg | エッジの平均長さ（edge_length_total / m） |  |
| street_length_total | 全道路の長さの合計（双方向道路は1回だけカウント） |  |
| street_length_avg | 道路の平均長さ |  |
| streets_per_node_avg | ノードあたりの平均道路数 |  |
| streets_per_node_counts | 各ノードの道路数の分布 |  |
| streets_per_node_proportions | 各ノードの道路数の割合 |  |
| intersection_count | 交差点の数 |  |
| circuity_avg | 平均迂回率。エッジの実際の長さと直線距離の比率 |  |
| street_segment_count | 道路区間の数 |  |
| self_loop_proportion | 自己ループの割合 |  |
| node_density_km | 1平方キロメートルあたりのノード密度 |  |
| intersection_density_km | 1平方キロメートルあたりの交差点密度 |  |
| edge_density_km | 1平方キロメートルあたりのエッジ密度 |  |
| street_density_km | 1平方キロメートルあたりの道路密度 |  |
| street_segment_count | 道路セグメントの総数 |  |
| clean_intersection_count | クリーンな交差点（自己ループや並行エッジを除く）の数 |  |
| clean_intersection_density_km | 1平方キロメートルあたりのクリーンな交差点密度 |  |
| **回路指数 (μ)** | 道路網の循環路の数 | 回遊性が高い |
| **α指数** | 実際の循環路数 ÷ 完全連結時の循環路数 | 完全連結型に近い |
| **β指数** | 交差点あたりの平均道路数 | 道路密度が高い |
| **γ指数** | 実際の道路数 ÷ 完全連結時の道路数 | 回遊性が高い |
| **平均最短距離 (Ai)** | ノード間の平均最短距離 | アクセス性が低い |
| **ネットワーク全体の平均最短距離 (Di)** | 全体のアクセス性 | アクセス性が低い |
| **ノードの迂回率 (A')** | 実際の最短距離 ÷ 直線距離 | 迂回が多い |
| **ネットワーク全体の平均迂回率 (A)** | 迂回のしやすさ | 迂回が多い |
----
"""
            )
    target_station = tokyo_stations[tokyo_stations["station_name"] == target].iloc[0]
    dest_station = tokyo_stations[tokyo_stations["station_name"] == dest].iloc[0]
    target_station["駅種別"] = "対象駅"
    dest_station["駅種別"] = "選択した駅"
    df = pd.concat([target_station, dest_station], axis=1).T
    df.reset_index().set_index("駅種別", inplace=True)
    df

    G = graph_from_df(target_station)
    if G is not None:
        st.write(
            f'{target_station["station_name"]} ({target_station["lat"]}, {target_station["lon"]})'
        )
        plot_graph(
            G,
            f'{target_station["station_name"]} ({target_station["lat"]}, {target_station["lon"]})',
        )
    G = graph_from_df(dest_station)
    if G is not None:
        st.write(
            f'{dest_station["station_name"]} ({dest_station["lat"]}, {dest_station["lon"]})'
        )
        plot_graph(
            G,
            f'{dest_station["station_name"]} ({dest_station["lat"]}, {dest_station["lon"]})',
        )


if __name__ == "__main__":
    main()
