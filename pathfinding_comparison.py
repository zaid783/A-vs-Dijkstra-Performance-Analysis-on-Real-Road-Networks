import osmnx as ox
import networkx as nx
import math
import time
import matplotlib.pyplot as plt
from typing import Tuple, List, Dict, Optional
import heapq

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
   
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return distance


def dijkstra_with_tracking(G: nx.MultiDiGraph, source: int, target: int) -> Tuple[List[int], float, int]:
    
    # Initialize
    distances = {node: float('infinity') for node in G.nodes()}
    distances[source] = 0
    previous_nodes = {node: None for node in G.nodes()}
    priority_queue = [(0, source)]
    visited = set()
    nodes_expanded = 0
    
    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        
        # Skip if already visited
        if current_node in visited:
            continue
        
        visited.add(current_node)
        nodes_expanded += 1
        
        # Check if we reached the target
        if current_node == target:
            break
        
        # Skip if we've found a shorter path already
        if current_distance > distances[current_node]:
            continue
        
        # Check neighbors
        for neighbor in G.neighbors(current_node):
            # Get edge data (may have multiple edges)
            edge_data = G.get_edge_data(current_node, neighbor)
            # Get the shortest edge if multiple exist
            edge_length = min([data.get('length', 0) for data in edge_data.values()])
            
            distance = current_distance + edge_length
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous_nodes[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))
    
    # Reconstruct path
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()
    
    # Convert distance from meters to kilometers
    distance_km = distances[target] / 1000.0
    
    return path, distance_km, nodes_expanded


def a_star_with_tracking(G: nx.MultiDiGraph, source: int, target: int, heuristic_weight: float = 1.2) -> Tuple[List[int], float, int]:
    
    # Get target coordinates for heuristic
    target_lat = G.nodes[target]['y']
    target_lon = G.nodes[target]['x']
    
    def heuristic(node: int) -> float:
        """Haversine heuristic function"""
        node_lat = G.nodes[node]['y']
        node_lon = G.nodes[node]['x']
        # Return distance in meters (to match edge lengths)
        # We multiply by weight to make it 'greedy'
        return haversine_distance(node_lat, node_lon, target_lat, target_lon) * 1000 * heuristic_weight
    
    # Initialize
    g_scores = {node: float('infinity') for node in G.nodes()}
    g_scores[source] = 0
    
    f_scores = {node: float('infinity') for node in G.nodes()}
    f_scores[source] = heuristic(source)
    
    previous_nodes = {node: None for node in G.nodes()}
    priority_queue = [(f_scores[source], source)]
    visited = set()
    nodes_expanded = 0
    
    while priority_queue:
        current_f, current_node = heapq.heappop(priority_queue)
        
        # Skip if already visited
        if current_node in visited:
            continue
        
        visited.add(current_node)
        nodes_expanded += 1
        
        # Check if we reached the target
        if current_node == target:
            break
        
        # Check neighbors
        for neighbor in G.neighbors(current_node):
            if neighbor in visited:
                continue
            
            # Get edge data
            edge_data = G.get_edge_data(current_node, neighbor)
            edge_length = min([data.get('length', 0) for data in edge_data.values()])
            
            tentative_g_score = g_scores[current_node] + edge_length
            
            if tentative_g_score < g_scores[neighbor]:
                previous_nodes[neighbor] = current_node
                g_scores[neighbor] = tentative_g_score
                f_scores[neighbor] = tentative_g_score + heuristic(neighbor)
                heapq.heappush(priority_queue, (f_scores[neighbor], neighbor))
    
    # Reconstruct path
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = previous_nodes[current]
    path.reverse()
    
    # Convert distance from meters to kilometers
    distance_km = g_scores[target] / 1000.0
    
    return path, distance_km, nodes_expanded


def load_city_graph(city_name: str, country: str = "Pakistan") -> nx.MultiDiGraph:

    print(f"\nLoading road network for {city_name}, {country}...")
    try:
        # Download the street network
        G = ox.graph_from_place(f"{city_name}, {country}", network_type='drive')
    
        # Enrich graph with speeds (km/h) and travel times (seconds) for time-weighted routing
        try:
            G = ox.add_edge_speeds(G)
            G = ox.add_edge_travel_times(G)
        except Exception as _e:
            # If speed data couldn't be added, continue with distance-only routing
            print("! Warning: Could not add speeds/travel times. Time-based routing may be unavailable.")
        
        print(f"✓ Loaded {len(G.nodes())} nodes and {len(G.edges())} edges")
        return G
    except Exception as e:
        print(f"✗ Error loading {city_name}: {e}")
        return None


def find_nearest_node(G: nx.MultiDiGraph, lat: float, lon: float) -> int:
    
    return ox.nearest_nodes(G, lon, lat)


