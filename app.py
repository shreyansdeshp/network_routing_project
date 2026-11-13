"""
app.py  -  Network Routing & Shortest Path Optimization
--------------------------------------------------------
Front end built with Streamlit (100% Python).

Run:   streamlit run app.py

Files:
    algorithms.py   -> Dijkstra and Floyd-Warshall           (the core logic)
    graph_utils.py  -> load / clean data, adjacency matrix, random network
    visualize.py    -> Plotly drawings (network graph, heatmap, charts)
    ui.py           -> CSS theme and HTML cards (looks only)
"""

import inspect
import time

import numpy as np
import pandas as pd
import streamlit as st

import ui
from algorithms import dijkstra, dijkstra_path, floyd_path, floyd_warshall
from graph_utils import (build_matrix, clean_edges, fmt, load_sample,
                         matrix_to_table, random_network)
from visualize import (PLOT_CONFIG, draw_heatmap, draw_network, draw_speed_chart,
                       spring_layout)

st.set_page_config(page_title="RouteLab · Network Routing Optimizer", page_icon="🛰️",
                   layout="wide", initial_sidebar_state="expanded")
ui.inject_css()

CYAN, AMBER, GREEN, ROSE, VIOLET, INDIGO = "#22d3ee", "#fbbf24", "#34d399", "#fb7185", "#a78bfa", "#818cf8"


def show_chart(fig, key):
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG, theme=None, key=key)


def names(indices):
    return [nodes[i] for i in indices]


def hop_costs(path):
    return [matrix[nodes.index(a), nodes.index(b)] for a, b in zip(path, path[1:])]


def cost_or_none(v):
    """For progress-bar columns: numbers stay numbers, infinity becomes empty."""
    return None if np.isinf(v) else float(v)


# ---------------------------------------------------------------- session state
if "edges" not in st.session_state:
    st.session_state.edges = load_sample()
    st.session_state.version = 0


def use_network(df):
    """Replace the current network (changing the version resets the table editor)."""
    st.session_state.edges = df.reset_index(drop=True)
    st.session_state.version += 1


# ---------------------------------------------------------------- sidebar
with st.sidebar:
    ui.brand()
    ui.side_label("Network source")
    choice = st.segmented_control("Network source", ["Sample", "Random", "Upload"],
                                  default="Sample", label_visibility="collapsed") or "Sample"

    if choice == "Sample":
        st.caption("8 routers (A–H) connected by 13 links.")
        if st.button("Load sample network", type="primary", width="stretch", icon=":material/hub:"):
            use_network(load_sample())

    elif choice == "Random":
        n_routers = st.slider("Routers", 4, 20, 8)
        max_extra = n_routers * (n_routers - 1) // 2 - (n_routers - 1)
        extra = st.slider("Extra links (alternate routes)", 0, max_extra, min(n_routers, max_extra))
        seed = st.number_input("Random seed", 0, 9999, 42)
        if st.button("Generate network", type="primary", width="stretch", icon=":material/casino:"):
            use_network(random_network(n_routers, extra, seed))

    else:
        file = st.file_uploader("CSV with columns: source, target, cost", type="csv")
        if file is not None and st.button("Use this file", type="primary", width="stretch",
                                          icon=":material/upload:"):
            df = pd.read_csv(file)
            if {"source", "target", "cost"}.issubset(df.columns):
                use_network(df[["source", "target", "cost"]])
            else:
                st.error("CSV must have the columns: source, target, cost")

    ui.side_label("Legend")
    ui.legend(vertical=True)
    ui.side_label("Cheat sheet")
    ui.cheat_sheet()

# ---------------------------------------------------------------- header
ui.hero()
stats_area = st.container()     # filled once the network has been read

tab_net, tab_dij, tab_fw, tab_fail, tab_cmp = st.tabs([
    ":material/hub: Network", ":material/my_location: Dijkstra", ":material/grid_on: Floyd–Warshall",
    ":material/link_off: Link failure", ":material/analytics: Compare",
])

