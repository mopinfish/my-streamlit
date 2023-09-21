import json
import os
import streamlit as st

import requests
from pycognito.utils import RequestsSrpAuth
from requests.auth import AuthBase

def get_auth() -> AuthBase:
    auth = RequestsSrpAuth(
        username=os.getenv("FIWARE_USERNAME"),
        password=os.getenv("FIWARE_PASSWORD"),
        user_pool_id=os.getenv("FIWARE_USER_POOL_ID"),
        client_id=os.getenv("FIWARE_APP_CLIENT_ID"),
        user_pool_region=os.getenv("FIWARE_USER_POOL_REGION"),
    )
    return auth


auth = get_auth()
headers = {
  'Fiware-Service': 'make_our_city_data',
  'Fiware-ServicePath': '/',
}
orion_endpoint = os.getenv("FIWARE_ORION_ENDPOINT")
path = "/v2/entities?\options=keyValues&limit=100&type=test_type"
response = requests.get(orion_endpoint + path, auth=auth, headers=headers)
st.markdown(f"```{orion_endpoint + path}```")
st.markdown(f"```{response}```")
ret = json.dumps(response.json(), indent=2)
st.markdown(f"```{ret}")
authorization= os.getenv("FIWARE_AUTHORIZATION")

if st.button("データを送る", key=0):
  auth = get_auth()
  headers = {
    'content-type': 'application/json',
    'Fiware-Service': 'make_our_city_data',
    'Fiware-ServicePath': '/',
    'Authorization': authorization,
  }
  data = {
    "type": "test_type",
    "id": "data_fusion_camp1",
    "title": {"value": "浜松で地域課題解決やらまいか！Data Fusion Camp 2023"},
    "subtitle": {"value": "浜松市データ連携基盤を活用したサービス開発実践プログラム"},
    "startAt": {"value": "2023-09-21T10:00:30Z", "type": "DateTime"},
    "endAt": {"value": "2023-09-21T20:00:31Z", "type": "DateTime"},
    "currentContents": {"value": "開催の挨拶"},
    "nextContents": {"value": "ハッカソンのプログラム説明"},
    "updatedAt": {"value": "2023-09-21T10:00:31Z", "type": "DateTime"}
  }
  response = requests.post(orion_endpoint + "/v2/entities", auth=auth, headers=headers, data=json.dumps(data))
  st.markdown(f"```{response}")
  st.markdown("送ったよ")
