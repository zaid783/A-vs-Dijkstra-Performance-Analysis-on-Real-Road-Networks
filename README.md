# Pathfinding Algorithms Comparison

## 📋 Project Description

This project provides a comprehensive comparison between **Dijkstra's Algorithm** and **A\* (A-Star) Algorithm** for pathfinding on real-world road networks. Using OpenStreetMap data, the application analyzes and visualizes the performance differences between these two classic pathfinding algorithms in urban environments.

The project demonstrates:
- **Algorithm Performance**: Compares execution time, nodes expanded, and computational efficiency
- **Real-World Application**: Uses actual road network data from OpenStreetMap
- **Visual Comparison**: Generates route visualizations showing both algorithms' paths
- **Detailed Metrics**: Provides distance calculations, time estimates, and performance statistics

### Key Features
- ✅ Implementation of Dijkstra's and A* pathfinding algorithms
- ✅ Real-world road network analysis using OSMnx
- ✅ Haversine distance heuristic for A* optimization
- ✅ Time-weighted routing for fastest route estimation
- ✅ Visual route comparison with matplotlib
- ✅ Comprehensive performance metrics and statistics
- ✅ Support for custom location testing

---

## 🛠️ Requirements

### Python Version
- Python 3.8 or higher

### Required Libraries
Install the following Python packages:

```bash
pip install osmnx
pip install networkx
pip install matplotlib
pip install numpy
```

Or install all dependencies at once:

```bash
pip install osmnx networkx matplotlib numpy
```

### System Requirements
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for downloading OpenStreetMap data

---

## 🚀 Getting Started

### Step 1: Clone or Download the Project
Download the project files to your local machine.

### Step 2: Install Dependencies
Open a terminal/command prompt in the project directory and run:

```bash
pip install osmnx networkx matplotlib numpy
```

### Step 3: Run the Main Comparison
Execute the main pathfinding comparison script:

```bash
python pathfinding_comparison.py
```

This will:
1. Load the Karachi road network from OpenStreetMap
2. Test predefined routes (Saima Arabian Villas to Airport, KIET to Airport)
3. Compare Dijkstra's and A* algorithms
4. Generate route visualization images
5. Display comprehensive performance statistics

### Step 4: Test Custom Routes (Optional)
To test your own routes, use the simple test script:

```bash
python simple_test.py
```

**Customize the coordinates** in `simple_test.py`:
```python
# Modify these values (lines 31-40)
city_name = "Karachi"
country = "Pakistan"

source_lat =   # Your starting latitude
source_lon = 67.16766  # Your starting longitude

target_lat = 24.81407  # Your destination latitude
target_lon = 67.01060  # Your destination longitude
```

---

## 📊 Project Outcomes

### Performance Metrics
The project provides detailed performance comparisons including:

1. **Execution Time**: How fast each algorithm finds the optimal path
2. **Distance Calculation**: Total route distance in kilometers
3. **Nodes Expanded**: Number of nodes explored during pathfinding
4. **Speedup Factor**: How much faster A* is compared to Dijkstra
5. **Efficiency Percentage**: Reduction in nodes explored by A*

### Sample Output
```
============================================================
PERFORMANCE SUMMARY
============================================================
🛣️  Dijkstra Distance (Optimal):    15.43 km
🚀 A* Distance (Weighted 1.0x):     15.43 km
🚗 Fastest Route (by time):         15.43 km, ETA 22.5 min
⚡ A* Speedup:                       2.34x faster
🎯 Node Efficiency:                 57.3% fewer nodes
⏱️  Time Saved:                     145.23 ms
============================================================
```

### Visual Outputs
The project generates high-resolution route comparison images:
- **Red Route**: Dijkstra's algorithm path
- **Blue Route**: A* algorithm path
- **Gray Background**: Complete road network

Example output files:
- `saima_arabian_villas,_gadap_town__to_karachi_airport_routes.png`
- `kiet_north_nazimabad_to_karachi_airport_routes.png`

### Key Findings
- **A* is significantly faster** than Dijkstra's algorithm (typically 2-3x speedup)
- **A* explores fewer nodes** (50-60% reduction in most cases)
- **Both algorithms find optimal paths** when using appropriate heuristic weights
- **Real-world performance** varies based on network complexity and route distance

---

## 📁 Project Structure

```
AA Project/
│
├── pathfinding_comparison.py    # Main comparison script
├── simple_test.py               # Simple single-route testing script
├── README.md                    # This file
│
├── cache/                       # OSMnx cached map data
├── Result/                      # Generated route images
├── __pycache__/                 # Python cache files
└── venv/                        # Virtual environment (if used)
```

---

## 🔧 Customization

### Testing Different Cities
Modify the `city_name` and `country` variables in either script:

```python
city_name = "New York"
country = "USA"
```

### Adjusting A* Heuristic Weight
In `pathfinding_comparison.py`, modify line 226:

```python
heuristic_weight = 1.0  # Increase for faster but potentially suboptimal paths
```

### Adding More Test Routes
In `pathfinding_comparison.py`, add routes to the `test_routes` list (lines 388-399):

```python
test_routes = [
    {
        'name': 'Your Route Name',
        'source': (latitude, longitude),
        'target': (latitude, longitude)
    },
    # Add more routes here
]
```

---

## 📝 Algorithm Details

### Dijkstra's Algorithm
- **Type**: Uninformed search algorithm
- **Guarantee**: Always finds the shortest path
- **Performance**: Explores many nodes, slower execution
- **Use Case**: When optimal path is critical

### A* Algorithm
- **Type**: Informed search algorithm with heuristic
- **Heuristic**: Haversine distance (great-circle distance)
- **Guarantee**: Finds optimal path with admissible heuristic
- **Performance**: Explores fewer nodes, faster execution
- **Use Case**: When speed matters and heuristic is available

---

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError: No module named 'osmnx'**
```bash
pip install osmnx
```

**2. Network Download Fails**
- Check your internet connection
- Try a smaller city or specific area
- OSMnx may be rate-limited; wait a few minutes and retry

**3. Memory Error**
- Reduce the city size or use specific neighborhoods
- Close other applications to free up RAM
- Use a more powerful machine for large cities

**4. Plot Not Displaying**
- Plots are saved as PNG files automatically
- Check the project directory for generated images
- Uncomment `plt.show()` in line 326 to display plots

---

## 📚 References

- **OSMnx Documentation**: https://osmnx.readthedocs.io/
- **NetworkX Documentation**: https://networkx.org/
- **Dijkstra's Algorithm**: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- **A* Search Algorithm**: https://en.wikipedia.org/wiki/A*_search_algorithm

---

## 👨‍💻 Author

Created as a demonstration of pathfinding algorithms on real-world road networks.

---

## 📄 License

This project is open-source and available for educational purposes.

---

## 🙏 Acknowledgments

- OpenStreetMap contributors for map data
- OSMnx library by Geoff Boeing
- NetworkX development team
