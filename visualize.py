"""
visualize.py
------------
Drawing functions (Plotly):
    spring_layout()    -> where to place each router on screen (display only)
    draw_network()     -> the network graph with the route highlighted
    draw_heatmap()     -> colour-coded distance matrix
    draw_speed_chart() -> benchmark line chart
"""

import numpy as np
import plotly.graph_objects as go

from graph_utils import fmt

CYAN, AMBER, GREEN, ROSE, VIOLET = "#22d3ee", "#fbbf24", "#34d399", "#fb7185", "#a78bfa"
INK, NODE_BG = "#070b14", "#0f1a2e"
FONT = "Inter, sans-serif"
PLOT_CONFIG = {"displayModeBar": False}


def rgba(hex_color, alpha):
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


# ----------------------------------------------------------------------
# Layout: a simple force-directed ("spring") layout using NumPy.
#   * every pair of routers pushes each other away  (repulsion)
#   * every link pulls its two routers together     (attraction, like a spring)
# After a few hundred small moves the network spreads out nicely.
# It only decides the picture - it has nothing to do with the routing.
# ----------------------------------------------------------------------
def spring_layout(nodes, edges, iterations=300):
    n = len(nodes)
    index = {name: i for i, name in enumerate(nodes)}
    links = [(index[s], index[t]) for s, t in zip(edges["source"], edges["target"])]

    angles = np.linspace(0, 2 * np.pi, n, endpoint=False) + np.pi / 2
    pos = np.column_stack([np.cos(angles), np.sin(angles)])      # start on a circle
    if n <= 2:
        return {name: pos[i] for i, name in enumerate(nodes)}

    k = 2 / np.sqrt(n)          # ideal distance between two routers
    step = 0.12
    for _ in range(iterations):
        delta = pos[:, None, :] - pos[None, :, :]                 # vector between every pair
        dist = np.linalg.norm(delta, axis=2)
        np.fill_diagonal(dist, 1)
        move = ((k * k / dist ** 2)[:, :, None] * delta).sum(axis=1)   # repulsion
        for i, j in links:                                        # attraction along links
            d = pos[i] - pos[j]
            pull = d * np.linalg.norm(d) / k
            move[i] -= pull
            move[j] += pull
        move -= 0.3 * pos                                         # gentle pull to the centre
        length = np.linalg.norm(move, axis=1) + 1e-9
        pos += move / length[:, None] * np.minimum(length, step)[:, None]
        step *= 0.985                                             # cool down

    pos -= pos.mean(axis=0)
    pos /= np.abs(pos).max(axis=0) + 1e-9                         # fit into [-1, 1]
    return {name: pos[i] for i, name in enumerate(nodes)}


# ----------------------------------------------------------------------
def draw_network(nodes, edges, pos, path=None, source=None, target=None, failed_link=None,
                 visited=(), current=None, node_text=None, height=470):
    path = list(path or [])
    path_links = {frozenset(p) for p in zip(path, path[1:])}
    fig = go.Figure()

    # ---- links ----
    normal_x, normal_y, best_x, best_y = [], [], [], []
    degree = {name: 0 for name in nodes}
    for s, t, c in edges[["source", "target", "cost"]].itertuples(index=False):
        degree[s] += 1
        degree[t] += 1
        (x0, y0), (x1, y1) = pos[s], pos[t]
        on_path = frozenset((s, t)) in path_links
        if on_path:
            best_x += [x0, x1, None]
            best_y += [y0, y1, None]
        else:
            normal_x += [x0, x1, None]
            normal_y += [y0, y1, None]
        fig.add_annotation(
            x=(x0 + x1) / 2, y=(y0 + y1) / 2, text=f"{c:g}", showarrow=False,
            font=dict(size=11, color=AMBER if on_path else "#cbd5e1", family=FONT),
            bgcolor="#0b1220", borderpad=3, borderwidth=1,
            bordercolor=rgba(AMBER, .7) if on_path else "rgba(148,163,184,.25)",
        )

    fig.add_trace(go.Scatter(x=normal_x, y=normal_y, mode="lines", hoverinfo="skip",
                             line=dict(color="rgba(148,163,184,.30)", width=1.6)))
    if best_x:
        fig.add_trace(go.Scatter(x=best_x, y=best_y, mode="lines", hoverinfo="skip",
                                 line=dict(color=rgba(AMBER, .16), width=18)))
        fig.add_trace(go.Scatter(x=best_x, y=best_y, mode="lines", hoverinfo="skip",
                                 line=dict(color=AMBER, width=4)))
    if failed_link:
        (x0, y0), (x1, y1) = pos[failed_link[0]], pos[failed_link[1]]
        fig.add_trace(go.Scatter(x=[x0, x1], y=[y0, y1], mode="lines", hoverinfo="skip",
                                 line=dict(color=ROSE, width=3, dash="dot")))
        fig.add_trace(go.Scatter(x=[(x0 + x1) / 2], y=[(y0 + y1) / 2], mode="markers", hoverinfo="skip",
                                 marker=dict(symbol="x-thin", size=18, line=dict(color=ROSE, width=4))))

    # ---- routers: choose a colour for each one ----
    fill, halo, ring, label = [], [], [], []
    for name in nodes:
        if name == source:
            color = GREEN
        elif name == target:
            color = ROSE
        elif name == current:
            color = VIOLET
        elif name in path:
            color = AMBER
        elif name in visited:
            color = CYAN
        else:
            color = None
        fill.append(color or NODE_BG)
        halo.append(rgba(color, .20) if color else rgba(CYAN, .07))
        ring.append("rgba(255,255,255,.35)" if color else CYAN)
        label.append(INK if color else "#e5e7eb")

    xs = [pos[name][0] for name in nodes]
    ys = [pos[name][1] for name in nodes]
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="markers", hoverinfo="skip",
                             marker=dict(size=64, color=halo, line=dict(width=0))))
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="markers+text", text=nodes, textposition="middle center",
        textfont=dict(color=label, size=14, family="Space Grotesk, Inter, sans-serif"),
        marker=dict(size=40, color=fill, line=dict(color=ring, width=2)),
        hovertext=[f"<b>Router {nm}</b><br>{degree[nm]} links" for nm in nodes], hoverinfo="text",
    ))

    # small label under each router (used for distances in the walkthrough)
    if node_text:
        for name in nodes:
            fig.add_annotation(x=pos[name][0], y=pos[name][1], yshift=-33, showarrow=False,
                               text=f"<b>{node_text[name]}</b>",
                               font=dict(size=11, color="#e5e7eb", family="JetBrains Mono, monospace"),
                               bgcolor="rgba(167,139,250,.18)", bordercolor="rgba(167,139,250,.45)",
                               borderwidth=1, borderpad=3)

    fig.update_layout(
        showlegend=False, height=height, margin=dict(l=6, r=6, t=6, b=6), font=dict(family=FONT),
        xaxis=dict(visible=False, range=[-1.18, 1.18], fixedrange=True),
        yaxis=dict(visible=False, range=[-1.32 if node_text else -1.2, 1.2], fixedrange=True),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", dragmode=False,
        hoverlabel=dict(bgcolor="#0f1626", bordercolor="#334155", font=dict(family=FONT, color="#e5e7eb")),
    )
    return fig


