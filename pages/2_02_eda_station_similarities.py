import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from math import pi
from sklearn.preprocessing import StandardScaler
# フォントファイルのパスを取得（Noto Sans CJK の例）
font_path = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
font_prop = fm.FontProperties(fname=font_path)

# 以降のグラフでデフォルトに設定
plt.rcParams["font.family"] = font_prop.get_name()

# ページ設定
st.set_page_config(page_title="複数駅類似度 + 指標分析", layout="wide")
st.title("🚉 複数駅の類似度 & 指標分析ツール（Zスコア標準化＋カテゴリ別比較）")

# データパス
SIM_PATH = "srp-data/02_tokyo_stations_with_similarities_by_selected_metrics.csv"
INFO_PATH = "srp-data/01_stations_with_metrics.csv"

# 指標カテゴリ定義
metric_categories = {
    "回遊性": [
        "circuit_index_mu",
        "mean_circuit_index_mu_a",
        "alpha_index",
        "beta_index",
        "gamma_index",
    ],
    "アクセス性": [
        "avg_shortest_path_Di",
        "closeness_centrality_mean",
        "integration_global_mean",
        "integration_local_r3_mean",
        "basic_node_density_km",
    ],
    "迂回性": ["avg_circuity_A", "basic_circuity_avg"],
    "交差点密度": [
        "intersection_density_Dc_per_ha",
        "basic_intersection_density_km",
        "basic_clean_intersection_density_km",
    ],
    "中心性": [
        "degree_centrality_mean",
        "betweenness_centrality_mean",
        "closeness_centrality_mean",
        "integration_global_mean",
        "integration_local_r3_mean",
    ],
    "街路スケール": [
        "basic_street_length_avg",
        "basic_edge_density_km",
        "total_edge_length_L",
        "road_density_Dl_m_per_ha",
        "basic_street_density_km",
    ],
}
selected_metrics = list(set(sum(metric_categories.values(), [])))

@st.cache_data
def load_and_standardize_info(path, selected_metrics):
    df = pd.read_csv(path, dtype={"station_cd": str})
    df["station_label"] = df["station_name"] + "（" + df["address"] + "）"
    df_unique = df.drop_duplicates(subset=["station_label"])

    # 東京都のデータのみをZスコア化対象とする
    df_tokyo = df_unique[df_unique["pref_cd"] == 13].copy()

    def is_convertible(series):
        try:
            pd.to_numeric(series.dropna().iloc[0])
            return True
        except:
            return False

    valid_metrics = [col for col in selected_metrics if col in df_tokyo.columns and is_convertible(df_tokyo[col])]
    df_metrics_tokyo = df_tokyo[valid_metrics].copy()

    # Zスコア標準化（東京都の駅に対してのみ）
    scaler = StandardScaler()
    df_scaled_tokyo = pd.DataFrame(scaler.fit_transform(df_metrics_tokyo), columns=valid_metrics)
    df_scaled_tokyo["station_cd"] = df_tokyo["station_cd"].values
    df_scaled_tokyo["station_label"] = df_tokyo["station_label"].values

    # 出力用データ：Zスコア化データ（東京都のみ）をindex付きで返す
    df_scaled_tokyo.set_index("station_label", inplace=True)
    return df_unique, df_scaled_tokyo, valid_metrics


# 類似度データ読み込み
df_sim_raw = pd.read_csv(
    SIM_PATH, dtype={"station_cd_source": str, "station_cd_target": str}
)
df_info_raw, df_info_zscore, valid_metrics = load_and_standardize_info(
    INFO_PATH, selected_metrics
)

# 駅ラベルマップ
station_label_map = df_info_raw.set_index("station_cd")["station_label"].to_dict()
df_sim_raw["source_label"] = df_sim_raw["station_cd_source"].map(station_label_map)
df_sim_raw["target_label"] = df_sim_raw["station_cd_target"].map(station_label_map)
df_sim = df_sim_raw.dropna(subset=["source_label", "target_label"]).drop_duplicates(
    subset=["source_label", "target_label"]
)

# 駅選択（複数可）
available_labels = sorted(df_sim["source_label"].unique())
selected_station_labels = st.multiselect(
    "基準駅を選択してください（複数選択可）", available_labels
)

if not selected_station_labels:
    st.stop()

