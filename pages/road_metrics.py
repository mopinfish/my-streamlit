import streamlit as st
import osmnx as ox
import networkx as nx
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def calculate_graph_metrics(place_name, radius=800):
    """
    Retrieve the road network around a given location and compute graph theory metrics.
    
    Parameters:
        place_name (str): Name of the location (e.g., "Tokyo Station, Japan")
        radius (int): Radius of the area to retrieve the network (meters)

    Returns:
        pd.Series: Pandas Series containing the computed metrics.
        G (networkx.Graph): The retrieved road network graph.
    """
    # Get the coordinates of the specified place
    point = ox.geocode(place_name)
    
    # Retrieve the road network within the specified radius
    G = ox.graph_from_point(point, dist=radius, network_type='drive')

    # Number of nodes and edges
    num_nodes = len(G.nodes)
    num_edges = len(G.edges)

    # Number of connected components
    num_components = nx.number_connected_components(nx.Graph(G))

    # **1. Graph Theory Metrics**
    circuit_index = num_edges - num_nodes + num_components  # Circuit index (μ)
    alpha_index = circuit_index / (2 * num_nodes - 5) if num_nodes > 2 else 0  # α index
    beta_index = num_edges / num_nodes if num_nodes > 0 else 0  # β index
    max_edges = 3 * (num_nodes - 2)
    gamma_index = num_edges / max_edges if max_edges > 0 else 0  # γ index

    # Road density and intersection density
    area_km2 = np.pi * (radius / 1000) ** 2  # Area of a circle with radius 800m (km²)
    total_length = sum(nx.get_edge_attributes(G, "length").values()) / 1000  # km
    road_density = total_length / area_km2 if area_km2 > 0 else 0
    intersection_density = num_nodes / area_km2 if area_km2 > 0 else 0

    # Circuitousness (A')
    def calculate_circuitousness():
        circuitousness_values = []
        for u, v, data in G.edges(data=True):
            if 'geometry' in data and data['geometry'] is not None:
                straight_line_distance = data['geometry'].length
            else:
                straight_line_distance = ox.distance.euclidean(
                    G.nodes[u]['y'], G.nodes[u]['x'], G.nodes[v]['y'], G.nodes[v]['x']
                )
            if straight_line_distance > 0:
                circuitousness = data['length'] / straight_line_distance
                circuitousness_values.append(circuitousness)
        return np.mean(circuitousness_values) if circuitousness_values else 0

    circuitousness = calculate_circuitousness()

    # **2. Centrality Metrics**
    degree_centrality = nx.degree_centrality(G)
    closeness_centrality = nx.closeness_centrality(G, distance='length')
    betweenness_centrality = nx.betweenness_centrality(G, weight='length', normalized=True)

    # **3. Integration Value Calculation**
    shortest_paths = dict(nx.shortest_path_length(G, weight='length'))

    # Global Integration
    global_integration_values = {
        node: (num_nodes - 1) / sum(shortest_paths[node].values()) if sum(shortest_paths[node].values()) > 0 else 0
        for node in G.nodes
    }

    # Local Integration (Radius=3)
    local_integration_values = {}
    for node in G.nodes:
        ego_graph = nx.ego_graph(G, node, radius=3, distance='length')
        local_shortest_paths = dict(nx.shortest_path_length(ego_graph, source=node, weight='length'))
        total_distance = sum(local_shortest_paths.values())
        num_local_nodes = len(local_shortest_paths)
        local_integration_values[node] = (num_local_nodes - 1) / total_distance if total_distance > 0 and num_local_nodes > 1 else 0

    # **4. Compute Statistics**
    def compute_statistics(values):
        return np.mean(list(values.values())), np.std(list(values.values()))

    degree_mean, degree_std = compute_statistics(degree_centrality)
    closeness_mean, closeness_std = compute_statistics(closeness_centrality)
    betweenness_mean, betweenness_std = compute_statistics(betweenness_centrality)
    global_mean, global_std = compute_statistics(global_integration_values)
    local_mean, local_std = compute_statistics(local_integration_values)

    # **Return results as Pandas Series**
    metrics = pd.Series({
        "Circuit Index (μ)": circuit_index,
        "Alpha Index": alpha_index,
        "Beta Index": beta_index,
        "Gamma Index": gamma_index,
        "Road Density (km/km²)": road_density,
        "Intersection Density (nodes/km²)": intersection_density,
        "Average Circuitousness (A')": circuitousness,
        "Degree Centrality (Mean)": degree_mean,
        "Degree Centrality (Std Dev)": degree_std,
        "Closeness Centrality (Mean)": closeness_mean,
        "Closeness Centrality (Std Dev)": closeness_std,
        "Betweenness Centrality (Mean)": betweenness_mean,
        "Betweenness Centrality (Std Dev)": betweenness_std,
        "Global Integration (Mean)": global_mean,
        "Global Integration (Std Dev)": global_std,
        "Local Integration (Radius=3, Mean)": local_mean,
        "Local Integration (Radius=3, Std Dev)": local_std
    })
    
    return metrics, G

# **Streamlit UI**
st.title("Urban Road Network Analysis Tool")

# User input form
with st.form("location_form"):
    place_name = st.text_input("Enter a location (e.g., 'Tokyo Station, Japan'):", "Tokyo Station, Japan")
    submitted = st.form_submit_button("Analyze")

if submitted:
    with st.spinner("Analyzing road network..."):
        metrics, G = calculate_graph_metrics(place_name)

    # Display results
    st.subheader("Graph Metrics")
    st.dataframe(metrics)

    # Network plot
    st.subheader("Road Network Visualization")
    fig, ax = ox.plot_graph(G, show=False, close=False)
    st.pyplot(fig)

    # Download CSV
    csv = metrics.to_csv().encode("utf-8")
    st.download_button(
        "Download CSV",
        csv,
        "graph_metrics.csv",
        "text/csv",
        key="download-csv"
    )
