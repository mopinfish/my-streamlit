import json
import pandas as pd
import urllib.error


# ローカルサーチ
class YolpSearch:

    def __init__(self, appid):
        self.appid = appid

    def search(self, ac, gc, start=0):
        baseurl = "https://map.yahooapis.jp/search/local/V1/localSearch"
        params = {
            "ac": ac,
            "gc": gc,
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
