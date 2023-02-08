import streamlit as st
import numpy as np
import pandas as pd

st.title('This is my first app!')

st.markdown("----")
st.markdown("# Head1")
st.markdown("## Head2")
st.markdown("----")

st.markdown("## Some Widgets")
check = st.checkbox("他のウィジェットを表示する") #引数に入れることでboolを返す

if check:
   st.button("ボタン") #引数に入れるとboolで返す
   st.selectbox("メニューリスト", ("選択肢1", "選択肢2", "選択肢3")) #第一引数：リスト名、第二引数：選択肢
   st.multiselect("メニューリスト（複数選択可）", ("選択肢1", "選択肢2", "選択肢3")) #第一引数：リスト名、第二引数：選択肢、複数選択可
   st.radio("ラジオボタン", ("選択肢1", "選択肢2", "選択肢3")) #第一引数：リスト名（選択肢群の上に表示）、第二引数：選択肢

# 以下をサイドバーに表示
st.sidebar.text_input("文字入力欄") #引数に入力内容を渡せる
st.sidebar.text_area("テキストエリア")

st.markdown("----")

st.markdown("## Visualize Data")
st.write('This is a table')
dataframe = pd.DataFrame(np.random.randn(10, 20),
  columns = ('col %d' % i
    for i in range(20)))
dataframe

dataframe = pd.DataFrame(np.random.randn(10, 5),
  columns = ('col %d' % i
    for i in range(5)))
dataframe
st.write('This is a line_chart.')
st.line_chart(dataframe)

st.write('This is a area_chart.')
st.area_chart(dataframe)

st.write('This is a bar_chart.')
st.bar_chart(dataframe)

st.write('Map data')
data_of_map = pd.DataFrame(
  np.random.randn(1000, 2) / [60, 60] + [36.66, -121.6],
  columns = ['latitude', 'longitude'])
st.map(data_of_map)