# ================================================================ 1. NETWORK
with tab_net:
    ui.section("Step 1 · Topology", "Design the network",
               "Each row is a <b>two-way link</b> between routers. Edit a cost, add or delete a row "
               "and every tab recalculates instantly.")
    left, right = st.columns([1, 1.75], gap="large")
    with left:
        edited = st.data_editor(
            st.session_state.edges, key=f"editor_{st.session_state.version}",
            num_rows="dynamic", hide_index=True, width="stretch", height=478,
            column_config={
                "source": st.column_config.TextColumn("From", width="small"),
                "target": st.column_config.TextColumn("To", width="small"),
                "cost": st.column_config.NumberColumn("Cost", min_value=0, step=1, width="small"),
            },
        )

    edges = clean_edges(edited)
    if edges.empty:
        ui.callout("warn", "The network is empty", "Add at least one link with a positive cost.")
        st.stop()

    nodes, matrix = build_matrix(edges)
    n = len(nodes)
    pos = spring_layout(nodes, edges)
    sig = abs(hash(tuple(nodes)))          # widget keys change when the routers change

    with right:
        with st.container(border=True, key="card_1"):
            show_chart(draw_network(nodes, edges, pos, height=462), "net_graph")

    ui.section("Data structure", "Adjacency matrix",
               "The algorithms read the network from this <b>NumPy n × n array</b>. "
               "<code>matrix[i][j]</code> is the link cost, <b>∞</b> means no direct link, the diagonal is 0.")
    st.dataframe(
        matrix_to_table(matrix, nodes).style.map(
            lambda v: "color:#475569" if v == "∞" else "color:#64748b" if v == "0"
            else "color:#22d3ee; font-weight:700"),
        width="stretch",
    )

# shared results used by several tabs
dist_all, nxt, fw_steps = floyd_warshall(matrix)
finite = dist_all[np.isfinite(dist_all)]
connected = bool(np.isfinite(dist_all).all())

with stats_area:
    ui.kpis([
        ("◉", "Routers", n, "nodes in the graph", CYAN),
        ("⟷", "Links", len(edges), "two-way edges", INDIGO),
        ("∑", "Avg link cost", f"{edges['cost'].mean():.2f}",
         f"min {edges['cost'].min():g} · max {edges['cost'].max():g}", VIOLET),
        ("⌀", "Network diameter", fmt(finite.max()), "longest shortest path", AMBER),
        ("✓" if connected else "✕", "Connectivity", "Connected" if connected else "Split",
         "every router reachable" if connected else "some routers unreachable", GREEN if connected else ROSE),
    ])

# ================================================================ 2. DIJKSTRA
with tab_dij:
    ui.section("Step 2 · Single source", "Dijkstra's algorithm",
               "<b>Greedy:</b> always settle the closest unvisited router next, then try to improve "
               "(<i>relax</i>) the distance of its neighbours.")
    c1, c2, _ = st.columns([1, 1, 1.4])
    src = c1.selectbox("Source router", nodes, key=f"dsrc{sig}")
    dst = c2.selectbox("Destination router", nodes, index=n - 1, key=f"ddst{sig}")
    s, d = nodes.index(src), nodes.index(dst)

    t0 = time.perf_counter()
    dist, prev, steps = dijkstra(matrix, s)
    elapsed = (time.perf_counter() - t0) * 1e6
    path = names(dijkstra_path(prev, s, d))

    ui.kpis([
        ("∑", "Total cost", fmt(dist[d]), f"from {src} to {dst}", AMBER),
        ("↝", "Hops", len(path) - 1 if path else "–", "links travelled", CYAN),
        ("◉", "Routers settled", len(steps), "loop iterations", VIOLET),
        ("⏱", "Compute time", f"{elapsed:,.0f} µs", "pure Python + NumPy", GREEN),
    ])
    if path:
        ui.route(path, hop_costs(path), fmt(dist[d]))
    else:
        ui.callout("danger", f"No route from {src} to {dst}", "These routers are in different parts of the network.")

    g, t = st.columns([1.65, 1], gap="large")
    with g:
        with st.container(border=True, key="card_2"):
            ui.legend(items=ui.LEGEND_ITEMS[:3])
            show_chart(draw_network(nodes, edges, pos, path, src, dst, height=430), "dij_graph")
    with t:
        with st.container(border=True, key="card_3"):
            st.markdown(f"**Distance table from {src}**")
            table = pd.DataFrame({
                "Router": nodes,
                "Cost": [cost_or_none(v) for v in dist],
                "Route": [" → ".join(names(dijkstra_path(prev, s, v))) or "unreachable" for v in range(n)],
            })
            st.dataframe(table, hide_index=True, width="stretch", height=min(440, 35 * (n + 1) + 3), column_config={
                "Router": st.column_config.TextColumn("To", width=40),
                "Route": st.column_config.TextColumn("Route", width="large"),
                "Cost": st.column_config.ProgressColumn("Cost", min_value=0, format="%g", width=110,
                                                        max_value=float(np.nanmax(table["Cost"].astype(float)) or 1)),
            })

    # ---- walkthrough ----
    ui.section("Walkthrough", "Replay Dijkstra step by step",
               "Drag the slider. <b>Violet</b> = router being settled now, <b>cyan</b> = already final, "
               "dark = not visited yet. The label under each router is its current distance.")
    k = st.slider("Step", 0, len(steps), len(steps))
    a, b = st.columns([1.65, 1], gap="large")
    if k == 0:
        state = np.where(np.arange(n) == s, 0.0, np.inf)
        visited_now, current = [], None
    else:
        state = steps[k - 1]["dist"]
        visited_now = names(st_["visited"] for st_ in steps[:k - 1])
        current = nodes[steps[k - 1]["visited"]]
    with a:
        with st.container(border=True, key="card_4"):
            show_chart(draw_network(nodes, edges, pos, path if k == len(steps) else None, src,
                                    visited=visited_now, current=current,
                                    node_text={nm: fmt(state[i]) for i, nm in enumerate(nodes)},
                                    height=430), "dij_walk")
    with b:
        if k == 0:
            ui.explain(f"STEP 0 / {len(steps)}", "Initialise",
                       f"Distance to the source <code>{src}</code> is 0, every other router starts at "
                       "<b>∞</b> (unknown). No router is visited yet.",
                       formula=f"dist[{src}] = 0   ·   dist[others] = ∞")
        else:
            info = steps[k - 1]
            ui.explain(
                f"STEP {k} / {len(steps)}", f"Settle router {current}",
                f"<code>{current}</code> has the smallest distance (<b>{fmt(info['dist'][info['visited']])}</b>) "
                "among unvisited routers, so its distance is now final. Next we relax each of its links.",
                rows_title="Neighbours improved",
                rows=[(nodes[v], f"{fmt(old)} → {fmt(new)}") for v, old, new in info["updated"]],
                empty="No neighbour found a cheaper route this step.",
                formula="if dist[u] + cost(u,v) < dist[v]:  dist[v] = dist[u] + cost(u,v)",
            )
        with st.expander("Full step table", icon=":material/table:"):
            rows = []
            for idx, info in enumerate(steps, start=1):
                row = {"Step": idx, "Settled": nodes[info["visited"]]}
                row.update({nm: fmt(info["dist"][i]) for i, nm in enumerate(nodes)})
                rows.append(row)
            st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")

    with st.expander("View the Python code", icon=":material/code:"):
        st.code(inspect.getsource(dijkstra) + "\n\n" + inspect.getsource(dijkstra_path), language="python")