def _sum_path_attribute(G: nx.MultiDiGraph, path: List[int], attr: str) -> float:
   
    if not path or len(path) < 2:
        return 0.0
    total = 0.0
    for u, v in zip(path[:-1], path[1:]):
        data = G.get_edge_data(u, v)
        if not data:
            continue
        # Pick the minimum attribute across parallel edges (safest shortest estimate)
        vals = [d.get(attr) for d in data.values() if d.get(attr) is not None]
        if not vals:
            continue
        total += min(vals)
    return total


def compare_algorithms(G: nx.MultiDiGraph, source_lat: float, source_lon: float, 
                       target_lat: float, target_lon: float, city_name: str) -> Dict:
   
    print(f"\n{'='*60}")
    print(f"Testing in {city_name}")
    print(f"{'='*60}")
    
    # Find nearest nodes
    print(f"Source: ({source_lat}, {source_lon})")
    print(f"Target: ({target_lat}, {target_lon})")
    
    source_node = find_nearest_node(G, source_lat, source_lon)
    target_node = find_nearest_node(G, target_lat, target_lon)
    
    # Run Dijkstra's algorithm (shortest by distance)
    print("\n⏱️  Running Dijkstra's Algorithm...")
    start_time = time.time()
    dijkstra_path, dijkstra_distance, dijkstra_nodes = dijkstra_with_tracking(G, source_node, target_node)
    dijkstra_time = time.time() - start_time
    print(f"✓ Completed in {dijkstra_time:.4f} seconds")
    print(f"  Shortest Path Distance (by road length): {dijkstra_distance:.2f} km")
    print(f"  Nodes expanded: {dijkstra_nodes}")
    
    # Run A* algorithm (Weighted A* for performance)
    heuristic_weight = 1.0
    print(f"\n⏱️  Running Weighted A* Algorithm (Weight={heuristic_weight})...")
    print("   (Prioritizing speed over perfect optimality to show difference)")
    start_time = time.time()
    astar_path, astar_distance, astar_nodes = a_star_with_tracking(G, source_node, target_node, heuristic_weight=heuristic_weight)
    astar_time = time.time() - start_time
    print(f"✓ Completed in {astar_time:.4f} seconds")
    print(f"  Path Distance: {astar_distance:.2f} km")
    print(f"  Nodes expanded: {astar_nodes}")

    # Compute fastest route (time-weighted) to approximate Google-like driving route
    fastest_path = None
    fastest_time_sec = None
    fastest_dist_km = None
    if all('travel_time' in d for _, _, d in G.edges(data=True)):
        try:
            fastest_path = nx.shortest_path(G, source_node, target_node, weight='travel_time')
            fastest_time_sec = _sum_path_attribute(G, fastest_path, 'travel_time')
            fastest_dist_m = _sum_path_attribute(G, fastest_path, 'length')
            fastest_dist_km = (fastest_dist_m or 0) / 1000.0
            print("\n🚗 Estimated Fastest Route (by time):")
            print(f"  ETA: {fastest_time_sec/60:.1f} min")
            print(f"  Distance: {fastest_dist_km:.2f} km")
        except Exception as _e:
            print("\n! Could not compute fastest (time-weighted) route. Proceeding with distance-only results.")
    
    # Performance comparison
    speedup = dijkstra_time / astar_time if astar_time > 0 else 0
    node_reduction = ((dijkstra_nodes - astar_nodes) / dijkstra_nodes * 100) if dijkstra_nodes > 0 else 0
    
    print(f"{'='*60}")
    print(f"PERFORMANCE SUMMARY")
    print(f"{'='*60}")
    print(f"🛣️  Dijkstra Distance (Optimal):    {dijkstra_distance:.2f} km")
    print(f"🚀 A* Distance (Weighted {heuristic_weight}x):     {astar_distance:.2f} km")
    if fastest_dist_km is not None and fastest_time_sec is not None:
        print(f"🚗 Fastest Route (by time):           {fastest_dist_km:.2f} km, ETA {fastest_time_sec/60:.1f} min")
    print(f"⚡ A* Speedup:                     {speedup:.2f}x faster")
    print(f"🎯 Node Efficiency:                {node_reduction:.1f}% fewer nodes")
    print(f"⏱️  Time Saved:                     {(dijkstra_time - astar_time)*1000:.2f} ms")
    print(f"{'='*60}")
    
    # Calculate straight-line distance for internal use only
    # No straight-line reporting; focus on road distances only
    
    results = {
        'city': city_name,
        'dijkstra_time': dijkstra_time,
        'dijkstra_distance': dijkstra_distance,
        'dijkstra_nodes': dijkstra_nodes,
        'dijkstra_path': dijkstra_path,
        'astar_time': astar_time,
        'astar_distance': astar_distance,
        'astar_nodes': astar_nodes,
        'astar_path': astar_path,
    'fastest_path': fastest_path,
    'fastest_time_sec': fastest_time_sec,
    'fastest_distance_km': fastest_dist_km,
        'source_node': source_node,
        'target_node': target_node
    }
    
    return results


