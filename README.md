# Network Routing & Shortest Path Optimization

A Python lab project that finds the cheapest route between routers in a network.
Everything is written in Python: **NumPy** for the matrices, **pandas** for the tables,
**Plotly** for the graphs and **Streamlit** for the web front end.

| Algorithm | What it does |
|---|---|
| **Dijkstra** | Shortest path from **one source** router to every other router |
| **Floyd–Warshall** | Shortest path between **all pairs** of routers, plus a routing table for each router |

## How to run

```bash
cd network_routing_project
```

```bash
pip install -r requirements.txt
```

```bash
streamlit run app.py
```

The app opens in your browser at http://localhost:8501.

## Project structure

```
network_routing_project/
├── app.py                  # Streamlit front end (the 5 tabs)
├── algorithms.py           # Dijkstra + Floyd-Warshall  (the main logic)
├── graph_utils.py          # load CSV, clean data, build adjacency matrix, random network
├── visualize.py            # Plotly drawings + force-directed layout (display only)
├── ui.py                   # CSS theme + HTML cards (looks only, no logic)
├── data/sample_network.csv # sample network: 8 routers, 13 links
├── requirements.txt
└── .streamlit/config.toml  # dark theme colours
```

## What each tab shows

1. **Network**: an editable links table (pandas DataFrame), a drawing of the network and the adjacency matrix (NumPy array).
2. **Dijkstra**: pick a source and a destination to see the best route highlighted, the cost to every router, and a **step-by-step replay** with a slider. The graph shows which router is settled at each step, and a card explains which neighbours improved.
3. **Floyd–Warshall**: a heatmap of all-pairs distances, a lookup for any pair, the **routing table** (next hop) for any router, and a **replay** of the matrix after each k, with the cells that improved outlined.
4. **Link failure**: break a link and watch the route recalculate, with before and after shown side by side.
5. **Compare**: checks that both algorithms give the same answers, compares them side by side, and runs a speed test on random networks.

## Input format

A CSV file with three columns. Links work in both directions and costs must be positive.

```
source,target,cost
A,B,4
A,C,2
```

---

# Viva notes

### 1. How is the network stored?
- As a **list of links** in a pandas DataFrame (`source, target, cost`).
- The links are converted into an **adjacency matrix**, a NumPy `n x n` array:
  - `matrix[i][j]` = cost of the link between i and j
  - `np.inf` = no direct link
  - the diagonal is `0`
- The matrix is symmetric because the links are two-way (an undirected graph).

### 2. Dijkstra's algorithm (Greedy)
1. Set `dist[source] = 0` and every other distance to infinity.
2. Pick the **unvisited node with the smallest distance** (`np.argmin`) and mark it visited.
3. **Relax** its neighbours: if `dist[u] + cost(u,v) < dist[v]`, update `dist[v]` and set `prev[v] = u`.
4. Repeat until every node is visited.
5. Rebuild the path by walking backwards through `prev` from the destination.

- **Complexity:** `O(V²)` with an array (`O((V+E) log V)` with a heap).
- **Limitation:** it fails with **negative weights**, because once a node is visited its distance is treated as final.
- **Real use:** OSPF (link-state routing) runs Dijkstra on every router.

### 3. Floyd–Warshall algorithm (Dynamic Programming)
For every intermediate node `k`, then every pair `(i, j)`:

```
dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
```

- Three nested loops, so the complexity is **`O(V³)`**, with `O(V²)` memory.
- It works with negative weights but not **negative cycles** (if `dist[i][i] < 0` there is a negative cycle).
- The **next-hop matrix** `nxt[i][j]` stores the first router to forward to on the way from i to j. That is exactly a router's **routing table**.

### 4. Why is it called "Dynamic Programming"?
The answer for step `k` is built from the stored answers of step `k-1`, so smaller sub-problems are solved once and reused.

### 5. Which one should you use?
- If you need the route from **one** router, use **Dijkstra** (faster).
- If you need routes between **every** pair and the network is small, use **Floyd–Warshall** (simple, gives all routing tables at once).
- Running Dijkstra from every node also gives all pairs: `O(V³)` with the array version.

### 6. Where are NumPy and pandas used?
- **NumPy:** adjacency matrix, `np.inf`, `np.argmin`, `np.where`, `np.full`, `np.allclose` (to check both algorithms agree), random network generation (`default_rng`), and the force-directed layout.
- **pandas:** reading the CSV, cleaning the data (`dropna`, `to_numeric`, `groupby().min()` to remove duplicate links), and building the result tables.

### 7. What happens when a link fails?
The link is removed, the adjacency matrix is rebuilt and Dijkstra runs again. This is how dynamic routing protocols adapt. If no other path exists, the destination becomes unreachable (the distance stays ∞).

### 8. How are the routers placed on screen?
A simple force-directed layout written with NumPy: every pair of routers pushes apart, every link pulls its two routers together, and after about 300 small steps the picture settles. It only affects the drawing, never the routing.

### 9. How do we make sure the random network is connected?
Each new node is first linked to a random node that is already connected, which forms a spanning tree. Extra random links are then added to create alternative routes.
