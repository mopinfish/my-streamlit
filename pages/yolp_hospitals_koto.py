import sys, os
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(str(Path(__file__).resolve().parent.parent))
from lib import YolpSearch

appid = os.environ["YAHOO_CLIENT_ID"]
ac = 13108
gc = "0401"
start = 0
yolp = YolpSearch(appid)
result = yolp.search(ac, gc, start)
features = result["Feature"]
total = result["ResultInfo"]["Total"]

print(total)
print(type(features))
while start + 100 < total:
    start += 100
    print(f"start is {start}")
    result = yolp.search(ac, gc, start)
    features.extend(result["Feature"])
print(len(features))

st.title("Yahoo Local Search Client")


def to_geometry(row):

    row["Coordinates"] = str(row["Geometry"]["Coordinates"])
    return row


hospitals = pd.DataFrame(features).sort_values("Id")
hospitals = hospitals.apply(to_geometry, axis=1)

hospitals
hospitals.to_csv("./data/hospitals_koto.csv", index=False)
