import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="東京駅類似度分析", layout="wide")

st.title("🚉 東京駅類似度インタラクティブ分析")
st.markdown("""
このアプリでは、各駅周辺800mの街路構造指標に基づく **コサイン類似度** を用いて、東京都内の駅間の類似性を可視化・探索できます。
""")

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_csv("srp-data/02_tokyo_stations_similarities.csv")
    return df

df = load_data()

# 駅一覧の取得
stations = sorted(set(df["org"]).union(df["dest"]))

# サイドバー
st.sidebar.header("⚙️ オプション")
selected_station = st.sidebar.selectbox("比較元の駅を選択", stations)
top_n = st.sidebar.slider("表示する類似駅の数", min_value=5, max_value=50, value=10)
show_heatmap = st.sidebar.checkbox("ヒートマップを表示", value=False)

# 類似度上位駅を抽出
filtered_df = df[df["org"] == selected_station].sort_values(
    by="Similarity", ascending=False
).head(top_n)

st.subheader(f"🎯 「{selected_station}」 に似ている駅トップ {top_n}")
st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)

# 類似度バー表示
fig_bar = px.bar(
    filtered_df,
    x="dest",
    y="Similarity",
    labels={"target_station": "類似駅", "Similarity": "コサイン類似度"},
    title=f"「{selected_station}」に似ている駅の類似度（上位 {top_n} 件）"
)
st.plotly_chart(fig_bar, use_container_width=True)

# ヒートマップ
if show_heatmap:
    st.subheader("🔍 全駅の類似度ヒートマップ")
    pivot_df = df.pivot(index="org", columns="dest", values="Similarity")
    fig_heatmap = px.imshow(
        pivot_df,
        aspect="auto",
        color_continuous_scale="Viridis",
        title="駅間コサイン類似度ヒートマップ"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# ダウンロード
csv_download = filtered_df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    label="📥 この結果をCSVでダウンロード",
    data=csv_download,
    file_name=f"similar_stations_to_{selected_station}.csv",
    mime="text/csv"
)
