"""
Simple example script for testing a single route
Modify the coordinates below to test different locations
"""

import osmnx as ox
import networkx as nx
import math
import time
import matplotlib.pyplot as plt
from pathfinding_comparison import (
    dijkstra_with_tracking, 
    a_star_with_tracking, 
    load_city_graph, 
    find_nearest_node,
    plot_routes,
    compare_algorithms,
    print_results_table
)


def main():
    """
    Simple single-route test
    """
    print("="*60)
    print("SIMPLE PATHFINDING TEST")
    print("="*60)
    
    # ===== MODIFY THESE VALUES =====
    city_name = "Karachi"
    country = "Pakistan"
    
    # Source coordinates (Jinnah International Airport)
    source_lat = 24.90210
    source_lon = 67.16766
    
    # Target coordinates (Clifton Beach)
    target_lat = 24.81407
    target_lon = 67.01060
    # ================================
    
    # Load the city's road network
    G = load_city_graph(city_name, country)
    
    if G is None:
        print("Failed to load city network. Exiting...")
        return
    
    # Compare algorithms
    results = compare_algorithms(G, source_lat, source_lon, target_lat, target_lon, city_name)
    
    # Plot the routes
    plot_routes(G, results, city_name)
    
    # Display results table
    print_results_table([results])
    
    print("\n✓ Test complete!")
    print(f"✓ Route map saved as {city_name.lower()}_routes.png")


if __name__ == "__main__":
    main()