# ================================================================ 3. FLOYD-WARSHALL
with tab_fw:
    ui.section("Step 3 · All pairs", "Floyd–Warshall algorithm",
               "<b>Dynamic programming:</b> allow one more intermediate router <code>k</code> at a time and "
               "keep any shortcut <code>i → k → j</code> that is cheaper than the current best <code>i → j</code>.")

    left, right = st.columns([1.1, 1], gap="large")
    with right:
        with st.container(border=True, key="card_5"):
            c1, c2 = st.columns(2)
            a_ = c1.selectbox("From", nodes, key=f"fwa{sig}")
            b_ = c2.selectbox("To", nodes, index=n - 1, key=f"fwb{sig}")
            i, j = nodes.index(a_), nodes.index(b_)
            fw_route = names(floyd_path(nxt, i, j))
            if fw_route and len(fw_route) > 1:
                ui.route(fw_route, hop_costs(fw_route), fmt(dist_all[i, j]), tag="Route lookup", compact=True)
            elif a_ == b_:
                ui.callout("info", "Same router", "Pick two different routers.")
            else:
                ui.callout("danger", "No route exists", "These routers are not connected.")
            show_chart(draw_network(nodes, edges, pos, fw_route, a_, b_, height=330), "fw_graph")
    with left:
        with st.container(border=True, key="card_6"):
            st.markdown("**All-pairs shortest distances** — white box = selected pair")
            show_chart(draw_heatmap(dist_all, nodes, highlight=(i, j), height=430), "fw_heat")
            st.download_button("Download matrix as CSV", icon=":material/download:",
                               data=pd.DataFrame(dist_all, index=nodes, columns=nodes).to_csv(),
                               file_name="all_pairs_shortest_paths.csv", mime="text/csv")

    # ---- routing tables ----
    ui.section("Routing tables", "What each router stores",
               "A real router only needs the <b>next hop</b> for every destination – the neighbour to forward "
               "the packet to. Floyd–Warshall's <code>next</code> matrix gives this for all routers at once.")
    r = st.pills("Router", nodes, default=nodes[0], key=f"rt{sig}") or nodes[0]
    ri = nodes.index(r)
    others = [x for x in range(n) if x != ri]
    routing = pd.DataFrame({
        "Destination": names(others),
        "Next hop": [nodes[nxt[ri, x]] if nxt[ri, x] != -1 else "–" for x in others],
        "Cost": [cost_or_none(dist_all[ri, x]) for x in others],
        "Full path": [" → ".join(names(floyd_path(nxt, ri, x))) or "unreachable" for x in others],
    })
    st.dataframe(routing, hide_index=True, width="stretch", column_config={
        "Next hop": st.column_config.TextColumn("Next hop ➜"),
        "Cost": st.column_config.ProgressColumn("Total cost", min_value=0, format="%g",
                                                max_value=float(finite.max() or 1)),
    })

    # ---- walkthrough ----
    ui.section("Walkthrough", "Watch the matrix improve",
               "At <code>k = 0</code> only direct links are known. Each step lets paths pass through one more "
               "router. Cells that just got cheaper are outlined in <b>amber</b>.")
    k = st.slider("Intermediate routers allowed (k)", 0, n, min(3, n))
    a, b = st.columns([1.1, 1], gap="large")
    changed = fw_steps[k] < fw_steps[k - 1] if k > 0 else None
    with a:
        with st.container(border=True, key="card_7"):
            show_chart(draw_heatmap(fw_steps[k], nodes, changed=changed, height=400), "fw_walk")
    with b:
        if k == 0:
            ui.explain(f"k = 0 / {n}", "Start with direct links",
                       "The matrix is just the adjacency matrix: link cost where a link exists, ∞ elsewhere.",
                       formula="dist = adjacency matrix")
        else:
            via = nodes[k - 1]
            pairs = [(x, y) for x, y in zip(*np.nonzero(changed)) if x < y]
            ui.explain(
                f"k = {k} / {n}", f"Allow paths through router {via}",
                f"Allowed intermediate routers: <b>{', '.join(nodes[:k])}</b>. "
                f"For every pair (i, j) we test whether going through <code>{via}</code> is cheaper.",
                formula=f"dist[i][j] = min(dist[i][j], dist[i][{via}] + dist[{via}][j])",
                rows_title=f"Pairs improved via {via} ({len(pairs)})",
                rows=[(f"{nodes[x]} ↔ {nodes[y]}", f"{fmt(fw_steps[k - 1][x, y])} → {fmt(fw_steps[k][x, y])}")
                      for x, y in pairs[:7]],
                empty=f"No pair got cheaper by passing through {via}.",
            )

    with st.expander("View the Python code", icon=":material/code:"):
        st.code(inspect.getsource(floyd_warshall) + "\n\n" + inspect.getsource(floyd_path), language="python")

