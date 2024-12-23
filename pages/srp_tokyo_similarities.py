import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Set page configuration
st.set_page_config(
    page_title="SRP Tools | Tokyo Similarities",
    page_icon=":school:",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
# Load data
stations = pd.read_csv('data/srp_tools/stations_with_std_stats.csv')
similarities_path = "data/srp_tools/cosine_similarity_tokyo.csv"
similarities = pd.read_csv(similarities_path)
#similarities.columns = ['org-dest', 'Similarity']
#similarities[['org', 'dest']] = similarities['org-dest'].str.split('-', expand=True)
#similarities.drop(columns=['org-dest'], inplace=True)
#similarities = similarities[['org', 'dest', 'Similarity']]
#similarities.to_csv(similarities_path, index=False)

# variables
tokyo_stations = stations[stations['pref_cd'] == 13]


# ------------------------------------------------------------------
# 特徴量の寄与度を計算して可視化
def show_feature_contributions(org, dest):
    columns = ['circuity_avg', 'edge_density_km', 'edge_length_avg',
       'edge_length_total', 'intersection_count', 'intersection_density_km',
       'k_avg', 'm', 'n', 'node_density_km', 'self_loop_proportion',
       'street_density_km', 'street_length_avg', 'street_length_total',
       'street_segment_count', 'streets_per_node_avg', 'average_clustering',
       'mean_integration', 'num_communities', 'modularity', 'var_integration',]

    # 類似度の高いペアのベクトルを取得
    vec1 = stations[stations['station_name'] == org].iloc[0][columns].values
    vec2 = stations[stations['station_name'] == dest].iloc[0][columns].values
    # 寄与度の計算
    contributions = (vec1 * vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    # 寄与率の可視化
    contribution_df = pd.DataFrame(contributions, index=columns, columns=['Contribution'])

    # Matplotlibでグラフを作成
    fig, ax = plt.subplots()
    ax.set_xlim(0, 0.8)  # X軸の範囲を0から0.8に固定
    plt.title('Feature Contributions to Cosine Similarity')
    plt.xlabel('Features')
    plt.ylabel('Contribution')
    plt.grid(axis='y')
    contribution_df.plot(ax = ax, kind='bar', legend=False)
    # StreamlitでMatplotlibのグラフを表示
    st.pyplot(fig)

# Contents of the page
def main():

    # components
    st.title("SRP Tools | Tokyo Similarities Analysis")
    # テキスト入力フィールドを作成
    search_term = st.text_input('検索')
    options = np.unique(tokyo_stations['station_name'].values)
    options = [option for option in options if search_term.lower() in option.lower()] if search_term else options
    target = st.selectbox(
        '対象駅を選択：',
        options,
    )

    if target:
        st.write("You can show dataframes, charts, and other content.")
        similar_stations = similarities.query(f'org == "{target}" | dest == "{target}"').sort_values(by='Similarity', ascending=False)
        top_10 = similar_stations.head(10)
        st.write(top_10)

        # Show feature contributions
        st.write("Feature Contributions")
        dest = st.selectbox(
            '寄与率を可視化する対象駅を選択：',
            pd.concat([top_10['org'], top_10['dest']]).unique(),
        )
        if dest:
            show_feature_contributions(target, dest)

if __name__ == '__main__':
    main()