def plot_routes(G: nx.MultiDiGraph, results: Dict, city_name: str):

    print(f"\n📊 Plotting routes for {city_name}...")
    
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))
    
    # Plot the graph
    ox.plot_graph(G, ax=ax, show=False, close=False, node_size=0, edge_color='lightgray', edge_linewidth=0.5)
    
    # Plot Dijkstra's path (red)
    ox.plot_graph_route(G, results['dijkstra_path'], ax=ax, route_color='red', 
                        route_linewidth=3, route_alpha=0.7, show=False, close=False,
                        orig_dest_size=100)
    
    # Plot A* path (blue)
    ox.plot_graph_route(G, results['astar_path'], ax=ax, route_color='blue', 
                        route_linewidth=2, route_alpha=0.6, show=False, close=False,
                        orig_dest_size=100)
    
    # Add legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color='red', lw=3, label=f"Dijkstra ({results['dijkstra_distance']:.2f} km)"),
        Line2D([0], [0], color='blue', lw=2, label=f"A* ({results['astar_distance']:.2f} km)")
    ]
    ax.legend(handles=legend_elements, loc='upper right', fontsize=12)
    
    plt.title(f"Pathfinding Comparison - {city_name}", fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Save the plot
    filename = f"{city_name.lower().replace(' ', '_')}_routes.png"
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"✓ Saved plot as {filename}")
    
    # plt.show()  # Disabled to prevent blocking
    plt.close()


def print_results_table(all_results: List[Dict]):
   
    print("\n" + "="*120)
    print("COMPREHENSIVE RESULTS TABLE")
    print("="*120)
    
    # Header
    header = f"{'City':<15} {'Algorithm':<12} {'Time (s)':<12} {'Distance (km)':<15} {'Nodes Exp.':<12} {'Speedup':<10}"
    print(header)
    print("-"*120)
    
    # Print results for each city
    for result in all_results:
        city = result['city']
        
        # Dijkstra row
        dijkstra_row = f"{city:<15} {'Dijkstra':<12} {result['dijkstra_time']:<12.4f} {result['dijkstra_distance']:<15.2f} {result['dijkstra_nodes']:<12} {'-':<10}"
        print(dijkstra_row)
        
        # A* row with speedup
        speedup = result['dijkstra_time'] / result['astar_time'] if result['astar_time'] > 0 else 0
        astar_row = f"{'':<15} {'A*':<12} {result['astar_time']:<12.4f} {result['astar_distance']:<15.2f} {result['astar_nodes']:<12} {speedup:<10.2f}x"
        print(astar_row)
        
        # Efficiency comparison
        node_reduction = ((result['dijkstra_nodes'] - result['astar_nodes']) / result['dijkstra_nodes'] * 100) if result['dijkstra_nodes'] > 0 else 0
        efficiency = f"{'':<15} {'Efficiency':<12} {'':<12} {'':<15} {node_reduction:>10.1f}% less {'':<10}"
        print(efficiency)
        print("-"*120)
    
    # Calculate averages
    avg_dijkstra_time = sum(r['dijkstra_time'] for r in all_results) / len(all_results)
    avg_astar_time = sum(r['astar_time'] for r in all_results) / len(all_results)
    avg_speedup = avg_dijkstra_time / avg_astar_time if avg_astar_time > 0 else 0
    
    print(f"\n{'AVERAGES':<15} {'Dijkstra':<12} {avg_dijkstra_time:<12.4f}")
    print(f"{'':<15} {'A*':<12} {avg_astar_time:<12.4f}")
    print(f"{'':<15} {'Avg Speedup':<12} {avg_speedup:<12.2f}x")
    print("="*120)


def main():
    
    print("="*60)
    print("PATHFINDING ALGORITHMS COMPARISON")
    print("Dijkstra vs A* on Real Road Networks")
    print("="*60)
    
    # Load Karachi graph once
    city_name = "Karachi"
    print(f"\nLoading road network for {city_name}, Pakistan...")
    G = load_city_graph(city_name)
    
    if G is None:
        print(f"Failed to load {city_name}. Exiting.")
        return
    
    # Define test routes within Karachi
    test_routes = [
        {
            'name': 'Saima Arabian Villas, Gadap Town  to karachi airport',
            'source': (25.012617754153904, 67.0413340029906),  # Saima Arabian Villas, Gadap Town
            'target': (24.901617102318127, 67.16795002875136)   # karachi airport
        },
        {
            'name': 'Kiet north nazimabad to karachi airport',
            'source': (24.93030973069608, 67.04517590845255),  # Kiet north nazimabad
            'target': (24.901617102318127, 67.16795002875136)   # karachi airport
        }
    ]
    
    all_results = []
    
    # Test each route
    for route in test_routes:
        route_name = route['name']
        source_lat, source_lon = route['source']
        target_lat, target_lon = route['target']
        
        # Compare algorithms
        results = compare_algorithms(G, source_lat, source_lon, target_lat, target_lon, route_name)
        all_results.append(results)
        
        # Plot routes
        plot_routes(G, results, route_name)
    
    # Print comprehensive results table
    if all_results:
        print_results_table(all_results)
    
    print("\n✓ Analysis complete!")


if __name__ == "__main__":
    main()