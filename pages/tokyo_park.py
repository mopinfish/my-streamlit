import streamlit as st
import os
import json
import socket
import urllib.error
import urllib.request
import pandas as pd
from pandas import json_normalize
import folium

from streamlit_folium import st_folium


# ローカルサーチ
class LocalSearch:

    def __init__(self, appid):
        self.appid = appid

    def search(self, ac, start=0):
        baseurl = 'https://map.yahooapis.jp/search/local/V1/localSearch'
        params = {
          'ac': ac,
          'gc': '0305007',
          'start': start,
          'output': 'json',
          'results': '100',
          'sort': 'score',
        }
        url = '{}?{}'.format(baseurl, urllib.parse.urlencode(params))
        headers = {
            'User-Agent': 'Yahoo AppID: {0}'.format(self.appid),
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3) as res:
            body = res.read()
            return json.loads(body.decode("utf-8"))
#            return self.__json2pois(body)

    def __json2pois(self, data):
        ydf = json.loads(data)
        features = ydf['Feature']
        result = []
        for f in features:
            if f['Geometry']['Type'] == 'point':
                ll = f['Geometry']['Coordinates'].split(',')
                poi = {'name':f['Name'], 'lat': ll[1], 'lon': ll[0]}
                result.append(poi)
        return result


st.title('東京都の公園')

def unwrap(row):
    genres = [x['Name'] for x in row['Genre']]
    genre = ",".join(genres)
    row['Genre'] = genre
    return row

appid = os.environ["YAHOO_CLIENT_ID"]
st.write('This is a table')
ac = 13
start = 0
result = LocalSearch(appid).search(ac, start)
features = result['Feature']

parks = pd.DataFrame(features)

properties = json_normalize(parks['Property']).apply(unwrap, axis=1)
display_parks = parks.copy().drop([
    'Gid',
    'Category',
    'Style',
    'Property',
], axis=1)
display_parks['Address'] = properties['Address']
display_parks['Genre'] = properties['Genre']

display_parks

# center on Liberty Bell, add marker
m = folium.Map(location=[35.6809591, 139.7673068], zoom_start=12)
for idx, park in display_parks.iterrows():
    lonlat = park['Geometry']['Coordinates'].split(',')
    latlon = [lonlat[1], lonlat[0]]

    iframe = folium.IFrame(f"""
        【公園名】：{park['Name']}<br><br>
        【説明】：{park['Description']}<br><br>
        【住所】：{park['Address']}<br><br>
        【ジャンル】：{park['Genre']}
        """
    )
    popup = folium.Popup(iframe, min_width=300, max_width=300)
    folium.Marker(
        latlon, tooltip=park['Name'], popup=popup
    ).add_to(m)

# call to render Folium map in Streamlit
st_data = st_folium(m, width=725)