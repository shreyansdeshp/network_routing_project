"""
graph_utils.py
--------------
Helper functions to load, clean and convert the network data.

  * The network is stored as a pandas DataFrame of links:  source | target | cost
  * The algorithms need a NumPy adjacency matrix, so build_matrix() converts it.
"""

import os
import string

import numpy as np
import pandas as pd

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "sample_network.csv")


def load_sample():
    """Read the sample network from the CSV file using pandas."""
    return pd.read_csv(DATA_FILE)


def clean_edges(df):
    """
    Clean the links table typed / uploaded by the user:
      - remove empty rows
      - cost must be a positive number (Dijkstra needs non-negative weights)
      - remove self loops (A -> A)
      - if the same link appears twice, keep the cheaper one
    """
    df = df[["source", "target", "cost"]].dropna().copy()
    df["source"] = df["source"].astype(str).str.strip()
    df["target"] = df["target"].astype(str).str.strip()
    df["cost"] = pd.to_numeric(df["cost"], errors="coerce")

    df = df[(df["source"] != "") & (df["target"] != "")]
    df = df[df["cost"] > 0]
    df = df[df["source"] != df["target"]]

    # links are two-way, so A-B and B-A are the same link -> sort each pair
    a = np.where(df["source"] < df["target"], df["source"], df["target"])
    b = np.where(df["source"] < df["target"], df["target"], df["source"])
    df = pd.DataFrame({"source": a, "target": b, "cost": df["cost"].values})
    df = df.groupby(["source", "target"], as_index=False)["cost"].min()
    return df.reset_index(drop=True)


def build_matrix(edges, nodes=None):
    """
    Convert the links table into an adjacency matrix (NumPy array).
    Returns (list_of_node_names, matrix).
    """
    if nodes is None:
        nodes = sorted(set(edges["source"]) | set(edges["target"]))
    index = {name: i for i, name in enumerate(nodes)}

    n = len(nodes)
    matrix = np.full((n, n), np.inf)   # no link = infinity
    np.fill_diagonal(matrix, 0)        # distance to itself = 0

    for s, t, c in edges[["source", "target", "cost"]].itertuples(index=False):
        i, j = index[s], index[t]
        matrix[i, j] = c
        matrix[j, i] = c               # undirected: link works both ways
    return nodes, matrix


def node_names(n):
    """A, B, C ... for small networks, N1, N2 ... for big ones."""
    if n <= 26:
        return list(string.ascii_uppercase[:n])
    return [f"N{i + 1}" for i in range(n)]


def random_network(n_nodes, extra_links, seed=None, max_cost=20):
    """
    Generate a random CONNECTED network.
      1. Connect every node to a random earlier node (a spanning tree),
         so every router can reach every other router.
      2. Add some extra random links to create alternative routes.
    """
    rng = np.random.default_rng(seed)
    names = node_names(n_nodes)
    order = rng.permutation(n_nodes)
    links = set()

    for i in range(1, n_nodes):
        a, b = int(order[i]), int(order[rng.integers(0, i)])
        links.add((min(a, b), max(a, b)))

    max_links = n_nodes * (n_nodes - 1) // 2
    wanted = min(len(links) + extra_links, max_links)
    while len(links) < wanted:
        a, b = rng.choice(n_nodes, size=2, replace=False)
        links.add((int(min(a, b)), int(max(a, b))))

    rows = [(names[a], names[b], int(rng.integers(1, max_cost + 1))) for a, b in sorted(links)]
    return pd.DataFrame(rows, columns=["source", "target", "cost"])


def fmt(value):
    """Show infinity as the ∞ symbol and drop useless .0 from numbers."""
    return "∞" if np.isinf(value) else f"{value:g}"


def matrix_to_table(matrix, nodes):
    """Turn a NumPy matrix into a labelled pandas DataFrame for display."""
    table = pd.DataFrame(matrix, index=nodes, columns=nodes)
    return table.map(fmt)
