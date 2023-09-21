import json
import os
import streamlit as st

import requests

authorization= os.getenv("FIWARE_AUTHORIZATION")
headers = {
  'Fiware-Service': 'make_our_city_data',
  'Fiware-ServicePath': '/',
  'Authorization': authorization,
}
orion_endpoint = os.getenv("FIWARE_ORION_ENDPOINT")
path = "/v2/entities?\options=keyValues&limit=100&type=test_type"
response = requests.get(orion_endpoint + path, headers=headers)
st.markdown(f"```{orion_endpoint + path}```")
st.markdown(f"```{response}```")
ret = json.dumps(response.json(), indent=2)
st.markdown(f"```{ret}")

if st.button("データを送る2", key=0):
  headers = {
    'content-type': 'application/json',
    'Fiware-Service': 'make_our_city_data',
    'Fiware-ServicePath': '/',
    'Authorization': authorization,
  }
  data = {
    "type": "test_type",
    "id": "data_fusion_camp2",
    "title": {"value": "浜松で地域課題解決やらまいか！Data Fusion Camp 2023"},
    "subtitle": {"value": "浜松市データ連携基盤を活用したサービス開発実践プログラム"},
    "startAt": {"value": "2023-09-21T10:00:30Z", "type": "DateTime"},
    "endAt": {"value": "2023-09-21T20:00:31Z", "type": "DateTime"},
    "currentContents": {"value": "開催の挨拶"},
    "nextContents": {"value": "ハッカソンのプログラム説明"},
    "updatedAt": {"value": "2023-09-21T10:00:31Z", "type": "DateTime"}
  }
  path = "/v2/entities/data_fusion_camp/attrs?type=test_type"
  response = requests.post(orion_endpoint + "/v2/entities", headers=headers, data=json.dumps(data))
  st.markdown(f"```{headers}```")
  st.markdown(f"```{response}```")
  st.markdown("送ったよ")