# ================================================================ 4. LINK FAILURE
with tab_fail:
    ui.section("Step 4 · Resilience", "Link failure & automatic re-routing",
               "Pick a link to cut. The adjacency matrix is rebuilt without it and Dijkstra runs again – "
               "the same thing a dynamic routing protocol does when a cable goes down.")
    labels = [f"{s_} ↔ {t_}   ·   cost {c_:g}" for s_, t_, c_ in edges.itertuples(index=False)]
    c1, c2, c3 = st.columns([1, 1, 1.3])
    f_src = c1.selectbox("Source", nodes, key=f"fsrc{sig}")
    f_dst = c2.selectbox("Destination", nodes, index=n - 1, key=f"fdst{sig}")
    fs, fd = nodes.index(f_src), nodes.index(f_dst)

    d_before, p_before, _ = dijkstra(matrix, fs)
    route_before = names(dijkstra_path(p_before, fs, fd))

    # by default, break a link that is ON the current best route (more interesting demo)
    route_links = {frozenset(p) for p in zip(route_before, route_before[1:])}
    on_route = [x for x, (s_, t_) in enumerate(zip(edges["source"], edges["target"]))
                if frozenset((s_, t_)) in route_links]
    broken = c3.selectbox("Link that fails", range(len(edges)), format_func=lambda x: labels[x],
                          index=on_route[len(on_route) // 2] if on_route else 0, key=f"brk{sig}")

    edges_after = edges.drop(index=broken).reset_index(drop=True)
    _, matrix_after = build_matrix(edges_after, nodes=nodes)
    d_after, p_after, _ = dijkstra(matrix_after, fs)
    route_after = names(dijkstra_path(p_after, fs, fd))
    failed = (edges.loc[broken, "source"], edges.loc[broken, "target"])

    if not route_after:
        ui.callout("danger", "Destination unreachable",
                   f"Without link {failed[0]} ↔ {failed[1]} the network is split – no path from {f_src} to {f_dst}.")
    elif route_before == route_after:
        ui.callout("ok", "Route unaffected",
                   f"Link {failed[0]} ↔ {failed[1]} was not on the best route, so traffic keeps flowing the same way.")
    else:
        extra_cost = d_after[fd] - d_before[fd]
        ui.callout("warn", f"Traffic re-routed · cost +{extra_cost:g}",
                   f"The old route used link {failed[0]} ↔ {failed[1]}. The new best route costs "
                   f"{fmt(d_after[fd])} instead of {fmt(d_before[fd])} "
                   f"({len(route_after) - 1} hops instead of {len(route_before) - 1}).")

    before, after = st.columns(2, gap="large")
    with before:
        with st.container(border=True, key="card_8"):
            st.markdown("##### Before failure")
            if route_before:
                ui.route(route_before, hop_costs(route_before), fmt(d_before[fd]), tag="Original route", compact=True)
            show_chart(draw_network(nodes, edges, pos, route_before, f_src, f_dst, height=380), "fail_before")
    with after:
        with st.container(border=True, key="card_9"):
            st.markdown("##### After failure")
            if route_after:
                costs_after = [matrix_after[nodes.index(x), nodes.index(y)] for x, y in zip(route_after, route_after[1:])]
                ui.route(route_after, costs_after, fmt(d_after[fd]), tag="New route", compact=True)
            show_chart(draw_network(nodes, edges_after, pos, route_after, f_src, f_dst,
                                    failed_link=failed, height=380), "fail_after")

# ================================================================ 5. COMPARE
with tab_cmp:
    ui.section("Step 5 · Analysis", "Dijkstra vs Floyd–Warshall",
               "Running Dijkstra once from every router also gives all-pairs answers – "
               "we use that to check both algorithms agree.")

    t0 = time.perf_counter()
    dij_all = np.array([dijkstra(matrix, v)[0] for v in range(n)])
    t_dij = time.perf_counter() - t0
    t0 = time.perf_counter()
    fw_all, _, _ = floyd_warshall(matrix, keep_steps=False)
    t_fw = time.perf_counter() - t0
    same = np.allclose(dij_all, fw_all)

    ui.kpis([
        ("⏱", "Dijkstra × every source", f"{t_dij * 1000:.2f} ms", f"{n} runs, one per router", CYAN),
        ("⏱", "Floyd–Warshall", f"{t_fw * 1000:.2f} ms", "a single run", AMBER),
        ("✓" if same else "✕", "Results match", "Yes" if same else "No",
         "np.allclose(dijkstra, floyd)", GREEN if same else ROSE),
    ])

    c1, c2 = st.columns(2, gap="large")
    with c1:
        ui.algo_card("Dijkstra", "Greedy · single source", CYAN, [
            ("Answers", "One source → every router"),
            ("Time complexity", "O(V²) with an array"),
            ("Negative weights", "Not allowed"),
            ("Output", "dist[ ] and prev[ ] arrays"),
            ("Real world", "OSPF link-state routing"),
            ("Best when", "You need routes from one router"),
        ])
    with c2:
        ui.algo_card("Floyd–Warshall", "Dynamic programming · all pairs", AMBER, [
            ("Answers", "Every pair of routers"),
            ("Time complexity", "O(V³)"),
            ("Negative weights", "Allowed (no negative cycles)"),
            ("Output", "dist[ ][ ] and next[ ][ ] matrices"),
            ("Real world", "Full routing tables, small networks"),
            ("Best when", "You need every route at once"),
        ])

    ui.section("Benchmark", "Speed test on random networks",
               "Dijkstra's time grows roughly with <b>V²</b>, Floyd–Warshall's with <b>V³</b>.")
    c1, c2 = st.columns([2, 1], vertical_alignment="bottom")
    biggest = c1.slider("Largest network size", 20, 100, 60, step=10)
    run = c2.button("Run speed test", type="primary", width="stretch", icon=":material/bolt:")
    if run:
        results = []
        bar = st.progress(0.0, text="Benchmarking…")
        sizes = list(range(10, biggest + 1, 10))
        for idx, size in enumerate(sizes):
            _, m = build_matrix(random_network(size, size * 2, seed=size))
            row = {"Routers": size}
            t0 = time.perf_counter()
            dijkstra(m, 0)
            row["Dijkstra (one source)"] = (time.perf_counter() - t0) * 1000
            t0 = time.perf_counter()
            floyd_warshall(m, keep_steps=False)
            row["Floyd–Warshall (all pairs)"] = (time.perf_counter() - t0) * 1000
            results.append(row)
            bar.progress((idx + 1) / len(sizes), text=f"Benchmarking… {size} routers")
        bar.empty()
        with st.container(border=True, key="card_10"):
            show_chart(draw_speed_chart(pd.DataFrame(results)), "bench")
