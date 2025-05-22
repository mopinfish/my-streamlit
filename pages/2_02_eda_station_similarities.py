import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="駅類似度分析（駅コードベース）", layout="wide")
st.title("🚉 駅コードに基づく類似度インタラクティブ分析")

@st.cache_data
def load_data():
    return pd.read_csv("02_tokyo_stations_with_similarities_by_all_metrics.csv", dtype=str)

df = load_data()
df["cosine_similarity"] = df["cosine_similarity"].astype(float)

# 駅コード一覧（比較元）
station_codes = sorted(df["station_cd_source"].unique())

# UI
st.sidebar.header("⚙️ オプション")
selected_code = st.sidebar.selectbox("比較元の駅コードを選択", station_codes)
top_n = st.sidebar.slider("表示数（上位類似駅）", min_value=5, max_value=50, value=10)
show_heatmap = st.sidebar.checkbox("駅コード間の類似度ヒートマップを表示", value=False)

# フィルターと表示
similar_df = (
    df[df["station_cd_source"] == selected_code]
    .sort_values(by="cosine_similarity", ascending=False)
    .head(top_n)
)

st.subheader(f"🔍 駅コード「{selected_code}」に類似する駅トップ {top_n}")
st.dataframe(similar_df.reset_index(drop=True), use_container_width=True)

fig = px.bar(
    similar_df,
    x="station_cd_target",
    y="cosine_similarity",
    labels={"station_cd_target": "類似駅コード", "cosine_similarity": "コサイン類似度"},
    title=f"「{selected_code}」に似ている駅（上位{top_n}件）"
)
st.plotly_chart(fig, use_container_width=True)

# ヒートマップ
if show_heatmap:
    st.subheader("🗺️ 駅コード間の類似度ヒートマップ")
    pivot_df = df.pivot(index="station_cd_source", columns="station_cd_target", values="cosine_similarity")
    fig_map = px.imshow(
        pivot_df,
        aspect="auto",
        color_continuous_scale="Blues",
        title="駅コード間のコサイン類似度マトリクス"
    )
    st.plotly_chart(fig_map, use_container_width=True)

# CSV出力
st.download_button(
    label="📥 類似駅データをCSVでダウンロード",
    data=similar_df.to_csv(index=False).encode("utf-8-sig"),
    file_name=f"similar_stations_{selected_code}.csv",
    mime="text/csv"
)
