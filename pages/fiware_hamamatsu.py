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


orion_endpoint = os.getenv("FIWARE_ORION_ENDPOINT")
st.markdown(orion_endpoint)
auth = get_auth()
response = requests.get(orion_endpoint + "/version", auth=auth)
ret = json.dumps(response.json(), indent=2)
st.markdown(f"```{ret}```")


