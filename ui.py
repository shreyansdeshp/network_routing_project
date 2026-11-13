"""
ui.py
-----
Look & feel of the app: the CSS theme and small HTML building blocks
(hero banner, stat cards, route ribbon, callouts ...).

Nothing here affects the algorithms - it only makes the results look good.
"""

import base64

import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

:root {
  --bg: #070b14;
  --surface: rgba(15, 22, 38, .72);
  --surface-solid: #0d1424;
  --line: rgba(148, 163, 184, .14);
  --text: #e5e7eb;
  --muted: #8b98ad;
  --cyan: #22d3ee;
  --indigo: #818cf8;
  --violet: #a78bfa;
  --amber: #fbbf24;
  --green: #34d399;
  --rose: #fb7185;
}

/* ---------- page ---------- */
.stApp {
  background:
    radial-gradient(1100px 560px at 8% -12%, rgba(99, 102, 241, .17), transparent 60%),
    radial-gradient(900px 520px at 100% -5%, rgba(34, 211, 238, .11), transparent 60%),
    var(--bg);
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stDecoration"] { display: none; }
.block-container { padding-top: 2.4rem; padding-bottom: 5rem; max-width: 1380px; }
h1, h2, h3, h4 { font-family: 'Space Grotesk', Inter, sans-serif !important; letter-spacing: -.01em; }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { border-right: 1px solid var(--line); }
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarContent"] { padding-top: 1.2rem; }
.brand { display: flex; align-items: center; gap: 12px; margin: 2px 0 18px; }
.brand .logo {
  width: 42px; height: 42px; border-radius: 12px; display: grid; place-items: center;
  background: linear-gradient(135deg, var(--cyan), var(--indigo) 60%, var(--violet));
  box-shadow: 0 8px 24px rgba(34, 211, 238, .28);
}
.brand .name { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.25rem; color: var(--text); line-height: 1.1; }
.brand .sub { font-size: .78rem; color: var(--muted); }
.side-label {
  font-size: .7rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase;
  color: var(--muted); margin: 18px 0 8px;
}
.cheat { display: grid; gap: 10px; }
.cheat .item { border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px; background: var(--surface); }
.cheat .item b { font-family: 'Space Grotesk', sans-serif; color: var(--text); font-size: .95rem; }
.cheat .item span { display: block; color: var(--muted); font-size: .8rem; margin-top: 3px; }
.cheat code { font-family: 'JetBrains Mono', monospace; color: var(--cyan); background: rgba(34, 211, 238, .08); padding: 1px 6px; border-radius: 6px; font-size: .75rem; }
.side-foot { color: var(--muted); font-size: .75rem; margin-top: 26px; opacity: .8; }

/* ---------- hero ---------- */
.hero {
  position: relative; overflow: hidden; display: flex; align-items: center; justify-content: space-between; gap: 24px;
  padding: 34px 40px; border-radius: 24px; border: 1px solid var(--line);
  background:
    linear-gradient(135deg, rgba(34, 211, 238, .10), rgba(129, 140, 248, .10) 50%, rgba(167, 139, 250, .05)),
    var(--surface-solid);
}
.hero::before {
  content: ""; position: absolute; inset: 0; pointer-events: none;
  background-image:
    linear-gradient(rgba(148, 163, 184, .07) 1px, transparent 1px),
    linear-gradient(90deg, rgba(148, 163, 184, .07) 1px, transparent 1px);
  background-size: 30px 30px;
  -webkit-mask-image: radial-gradient(ellipse at 75% 50%, #000 10%, transparent 70%);
          mask-image: radial-gradient(ellipse at 75% 50%, #000 10%, transparent 70%);
}
.hero-text { position: relative; max-width: 720px; }
.badge {
  display: inline-flex; align-items: center; gap: 8px; padding: 6px 12px; border-radius: 999px;
  border: 1px solid rgba(34, 211, 238, .3); background: rgba(34, 211, 238, .08);
  color: var(--cyan); font-size: .74rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
}
.live { width: 7px; height: 7px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 0 rgba(52, 211, 153, .7); animation: live 2s infinite; }
@keyframes live { 70% { box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); } 100% { box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); } }
.hero-title {
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: var(--text);
  font-size: clamp(1.9rem, 3.1vw, 2.85rem); line-height: 1.07; margin: 16px 0 12px; letter-spacing: -.02em;
}
.grad { background: linear-gradient(90deg, var(--cyan), var(--indigo) 55%, #c084fc); -webkit-background-clip: text; background-clip: text; color: transparent; }
.hero-sub { color: #a8b3c7; font-size: 1.02rem; line-height: 1.6; }
.hero-sub b { color: var(--text); }
.stack { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 20px; }
.stack span {
  font-family: 'JetBrains Mono', monospace; font-size: .78rem; color: #cbd5e1;
  border: 1px solid var(--line); background: rgba(255, 255, 255, .03); padding: 5px 11px; border-radius: 8px;
}
.hero-art { position: relative; width: 340px; height: 190px; flex: none; }
.packet {
  position: absolute; top: 0; left: 0; width: 11px; height: 11px; border-radius: 50%; background: #fff;
  box-shadow: 0 0 14px 5px rgba(251, 191, 36, .85);
  offset-path: path('M30 140 L100 60 L190 100 L315 90'); offset-rotate: 0deg;
  animation: travel 3.4s cubic-bezier(.55, 0, .45, 1) infinite;
}
@keyframes travel {
  0% { offset-distance: 0%; opacity: 0; } 8% { opacity: 1; } 90% { opacity: 1; } 100% { offset-distance: 100%; opacity: 0; }
}
@media (max-width: 1000px) { .hero-art { display: none; } .hero { padding: 26px; } }

/* ---------- section headers ---------- */
.section { margin: 10px 0 2px; }
.section .eyebrow { font-size: .72rem; letter-spacing: .16em; text-transform: uppercase; color: var(--cyan); font-weight: 700; }
.section .title { font-family: 'Space Grotesk', sans-serif; font-size: 1.6rem; font-weight: 700; color: var(--text); margin: 4px 0 4px; letter-spacing: -.01em; }
.section .desc { color: var(--muted); font-size: .96rem; max-width: 860px; line-height: 1.55; }
.section .desc b { color: #cbd5e1; }

/* ---------- KPI cards ---------- */
.kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 14px; }
.kpi {
  position: relative; overflow: hidden; padding: 16px 18px; border-radius: 16px;
  background: var(--surface); border: 1px solid var(--line);
}
.kpi::after {
  content: ""; position: absolute; right: -40px; top: -40px; width: 110px; height: 110px; border-radius: 50%;
  background: radial-gradient(circle, var(--accent), transparent 70%); opacity: .16;
}
.kpi .label { display: flex; align-items: center; gap: 9px; font-size: .74rem; font-weight: 700; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.kpi .ico {
  width: 26px; height: 26px; border-radius: 8px; display: grid; place-items: center; font-size: .85rem;
  color: var(--accent); background: color-mix(in srgb, var(--accent) 16%, transparent);
  border: 1px solid color-mix(in srgb, var(--accent) 30%, transparent);
}
.kpi .value { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.95rem; color: var(--text); margin-top: 10px; line-height: 1.05; }
.kpi .hint { font-size: .8rem; color: var(--muted); margin-top: 5px; }

/* ---------- route ribbon ---------- */
.route {
  border-radius: 16px; padding: 16px 20px; border: 1px solid rgba(251, 191, 36, .28);
  background: linear-gradient(90deg, rgba(251, 191, 36, .08), rgba(251, 191, 36, .02)), var(--surface);
}
.route .head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; gap: 12px; flex-wrap: wrap; }
.route .head .tag { font-size: .72rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; color: var(--amber); }
.route .head .total { color: var(--muted); font-size: .88rem; }
.route .head .total b { color: var(--text); font-family: 'Space Grotesk', sans-serif; font-size: 1.05rem; }
.route .path { display: flex; align-items: center; flex-wrap: wrap; row-gap: 14px; }
.hop {
  width: 40px; height: 40px; border-radius: 50%; display: grid; place-items: center; flex: none;
  font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: .95rem; color: #1b1405;
  background: var(--amber); box-shadow: 0 0 0 4px rgba(251, 191, 36, .14), 0 0 22px rgba(251, 191, 36, .35);
}
.hop.src { background: var(--green); color: #04150e; box-shadow: 0 0 0 4px rgba(52, 211, 153, .15), 0 0 22px rgba(52, 211, 153, .35); }
.hop.dst { background: var(--rose); color: #1a0509; box-shadow: 0 0 0 4px rgba(251, 113, 133, .15), 0 0 22px rgba(251, 113, 133, .35); }
.wire { position: relative; width: 58px; height: 2px; margin: 0 6px; flex: none; background: linear-gradient(90deg, rgba(251, 191, 36, .9), rgba(251, 191, 36, .45)); }
.wire i {
  position: absolute; left: 50%; top: -11px; transform: translateX(-50%); font-style: normal; white-space: nowrap;
  font-family: 'JetBrains Mono', monospace; font-size: .7rem; font-weight: 700; color: var(--amber);
  background: #0b1220; border: 1px solid rgba(251, 191, 36, .45); padding: 1px 7px; border-radius: 999px;
}
.wire i { z-index: 2; }
.route.compact { padding: 14px 16px; }
.route.compact .hop { width: 32px; height: 32px; font-size: .82rem; }
.route.compact .wire { width: 30px; margin: 0 3px; }
.wire::after {
  z-index: 1; content: ""; position: absolute; top: -2px; width: 6px; height: 6px; border-radius: 50%; background: #fff;
  box-shadow: 0 0 8px 2px rgba(251, 191, 36, .9); animation: zip 1.6s linear infinite;
}
@keyframes zip { from { left: 0; opacity: 0; } 20% { opacity: 1; } 80% { opacity: 1; } to { left: calc(100% - 6px); opacity: 0; } }

/* ---------- legend ---------- */
.legend { display: flex; flex-wrap: wrap; gap: 8px 16px; font-size: .8rem; color: #b6c0d1; }
.legend.vertical { flex-direction: column; gap: 8px; }
.legend .dot { display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 7px; vertical-align: -1px; }

/* ---------- callouts ---------- */
.callout {
  display: flex; gap: 14px; align-items: flex-start; padding: 14px 18px; border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--accent) 35%, transparent);
  background: color-mix(in srgb, var(--accent) 8%, var(--surface-solid));
}
.callout .ci {
  flex: none; width: 30px; height: 30px; border-radius: 9px; display: grid; place-items: center; font-weight: 800;
  color: var(--accent); background: color-mix(in srgb, var(--accent) 16%, transparent);
}
.callout .ct { font-weight: 700; color: var(--text); font-size: .98rem; }
.callout .cd { color: #a8b3c7; font-size: .9rem; margin-top: 2px; line-height: 1.5; }

/* ---------- explanation card (walkthroughs) ---------- */
.explain { border-radius: 16px; border: 1px solid var(--line); background: var(--surface); padding: 18px 20px; }
.explain .pill {
  display: inline-block; font-family: 'JetBrains Mono', monospace; font-size: .72rem; font-weight: 700; color: var(--violet);
  background: rgba(167, 139, 250, .12); border: 1px solid rgba(167, 139, 250, .3); padding: 3px 9px; border-radius: 999px;
}
.explain .et { font-family: 'Space Grotesk', sans-serif; font-size: 1.3rem; font-weight: 700; color: var(--text); margin: 10px 0 6px; }
.explain .ed { color: #a8b3c7; font-size: .92rem; line-height: 1.55; }
.explain .ed code, .explain .formula {
  font-family: 'JetBrains Mono', monospace; font-size: .8rem; color: var(--cyan); background: rgba(34, 211, 238, .07);
  padding: 2px 6px; border-radius: 6px;
}
.explain .formula { display: block; padding: 10px 12px; margin-top: 12px; border: 1px solid rgba(34, 211, 238, .18); }
.explain .rows-title { font-size: .7rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); font-weight: 700; margin: 16px 0 8px; }
.explain .row {
  display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; border-radius: 10px;
  background: rgba(255, 255, 255, .025); border: 1px solid var(--line); margin-bottom: 6px; font-size: .88rem; color: #cbd5e1;
}
.explain .row b { font-family: 'JetBrains Mono', monospace; color: var(--text); }
.explain .row .chg { font-family: 'JetBrains Mono', monospace; color: var(--green); font-weight: 700; }
.explain .empty { color: var(--muted); font-size: .86rem; font-style: italic; }

/* ---------- algorithm profile cards ---------- */
.algo { border-radius: 18px; border: 1px solid var(--line); background: var(--surface); overflow: hidden; height: 100%; }
.algo .top { padding: 18px 20px; background: linear-gradient(135deg, color-mix(in srgb, var(--accent) 20%, transparent), transparent); border-bottom: 1px solid var(--line); }
.algo .top .n { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.35rem; color: var(--text); }
.algo .top .t { color: var(--accent); font-size: .8rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin-top: 2px; }
.algo .kv { display: flex; justify-content: space-between; gap: 16px; padding: 11px 20px; border-bottom: 1px solid var(--line); font-size: .9rem; }
.algo .kv:last-child { border-bottom: none; }
.algo .kv span { color: var(--muted); }
.algo .kv b { color: var(--text); text-align: right; font-weight: 600; }

/* ---------- streamlit widgets ---------- */
[role="tablist"] {
  gap: 4px; padding: 6px; border-radius: 14px; border: 1px solid var(--line); background: var(--surface);
  width: fit-content; max-width: 100%; flex-wrap: wrap;
}
[data-testid="stTab"] {
  height: 40px; padding: 0 14px; border-radius: 10px; background: transparent; color: var(--muted);
  transition: background .2s ease, color .2s ease; display: flex; align-items: center;
}
[data-testid="stTab"] p { font-weight: 600; font-size: .93rem; }
[data-testid="stTab"]:hover { background: rgba(148, 163, 184, .08); color: var(--text); }
[data-testid="stTab"][aria-selected="true"] {
  background: linear-gradient(135deg, var(--cyan), var(--indigo)); color: #041019;
  box-shadow: 0 6px 22px rgba(34, 211, 238, .25);
}
[data-testid="stTab"][aria-selected="true"] * { color: #041019 !important; }
[role="tabpanel"] { padding-top: 1.6rem; }

[class*="st-key-card"] {
  background: var(--surface); border-color: var(--line) !important; border-radius: 18px !important;
  box-shadow: 0 10px 30px rgba(0, 0, 0, .25);
}

[data-testid="stExpander"] details { border-radius: 14px; border-color: var(--line); background: var(--surface); }
[data-testid="stExpander"] summary p { font-weight: 600; }

[data-testid="stBaseButton-primary"] {
  background: linear-gradient(135deg, var(--cyan), var(--indigo)); color: #041019; border: none; font-weight: 700;
  box-shadow: 0 6px 20px rgba(34, 211, 238, .22);
}
[data-testid="stBaseButton-primary"]:hover { filter: brightness(1.08); color: #041019; }
[data-testid="stBaseButton-primary"] p { font-weight: 700; }

[data-testid="stDataFrame"], [data-testid="stDataEditor"] { border-radius: 12px; overflow: hidden; }
[data-testid="stWidgetLabel"] p { font-weight: 600; color: #b6c0d1; }
</style>
"""

ICON_LOGO = """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#041019" stroke-width="2.2"
stroke-linecap="round"><circle cx="5" cy="6" r="2.4"/><circle cx="19" cy="6" r="2.4"/><circle cx="12" cy="18" r="2.4"/>
<path d="M7.2 7.2 10.6 16M16.8 7.2 13.4 16M7.4 6h9.2"/></svg>"""


def svg_url(svg):
    """st.html removes inline <svg> and <img>, so SVG artwork is used as a CSS background."""
    data = base64.b64encode(svg.encode("utf-8")).decode()
    return f"url('data:image/svg+xml;base64,{data}')"


SVG_ANIM = """<style>
.flow { stroke-dasharray: 7 9; animation: flow 1.1s linear infinite; }
@keyframes flow { to { stroke-dashoffset: -32; } }
.halo { animation: breathe 2.6s ease-in-out infinite; transform-box: fill-box; transform-origin: center; }
@keyframes breathe { 50% { transform: scale(1.4); opacity: .04; } }
</style>"""


def inject_css():
    art = (f"<style>.hero-art {{ background: {hero_svg()} center/contain no-repeat; }}"
           f".brand .logo .mark {{ width: 22px; height: 22px; background: {svg_url(ICON_LOGO)} center/contain no-repeat; }}</style>")
    st.html(CSS + art)


def brand():
    st.html(f"""
    <div class="brand">
      <div class="logo"><div class="mark"></div></div>
      <div><div class="name">RouteLab</div><div class="sub">Shortest-path optimizer</div></div>
    </div>""")


def side_label(text):
    st.html(f"<div class='side-label'>{text}</div>")


def cheat_sheet():
    st.html("""
    <div class="cheat">
      <div class="item"><b>Dijkstra</b><span>One source → all routers · Greedy · <code>O(V²)</code></span></div>
      <div class="item"><b>Floyd–Warshall</b><span>Every pair of routers · Dynamic programming · <code>O(V³)</code></span></div>
      <div class="item"><b>Graph model</b><span>Router = node · Link = edge · Cost = weight</span></div>
    </div>
    <div class="side-foot">Built with Python · NumPy · pandas · Plotly · Streamlit</div>""")


def hero_svg():
    # small decorative network, the amber route is animated with CSS
    nodes = [(30, 140), (100, 60), (110, 160), (190, 100), (250, 30), (260, 165), (315, 90)]
    links = [(0, 2), (1, 2), (2, 3), (1, 4), (3, 4), (3, 5), (2, 5), (4, 6), (5, 6)]
    route = [(0, 1), (1, 3), (3, 6)]
    lines = "".join(
        f"<line x1='{nodes[a][0]}' y1='{nodes[a][1]}' x2='{nodes[b][0]}' y2='{nodes[b][1]}' "
        f"stroke='rgba(148,163,184,.35)' stroke-width='1.5'/>" for a, b in links)
    glow = "".join(
        f"<line x1='{nodes[a][0]}' y1='{nodes[a][1]}' x2='{nodes[b][0]}' y2='{nodes[b][1]}' "
        f"stroke='rgba(251,191,36,.18)' stroke-width='12' stroke-linecap='round'/>"
        f"<line class='flow' x1='{nodes[a][0]}' y1='{nodes[a][1]}' x2='{nodes[b][0]}' y2='{nodes[b][1]}' "
        f"stroke='#fbbf24' stroke-width='2.5' stroke-linecap='round'/>" for a, b in route)
    colors = {0: "#34d399", 1: "#fbbf24", 3: "#fbbf24", 6: "#fb7185"}
    dots = ""
    for i, (x, y) in enumerate(nodes):
        c = colors.get(i, "#22d3ee")
        filled = i in colors
        dots += (f"<circle class='halo' cx='{x}' cy='{y}' r='15' fill='{c}' opacity='.16'/>"
                 f"<circle cx='{x}' cy='{y}' r='8.5' fill='{c if filled else '#0d1424'}' stroke='{c}' stroke-width='2'/>")
    return svg_url("<svg xmlns='http://www.w3.org/2000/svg' width='340' height='190' viewBox='0 0 340 190'>"
                   f"{SVG_ANIM}{lines}{glow}{dots}</svg>")


def hero():
    st.html(f"""
    <div class="hero">
      <div class="hero-text">
        <span class="badge"><span class="live"></span>Python Lab Project · Graph Algorithms</span>
        <div class="hero-title">Network Routing &amp; <span class="grad">Shortest&nbsp;Path</span> Optimization</div>
        <div class="hero-sub">A computer network modelled as a weighted graph: routers are <b>nodes</b>,
          links are <b>edges</b> and link cost is the <b>weight</b>. Find optimal routes with
          <b>Dijkstra</b> (single source) and <b>Floyd–Warshall</b> (all pairs).</div>
        <div class="stack"><span>numpy</span><span>pandas</span><span>plotly</span><span>streamlit</span></div>
      </div>
      <div class="hero-art">
        <div class="packet"></div>
      </div>
    </div>""")


def section(eyebrow, title, desc=""):
    st.html(f"""
    <div class="section">
      <div class="eyebrow">{eyebrow}</div>
      <div class="title">{title}</div>
      <div class="desc">{desc}</div>
    </div>""")


def kpis(cards):
    """cards = list of (icon, label, value, hint, accent_color)"""
    html = "".join(
        f"""<div class="kpi" style="--accent:{accent}">
              <div class="label"><span class="ico">{icon}</span>{label}</div>
              <div class="value">{value}</div>
              <div class="hint">{hint}</div>
            </div>""" for icon, label, value, hint, accent in cards)
    st.html(f"<div class='kpis'>{html}</div>")


def route(path, hop_costs, total, tag="Optimal route", compact=False):
    """Draw a path like  A —2— C —1— B  with the cost of every hop."""
    parts = []
    for k, name in enumerate(path):
        cls = "src" if k == 0 else "dst" if k == len(path) - 1 else ""
        parts.append(f"<div class='hop {cls}'>{name}</div>")
        if k < len(hop_costs):
            parts.append(f"<div class='wire'><i>{hop_costs[k]:g}</i></div>")
    st.html(f"""
    <div class="route {'compact' if compact else ''}">
      <div class="head"><span class="tag">{tag}</span>
        <span class="total">{len(path) - 1} hops · total cost <b>{total}</b></span></div>
      <div class="path">{''.join(parts)}</div>
    </div>""")


LEGEND_ITEMS = [("#34d399", "Source"), ("#fb7185", "Destination"), ("#fbbf24", "Shortest path"),
                ("#a78bfa", "Current (walkthrough)"), ("#22d3ee", "Visited / router")]


def legend(vertical=False, items=None):
    items = items or LEGEND_ITEMS
    html = "".join(f"<span><span class='dot' style='background:{c}'></span>{t}</span>" for c, t in items)
    st.html(f"<div class='legend {'vertical' if vertical else ''}'>{html}</div>")


CALLOUT = {"info": ("#22d3ee", "i"), "ok": ("#34d399", "✓"), "warn": ("#fbbf24", "!"), "danger": ("#fb7185", "✕")}


def callout(kind, title, text=""):
    color, icon = CALLOUT[kind]
    st.html(f"""
    <div class="callout" style="--accent:{color}">
      <div class="ci">{icon}</div>
      <div><div class="ct">{title}</div><div class="cd">{text}</div></div>
    </div>""")


def explain(pill, title, text, rows_title="", rows=None, empty="", formula=""):
    """Card used by the step-by-step walkthroughs. rows = list of (left, right)."""
    rows_html = ""
    if rows_title:
        if rows:
            rows_html = "".join(f"<div class='row'><b>{a}</b><span class='chg'>{b}</span></div>" for a, b in rows)
        else:
            rows_html = f"<div class='empty'>{empty}</div>"
        rows_html = f"<div class='rows-title'>{rows_title}</div>{rows_html}"
    formula_html = f"<code class='formula'>{formula}</code>" if formula else ""
    st.html(f"""
    <div class="explain">
      <span class="pill">{pill}</span>
      <div class="et">{title}</div>
      <div class="ed">{text}</div>
      {formula_html}
      {rows_html}
    </div>""")


def algo_card(name, tag, accent, rows):
    kv = "".join(f"<div class='kv'><span>{k}</span><b>{v}</b></div>" for k, v in rows)
    st.html(f"""
    <div class="algo" style="--accent:{accent}">
      <div class="top"><div class="n">{name}</div><div class="t">{tag}</div></div>
      {kv}
    </div>""")
