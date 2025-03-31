import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mylib import osmnx_utils as oxu

# Set page configuration
st.set_page_config(
    page_title="SRP Tools | 1.1 EDA Tokyo Stations",
    page_icon=":school:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)
# CSVファイルの読み込み（ローカル or URLに応じて変更）
@st.cache_data
def load_data():
    return pd.read_csv("data/srp_tools/tokyo_stations_with_stats.csv")

df = load_data()

# 街路構造に関する指標リスト
#street_structure_columns = [
    #'circuity_avg', 'edge_density_km', 'edge_length_avg', 'edge_length_total',
    #'intersection_count', 'intersection_density_km', 'k_avg', 'm', 'n',
    #'node_density_km', 'self_loop_proportion', 'street_density_km',
    #'street_length_avg', 'street_length_total', 'street_segment_count',
    #'streets_per_node_avg', 'Circuit Index (μ)', 'Alpha Index', 'Beta Index',
    #'Gamma Index', 'Road Density (km/km²)', 'Intersection Density (nodes/km²)',
    #"Average Circuitousness (A')", 'Degree Centrality (Mean)', 'Degree Centrality (Std Dev)',
    #'Closeness Centrality (Mean)', 'Closeness Centrality (Std Dev)',
    #'Betweenness Centrality (Mean)', 'Betweenness Centrality (Std Dev)',
    #'Global Integration (Mean)', 'Global Integration (Std Dev)',
    #'Local Integration (Radius=3, Mean)', 'Local Integration (Radius=3, Std Dev)'
#]
street_structure_columns = ['Circuit Index (μ)', 'Alpha Index', 'Beta Index', 'Gamma Index']

# UI: 指標選択
st.title("駅の街路構造分析")
st.markdown("## 駅の街路構造指標によるソート")
selected_feature = st.selectbox("ソートする指標を選択してください", street_structure_columns)

# UI: 昇順 or 降順
ascending = st.radio("並び順", ["昇順", "降順"]) == "昇順"

# ソート処理
sorted_df = df.sort_values(by=selected_feature, ascending=ascending).drop_duplicates(subset=['station_name'], keep='first')

# 表示カラムを選択
display_columns = ['station_name', 'Circuit Index (μ)', 'Alpha Index', 'Beta Index', 'Gamma Index']

# 表示
st.subheader(f"{selected_feature} による駅のソート")
st.dataframe(sorted_df[display_columns].reset_index(drop=True), use_container_width=True)

# 分布グラフの表示
st.subheader(f"【分布】{selected_feature} のヒストグラム")

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(df[selected_feature].dropna(), bins=20, color='skyblue', edgecolor='black')
ax.set_xlabel(selected_feature)
ax.set_ylabel("駅数")
ax.set_title(f"{selected_feature} の分布")
st.pyplot(fig)

# 一つ目の駅
first_station = sorted_df.iloc[0]
# 二つ目の駅
second_station = sorted_df.iloc[1]

G1 = oxu.graph_from_place(first_station['station_name'])
if G1 is not None:
    oxu.plot_graph(G1, f'{first_station["station_name"]} ({first_station["lat"]}, {first_station["lon"]})')
G2 = oxu.graph_from_place(second_station['station_name'])
if G2 is not None:
    oxu.plot_graph(G2, f'{second_station["station_name"]} ({second_station["lat"]}, {second_station["lon"]})')