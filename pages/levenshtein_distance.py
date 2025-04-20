import streamlit as st  # type: ignore
import networkx as nx  # type: ignore
from pyvis.network import Network  # type: ignore
import streamlit.components.v1 as components  # type: ignore


### graph info
num = 26
g = [[(i + 1) % num, (i + 4) % num] if i % 7 != 0 else [] for i in range(num)]

weight = [[0] * num for _ in range(num)]
for now in range(num):
    for to in g[now]:
        weight[now][to] += 10 * abs(now - to)
        weight[to][now] += 10 * abs(now - to)

edges = [[] for _ in range(num)]
for i in range(num):
    for j in g[i]:
        w = weight[i][j]
        edges[i].append((w, j))
        edges[j].append((w, i))

nodes = [chr(i + ord("A")) for i in range(num)]

pos = [[i + 1, i + 1] for i in range(num)]


### main body
# title
st.title("Dijkstra")

# sider bar
with st.form(key="node"):
    with st.sidebar:
        s = st.selectbox("Start", nodes)
        t = st.selectbox("End", nodes)
        btn = st.form_submit_button("Run")

# Dijkstra
from heapq import heappop, heappush

s_ = ord(s) - ord("A")
t_ = ord(t) - ord("A")

INF = 10**10

dist = [INF for _ in range(num)]
dist[s_] = 0
visited = [False] * num
prev = [-1] * num
que = []

heappush(que, (dist[s_], s_))
while que:
    w, now = heappop(que)

    if visited[now]:
        continue
    visited[now] = True

    for c, to in edges[now]:
        if visited[to]:
            continue
        if dist[to] > dist[now] + c:
            dist[to] = dist[now] + c
            prev[to] = now
            heappush(que, (dist[to], to))

route = []
now = t_
while now != -1:
    last = prev[now]
    if last == -1:
        break

    route.append((now, last))
    now = last

# generate network
nt = Network("700px", "800px", heading="")

# add nodes
for i in range(num):
    posx = pos[i][0]
    posy = pos[i][1]
    col = "orange" if s == nodes[i] or t == nodes[i] else None
    nt.add_node(i, label=nodes[i], x=posx, y=posy, color=col)

# add edges
for now in range(num):
    for to in g[now]:
        if (now, to) in route or (to, now) in route:
            col, wid = ("orange", 5)
        else:
            col, wid = ("green", 1)
        nt.add_edge(now, to, color=col, width=wid, label=str(weight[now][to]))

# HTMLファイルとして保存
nt.save_graph("network.html")
# StreamlitでHTMLを表示
with open("network.html", "r", encoding="utf-8") as f:
    html = f.read()
components.html(html, height=600)

with st.sidebar:
    st.text(f" {s} から {t} までの距離は {dist[t_]} です")