selected_station_cds = df_info_raw[
    df_info_raw["station_label"].isin(selected_station_labels)
]["station_cd"].tolist()

# 類似駅抽出（全選択駅に対して）
similar_stations_all = df_sim[
    df_sim["station_cd_source"].isin(selected_station_cds)
].sort_values(by="cosine_similarity", ascending=False)

# 類似駅から基準駅以外を抽出し、top_n件ずつ取得（重複除去）
top_n = st.slider("基準駅ごとの類似駅数", min_value=3, max_value=20, value=10)
similar_targets = (
    similar_stations_all.groupby("station_cd_source")
    .head(top_n)["target_label"]
    .tolist()
)
target_labels = list(set(selected_station_labels + similar_targets))
df_compare_scaled = df_info_zscore.loc[df_info_zscore.index.isin(target_labels)]

# 類似駅リスト表示
st.subheader("🔍 類似駅リスト")
df_display = similar_stations_all[
    similar_stations_all["station_cd_source"].isin(selected_station_cds)
].copy()
df_display = df_display[df_display["target_label"].isin(similar_targets)]
df_display["cosine_similarity"] = df_display["cosine_similarity"].map(
    lambda x: f"{x:.4f}"
)
df_display = df_display.rename(
    columns={
        "source_label": "基準駅",
        "target_label": "類似駅",
        "cosine_similarity": "コサイン類似度",
    }
)
st.dataframe(df_display[["基準駅", "類似駅", "コサイン類似度"]])

# 全体レーダーチャート
st.subheader("📊 全指標のレーダーチャート（Zスコア）")
if len(df_compare_scaled) > 1:
    N = len(valid_metrics)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    for name, row in df_compare_scaled[valid_metrics].iterrows():
        values = row.tolist() + [row.tolist()[0]]
        ax.plot(angles, values, label=name)
        ax.fill(angles, values, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(valid_metrics, fontsize=8)
    ax.set_title("全指標を対象とした比較", y=1.1)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1))
    st.pyplot(fig)

# カテゴリ別比較
st.subheader("📚 カテゴリ別プロファイル比較")
tabs = st.tabs(metric_categories.keys())

for category, tab in zip(metric_categories.keys(), tabs):
    with tab:
        st.markdown(f"### 📌 カテゴリ：{category}")
        metrics = [
            m for m in metric_categories[category] if m in df_compare_scaled.columns
        ]

        if not metrics:
            st.warning("このカテゴリに有効な指標が見つかりません。")
            continue

        df_subset = df_compare_scaled[metrics]

        # ヒートマップ
        st.markdown("#### 🔥 ヒートマップ")
        fig_h, ax = plt.subplots(figsize=(10, 4))
        sns.heatmap(df_subset, annot=True, cmap="YlGnBu", ax=ax)
        st.pyplot(fig_h)

        # レーダーチャート
        st.markdown("#### 🧭 レーダーチャート")
        angles = [n / float(len(metrics)) * 2 * pi for n in range(len(metrics))]
        angles += angles[:1]

        fig_r, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        for name in df_subset.index:
            values = df_subset.loc[name].tolist() + [df_subset.loc[name].tolist()[0]]
            ax.plot(angles, values, label=name)
            ax.fill(angles, values, alpha=0.1)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics, fontsize=9)
        ax.set_title(f"{category}カテゴリ レーダーチャート", y=1.1)
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
        st.pyplot(fig_r)

# lat/lon を folium 用に変換
df_info_raw = df_info_raw.rename(columns={"lat": "latitude", "lon": "longitude"})

# 地図表示
st.subheader("🗺️ 駅の位置マップ（基準駅＋類似駅）")

df_map_data = df_info_raw[df_info_raw["station_label"].isin(target_labels)].copy()
df_map_data = df_map_data.dropna(subset=["latitude", "longitude"])

import folium
from streamlit_folium import st_folium

# 初期地図中心を駅群の平均位置に設定
start_coords = [df_map_data["latitude"].mean(), df_map_data["longitude"].mean()]
m = folium.Map(location=start_coords, zoom_start=11)

# 駅をマッピング
for _, row in df_map_data.iterrows():
    color = "red" if row["station_label"] in selected_station_labels else "blue"
    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=6,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.8,
        tooltip=row["station_label"],
    ).add_to(m)

st_folium(m, width=800, height=500)
