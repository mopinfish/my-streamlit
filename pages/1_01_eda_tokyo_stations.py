import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from mylib import osmnx_utils as oxu

# フォントファイルのパスを取得（Noto Sans CJK の例）
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_prop = fm.FontProperties(fname=font_path)

# 以降のグラフでデフォルトに設定
plt.rcParams["font.family"] = font_prop.get_name()
# Set page configuration
st.set_page_config(
    page_title="SRP Tools | 1.1 EDA Tokyo Stations",
    page_icon=":school:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

# 2 1 3 4 7 11 18 29 47


# CSVファイルの読み込み（ローカル or URLに応じて変更）
@st.cache_data
def load_data():
    return pd.read_csv("srp-data/01_stations_with_metrics.csv")


df = load_data()

# 街路構造に関する指標リスト
# street_structure_columns = [
#'circuity_avg', 'edge_density_km', 'edge_length_avg', 'edge_length_total',
#'intersection_count', 'intersection_density_km', 'k_avg', 'm', 'n',
#'node_density_km', 'self_loop_proportion', 'street_density_km',
#'street_length_avg', 'street_length_total', 'street_segment_count',
#'streets_per_node_avg', 'Circuit Index (μ)', 'Alpha Index', 'Beta Index',
#'Gamma Index', 'Road Density (km/km²)', 'Intersection Density (nodes/km²)',
# "Average Circuitousness (A')", 'Degree Centrality (Mean)', 'Degree Centrality (Std Dev)',
#'Closeness Centrality (Mean)', 'Closeness Centrality (Std Dev)',
#'Betweenness Centrality (Mean)', 'Betweenness Centrality (Std Dev)',
#'Global Integration (Mean)', 'Global Integration (Std Dev)',
#'Local Integration (Radius=3, Mean)', 'Local Integration (Radius=3, Std Dev)'
# ]
street_structure_columns = [
'n_nodes', 'e_edges', 'p_components', 'circuit_index_mu',
       'mean_circuit_index_mu_a', 'alpha_index', 'beta_index', 'gamma_index',
       'avg_shortest_path_Di', 'total_edge_length_L',
       'road_density_Dl_m_per_ha', 'intersection_count_deg≥3',
       'intersection_density_Dc_per_ha', 'avg_circuity_A', 'area_m2',
       'degree_centrality_mean', 'degree_centrality_std',
       'closeness_centrality_mean', 'closeness_centrality_std',
       'betweenness_centrality_mean', 'betweenness_centrality_std',
       'integration_global_mean', 'integration_global_std',
       'integration_local_r3_mean', 'integration_local_r3_std', 'basic_n',
       'basic_m', 'basic_k_avg', 'basic_edge_length_total',
       'basic_edge_length_avg', 'basic_streets_per_node_avg',
       'basic_streets_per_node_counts', 'basic_streets_per_node_proportions',
       'basic_intersection_count', 'basic_street_length_total',
       'basic_street_segment_count', 'basic_street_length_avg',
       'basic_circuity_avg', 'basic_self_loop_proportion',
       'basic_clean_intersection_count', 'basic_node_density_km',
       'basic_intersection_density_km', 'basic_edge_density_km',
       'basic_street_density_km', 'basic_clean_intersection_density_km'
]

# UI: 指標選択
st.title("駅の街路構造分析")
st.markdown("## 駅の街路構造指標によるソート")
selected_feature = st.selectbox(
    "ソートする指標を選択してください", street_structure_columns
)

# UI: 昇順 or 降順
ascending = st.radio("並び順", ["昇順", "降順"]) == "昇順"

# ソート処理
sorted_df = df.sort_values(by=selected_feature, ascending=ascending).drop_duplicates(
    subset=["station_name"], keep="first"
)

# 表示カラムを選択
# display_columns = ['station_name', 'Circuit Index (μ)', 'Alpha Index', 'Beta Index', 'Gamma Index']
display_columns = ["station_name", selected_feature]

# 表示
st.subheader(f"{selected_feature} による駅のソート")
st.dataframe(
    sorted_df[display_columns].reset_index(drop=True), use_container_width=True
)

# 分布グラフの表示
st.subheader(f"【分布】{selected_feature} のヒストグラム")

fig, ax = plt.subplots(figsize=(8, 4))
ax.hist(df[selected_feature].dropna(), bins=20, color="skyblue", edgecolor="black")
ax.set_xlabel(selected_feature)
ax.set_ylabel("駅数")
ax.set_title(f"{selected_feature} の分布")
st.pyplot(fig)

# 上位10駅のグラフ表示
for s in sorted_df.head(10).itertuples():
    st.write(f"駅名: {s.station_name}, 緯度: {s.lat}, 経度: {s.lon}")
    G = oxu.graph_from_place(s.station_name)
    if G is not None:
        oxu.plot_graph(G, f"{s.station_name} ({s.lat}, {s.lon})")
