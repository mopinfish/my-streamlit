import os
import json
import socket
import urllib.error
import urllib.request
import pandas as pd
from pandas import json_normalize


# ローカルサーチ
class LocalSearch:

    def __init__(self, appid):
        self.appid = appid

    def search(self, ac, start=0):
        baseurl = "https://map.yahooapis.jp/search/local/V1/localSearch"
        params = {
            "ac": ac,
            "gc": "0305007",
            "start": start,
            "output": "json",
            "results": "200",
            "sort": "score",
        }
        url = "{}?{}".format(baseurl, urllib.parse.urlencode(params))
        headers = {
            "User-Agent": "Yahoo AppID: {0}".format(self.appid),
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3) as res:
            body = res.read()
            return json.loads(body.decode("utf-8"))

    #            return self.__json2pois(body)

    def __json2pois(self, data):
        ydf = json.loads(data)
        features = ydf["Feature"]
        result = []
        for f in features:
            if f["Geometry"]["Type"] == "point":
                ll = f["Geometry"]["Coordinates"].split(",")
                poi = {"name": f["Name"], "lat": ll[1], "lon": ll[0]}
                result.append(poi)
        return result


def unwrap(row):
    genres = [x["Name"] for x in row["Genre"]]
    genre = ",".join(genres)
    row["Genre"] = genre
    return row


def to_geometry(row):

    row["Coordinates"] = str(row["Geometry"]["Coordinates"])
    return row


appid = os.environ["YAHOO_CLIENT_ID"]
ac = 13
start = 0
localSearch = LocalSearch(appid)
result = localSearch.search(ac, start)
features = result["Feature"]
total = result["ResultInfo"]["Total"]

print(total)
print(type(features))
while start + 100 < total:
    start += 100
    print(f"start is {start}")
    result = localSearch.search(ac, start)
    features.extend(result["Feature"])
print(len(features))


parks = pd.DataFrame(features).sort_values("Id")
parks = parks.apply(to_geometry, axis=1)

properties = json_normalize(parks["Property"]).apply(unwrap, axis=1)
display_parks = parks.copy().drop(
    [
        "Gid",
        "Geometry",
        "Category",
        "Style",
        "Property",
    ],
    axis=1,
)
display_parks["Address"] = properties["Address"]
display_parks["Genre"] = properties["Genre"]
display_parks.to_csv("./data/parks.csv", index=False)
