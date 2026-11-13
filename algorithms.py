"""
algorithms.py
-------------
The two shortest-path algorithms used in this project.

  1. Dijkstra        -> shortest path from ONE source router to every other router
  2. Floyd-Warshall  -> shortest path between ALL PAIRS of routers

Both work on an "adjacency matrix" (a NumPy 2D array):
    matrix[i][j] = cost of the link between router i and router j
    matrix[i][j] = inf  -> there is no direct link
    matrix[i][i] = 0    -> cost to reach yourself is zero
"""

import numpy as np

INF = np.inf


# ----------------------------------------------------------------------
# 1. DIJKSTRA  (Greedy algorithm)
# ----------------------------------------------------------------------
def dijkstra(matrix, source):
    """
    Finds the cheapest cost from `source` to every node.

    Idea: repeatedly pick the unvisited node with the smallest known distance,
    mark it as final, and try to improve ("relax") the distance of its neighbours.

    Returns
        dist  : array, dist[v] = cheapest cost from source to v
        prev  : array, prev[v] = node that comes just before v on the best path
        steps : list of dicts, one per iteration - used for the walkthrough
                {"visited": node, "dist": copy of dist, "updated": [(v, old, new), ...]}
    """
    n = len(matrix)
    dist = np.full(n, INF)          # unknown distances start at infinity
    prev = np.full(n, -1)           # -1 means "no previous node yet"
    visited = np.zeros(n, dtype=bool)
    dist[source] = 0
    steps = []

    for _ in range(n):
        # Step 1: choose the unvisited node with the smallest distance
        candidates = np.where(visited, INF, dist)
        u = int(np.argmin(candidates))
        if candidates[u] == INF:     # all remaining nodes are unreachable
            break
        visited[u] = True

        # Step 2: relax every neighbour v of u
        updated = []
        for v in range(n):
            if not visited[v] and matrix[u, v] != INF:
                new_cost = dist[u] + matrix[u, v]
                if new_cost < dist[v]:
                    updated.append((v, dist[v], new_cost))
                    dist[v] = new_cost
                    prev[v] = u

        steps.append({"visited": u, "dist": dist.copy(), "updated": updated})

    return dist, prev, steps


def dijkstra_path(prev, source, target):
    """Walk backwards through `prev` from target to source to rebuild the path."""
    path = []
    node = target
    while node != -1:
        path.append(int(node))
        node = prev[node]
    path.reverse()
    # if the walk did not end at the source, the target is unreachable
    return path if path and path[0] == source else []


# ----------------------------------------------------------------------
# 2. FLOYD-WARSHALL  (Dynamic Programming)
# ----------------------------------------------------------------------
def floyd_warshall(matrix, keep_steps=True):
    """
    Finds the cheapest cost between every pair of nodes.

    Idea: for every node k, check whether going i -> k -> j
    is cheaper than the current best i -> j.

        dist[i][j] = min( dist[i][j],  dist[i][k] + dist[k][j] )

    Returns
        dist  : n x n array of shortest costs
        nxt   : n x n array, nxt[i][j] = FIRST router to go to from i to reach j
                (this is exactly a router's "next hop" in a routing table)
        steps : list of distance matrices after each k (for the step-by-step view)
    """
    n = len(matrix)
    dist = matrix.copy()

    # next hop: if there is a direct link i-j, the next hop from i is j itself
    nxt = np.full((n, n), -1)
    for i in range(n):
        for j in range(n):
            if matrix[i, j] != INF:
                nxt[i, j] = j

    steps = [dist.copy()] if keep_steps else []

    for k in range(n):              # k = intermediate router we are allowed to use
        for i in range(n):          # i = start router
            for j in range(n):      # j = end router
                if dist[i, k] + dist[k, j] < dist[i, j]:
                    dist[i, j] = dist[i, k] + dist[k, j]
                    nxt[i, j] = nxt[i, k]   # to reach j, first head towards k
        if keep_steps:
            steps.append(dist.copy())

    return dist, nxt, steps


def floyd_path(nxt, i, j):
    """Follow the next-hop matrix from i until we reach j."""
    if nxt[i, j] == -1:
        return []
    path = [int(i)]
    while i != j:
        i = nxt[i, j]
        path.append(int(i))
    return path

