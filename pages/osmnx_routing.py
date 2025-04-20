import streamlit as st
import osmnx as ox

ox.config(use_cache=True, log_console=True)
from geopy.geocoders import Nominatim
import folium
from folium import plugins
from streamlit_folium import st_folium
import contextily
import shapely.geometry
import geopandas
import contextily
import matplotlib.pyplot

geolocator = Nominatim(user_agent="geocoding-example")

st.title("Routing by OSMnx")

address = st.text_input("表示したい場所を入力してください")
origin_address = st.text_input("出発地を入力してください")
destination_address = st.text_input("目的地を入力してください")
network_type = st.selectbox(
    "network_type", ("all_private", "all", "bike", "drive", "drive_service", "walk")
)  # 第一引数：リスト名、第二引数：選択肢、複数選択可

if st.button("最短ルートを表示", key=2):
    # Get the area of interest polygon
    place_polygon = ox.geocode_to_gdf(address)

    # Re-project the polygon to a local projected CRS (so that the CRS unit is meters)
    place_polygon = place_polygon.to_crs("EPSG:3067")

    # Buffer by 200 meters
    place_polygon["geometry"] = place_polygon.buffer(200)

    # Re-project the polygon back to WGS84 (required by OSMnx)
    place_polygon = place_polygon.to_crs("EPSG:4326")

    # Retrieve the network graph
    graph = ox.graph_from_polygon(place_polygon.at[0, "geometry"], network_type="bike")

    # Transform the graph to UTM
    graph = ox.project_graph(graph)

    # Extract reprojected nodes and edges
    nodes, edges = ox.graph_to_gdfs(graph)

    origin = (
        ox.geocode_to_gdf(origin_address)  # fetch geolocation
        .to_crs(edges.crs)  # transform to UTM
        .at[0, "geometry"]  # pick geometry of first row
        .centroid  # use the centre point
    )

    destination = (
        ox.geocode_to_gdf(destination_address)
        .to_crs(edges.crs)
        .at[0, "geometry"]
        .centroid
    )
    origin_node_id = ox.nearest_nodes(graph, origin.x, origin.y)
    destination_node_id = ox.nearest_nodes(graph, destination.x, destination.y)
    # Find the shortest path between origin and destination
    route = ox.shortest_path(graph, origin_node_id, destination_node_id)
    # Plot the shortest path
    fig, ax = ox.plot_graph_route(graph, route)
    # Get the nodes along the shortest path
    route_nodes = nodes.loc[route]

    # Create a geometry for the shortest path
    route_line = shapely.geometry.LineString(list(route_nodes.geometry.values))
    route_geom = geopandas.GeoDataFrame(
        {
            "geometry": [route_line],
            "osm_nodes": [route],
        },
        crs=edges.crs,
    )

    buildings = ox.geometries_from_place(address, {"building": True}).to_crs(edges.crs)

    # Calculate the route length
    route_geom["length_m"] = route_geom.length

    fig, ax = matplotlib.pyplot.subplots(figsize=(12, 8))

    # Plot edges and nodes
    edges.plot(ax=ax, linewidth=0.75, color="gray")
    nodes.plot(ax=ax, markersize=2, color="gray")

    # Add buildings
    ax = buildings.plot(ax=ax, facecolor="lightgray", alpha=0.7)

    # Add the route
    ax = route_geom.plot(ax=ax, linewidth=2, linestyle="--", color="red")

    # Add basemap
    contextily.add_basemap(
        ax, crs=buildings.crs, source=contextily.providers.CartoDB.Positron
    )

    _ = ax.axis("off")
    # Matplotlib の Figure を指定して可視化する
    st.pyplot(ax.figure)
