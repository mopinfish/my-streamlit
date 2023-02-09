import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

months = {
    '2月': [1, 28],
    '3月': [1, 31],
    '4月': [1, 30],
    '5月': [1, 31],
    '6月': [1, 30],
    '7月': [1, 31],
    '8月': [1, 31],
    '9月': [1, 30],
    '10月': [1, 31],
    '11月': [1, 30],
    '12月': [1, 31],
}

st.title('江東区 花粉グラフ')

selected_month = st.selectbox(
    '表示する月を選択：',
    months.keys()
)
months_number = selected_month.replace('月', '').zfill(2)
start = f"2022{months_number}{str(months[selected_month][0]).zfill(2)}"
end = f"2022{months_number}{str(months[selected_month][1]).zfill(2)}"
url = f'https://wxtech.weathernews.com/opendata/v1/pollen?citycode=13108&start={start}&end={end}'
st.write(url)


pollen = pd.read_csv(url)
pollen = pollen.query('pollen >= 0')
X_dt = pd.to_datetime(pollen['date'])
Y = pollen.pollen

# 描画領域を用意する
fig = plt.figure()
plt.plot(X_dt, Y)
plt.xticks(rotation=30) #横軸目盛りを30度傾ける
plt.show()
# Matplotlib の Figure を指定して可視化する
st.pyplot(fig)