# ----------------------------------------------------------------------
def draw_heatmap(matrix, nodes, highlight=None, changed=None, height=430):
    """Distance matrix as coloured tiles. highlight=(i, j) outlines one cell,
    changed = boolean matrix of cells to outline in amber."""
    n = len(nodes)
    z = np.where(np.isfinite(matrix), matrix, np.nan)
    text = [[fmt(v) for v in row] for row in matrix]
    fig = go.Figure(go.Heatmap(
        z=z, x=nodes, y=nodes, text=text, texttemplate="%{text}",
        textfont=dict(family=FONT, size=12 if n <= 12 else 9, color="#f1f5f9"),
        colorscale=[[0, "#0c2233"], [0.4, "#0e7490"], [0.75, "#6366f1"], [1, "#c084fc"]],
        xgap=3, ygap=3, showscale=False,
        hovertemplate="%{y} → %{x}<br>cost <b>%{text}</b><extra></extra>",
    ))
    if changed is not None:
        for i, j in zip(*np.nonzero(changed)):
            fig.add_shape(type="rect", x0=j - .5, x1=j + .5, y0=i - .5, y1=i + .5,
                          line=dict(color=AMBER, width=2.5))
    if highlight is not None:
        i, j = highlight
        fig.add_shape(type="rect", x0=j - .5, x1=j + .5, y0=i - .5, y1=i + .5,
                      line=dict(color="#ffffff", width=3))
    axis = dict(showgrid=False, zeroline=False, fixedrange=True, automargin=True, ticks="",
                tickfont=dict(color="#94a3b8", size=12, family="Space Grotesk, Inter, sans-serif"))
    fig.update_layout(
        height=height, margin=dict(l=34, r=6, t=34, b=6), font=dict(family=FONT),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#0b1220",
        xaxis=dict(side="top", **axis), yaxis=dict(autorange="reversed", **axis),
        hoverlabel=dict(bgcolor="#0f1626", bordercolor="#334155", font=dict(family=FONT, color="#e5e7eb")),
    )
    return fig


# ----------------------------------------------------------------------
def draw_speed_chart(df):
    fig = go.Figure()
    for col, color in [("Dijkstra (one source)", CYAN), ("Floyd–Warshall (all pairs)", AMBER)]:
        fig.add_trace(go.Scatter(
            x=df["Routers"], y=df[col], name=col, mode="lines+markers",
            line=dict(color=color, width=3, shape="spline"), marker=dict(size=8, color=color),
            fill="tozeroy", fillcolor=rgba(color, .07),
            hovertemplate="%{x} routers<br>%{y:.2f} ms<extra>" + col + "</extra>",
        ))
    grid = dict(gridcolor="rgba(148,163,184,.10)", zeroline=False, color="#94a3b8", automargin=True)
    fig.update_layout(
        height=380, margin=dict(l=60, r=16, t=40, b=50), font=dict(family=FONT, color="#cbd5e1"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=1.12, x=0),
        xaxis=dict(title="Number of routers", **grid), yaxis=dict(title="Time (ms)", **grid),
        hoverlabel=dict(bgcolor="#0f1626", bordercolor="#334155", font=dict(family=FONT)),
    )
    return fig
