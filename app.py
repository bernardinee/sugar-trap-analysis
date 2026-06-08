import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

st.set_page_config(
    page_title="Sugar Trap · Helix CPG",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;1,9..40,300&display=swap');

:root {
  --bg:         #0E0F11;
  --surface:    #161719;
  --surface2:   #1E2024;
  --border:     #2A2D32;
  --gold:       #C9A84C;
  --gold-dim:   #8A6E2F;
  --gold-glow:  rgba(201,168,76,0.12);
  --text:       #E8E4DC;
  --text-dim:   #7A7670;
  --text-mid:   #A8A49C;
  --red:        #D95B3A;
  --green:      #4DAA72;
  --blue:       #4A85C4;
}

html, body, [class*="css"], .stApp {
  background-color: var(--bg) !important;
  font-family: 'DM Sans', sans-serif;
  color: var(--text);
}
[data-testid="stSidebar"] {
  background-color: var(--surface) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebar"] label {
  color: var(--text-dim) !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.06em !important;
  text-transform: uppercase !important;
}
.block-container { padding: 2rem 2.5rem 3rem 2.5rem !important; max-width: 100% !important; }
#MainMenu, footer, header { visibility: hidden; }
h1, h2, h3 { font-family: 'DM Serif Display', serif !important; }

.kpi-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: 2px solid var(--gold);
  padding: 1.4rem 1.6rem 1.2rem;
  position: relative;
  overflow: hidden;
}
.kpi-wrap::after {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 60px;
  background: var(--gold-glow);
  pointer-events: none;
}
.kpi-label  { font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--text-dim); margin-bottom: 0.5rem; font-weight: 500; }
.kpi-value  { font-family: 'DM Serif Display', serif; font-size: 2.4rem; color: var(--text); line-height: 1; margin-bottom: 0.3rem; }
.kpi-delta  { font-size: 0.82rem; color: var(--green); }
.kpi-unit   { font-size: 0.82rem; color: var(--text-dim); margin-left: 2px; }

.section-label { font-size: 0.7rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--gold); font-weight: 500; margin-bottom: 0.3rem; }
.section-title { font-family: 'DM Serif Display', serif; font-size: 1.75rem; color: var(--text); line-height: 1.2; margin-bottom: 0.35rem; }
.section-sub   { font-size: 0.88rem; color: var(--text-dim); font-style: italic; margin-bottom: 1.4rem; }
.divider       { border: none; border-top: 1px solid var(--border); margin: 2.5rem 0; }

.insight-card    { background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--gold); padding: 1.6rem 2rem; margin: 1.5rem 0; }
.insight-eyebrow { font-size: 0.68rem; letter-spacing: 0.16em; text-transform: uppercase; color: var(--gold); margin-bottom: 0.8rem; font-weight: 500; }
.insight-body    { font-size: 1.05rem; line-height: 1.75; color: var(--text-mid); }
.insight-body strong { color: var(--text); font-weight: 500; }

.method-card  { background: var(--surface2); border: 1px solid var(--border); padding: 1.2rem 1.4rem; }
.method-title { font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-dim); margin-bottom: 1rem; font-weight: 500; }
.method-row   { display: flex; justify-content: space-between; align-items: baseline; padding: 0.5rem 0; border-bottom: 1px solid var(--border); font-size: 0.88rem; }
.method-row:last-child { border-bottom: none; }
.method-name   { color: var(--text-mid); }
.method-weight { color: var(--gold); font-weight: 500; font-family: 'DM Serif Display', serif; font-size: 1rem; }

.top3-bar   { background: var(--surface); border: 1px solid var(--border); border-top: 2px solid var(--green); padding: 1.2rem 1.6rem; display: flex; align-items: center; gap: 2rem; margin-top: 1rem; }
.top3-label { font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--text-dim); font-weight: 500; white-space: nowrap; }
.top3-items { display: flex; gap: 1rem; flex-wrap: wrap; }
.top3-pill  { background: rgba(77,170,114,0.12); border: 1px solid rgba(77,170,114,0.3); color: var(--green); padding: 0.3rem 0.9rem; font-size: 0.85rem; font-weight: 500; }

.page-header  { border-bottom: 1px solid var(--border); padding-bottom: 1.5rem; margin-bottom: 2rem; }
.page-eyebrow { font-size: 0.7rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--gold-dim); margin-bottom: 0.5rem; font-weight: 500; }
.page-title   { font-family: 'DM Serif Display', serif; font-size: 2.6rem; color: var(--text); line-height: 1.1; margin-bottom: 0.5rem; }
.page-title em { color: var(--gold); font-style: italic; }
.page-desc    { font-size: 0.95rem; color: var(--text-dim); max-width: 600px; line-height: 1.6; }

.sidebar-brand { font-family: 'DM Serif Display', serif; font-size: 1.15rem; color: var(--text) !important; letter-spacing: 0.01em; margin-bottom: 0.2rem; }
.sidebar-sub   { font-size: 0.72rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--gold-dim) !important; margin-bottom: 0; }

[data-testid="metric-container"] { background: transparent !important; border: none !important; padding: 0 !important; }
[data-testid="stMultiSelect"] span[data-baseweb="tag"] { background-color: var(--gold-glow) !important; border: 1px solid var(--gold-dim) !important; color: var(--gold) !important; }
[data-testid="stAlert"] { background: rgba(77,170,114,0.08) !important; border: 1px solid rgba(77,170,114,0.25) !important; border-radius: 0 !important; color: var(--green) !important; }
</style>
""", unsafe_allow_html=True)


CATEGORY_COLORS = {
    "Chocolate & Candy":     "#C4503A",
    "Biscuits & Cookies":    "#C9883A",
    "Chips & Crisps":        "#B8A43A",
    "Bars & Granola":        "#4DAA72",
    "Nuts & Seeds":          "#4A85C4",
    "Dairy Snacks":          "#8A6EC4",
    "Fruit & Veggie Snacks": "#C45A8A",
    "Other Snacks":          "#5A5E66",
}

SUGAR_THRESHOLD   = 15
PROTEIN_THRESHOLD = 10
PLOT_BG    = "#161719"
PAPER_BG   = "#161719"
GRID_COLOR = "#2A2D32"
FONT_COLOR = "#7A7670"
TEXT_COLOR = "#E8E4DC"


@st.cache_data(show_spinner="Initialising...")
def load_data():
    df  = pd.read_csv("sugar_trap_clean_data.csv", low_memory=False)
    opp = pd.read_csv("opportunity_scores.csv", index_col=0)
    return df, opp

df, opp_df = load_data()


# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-brand">Sugar Trap</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Helix CPG Partners</p>', unsafe_allow_html=True)
    st.markdown("---")
    all_categories = sorted(df["primary_category"].unique().tolist())
    selected_cats  = st.multiselect("CATEGORIES", options=all_categories, default=all_categories)
    st.markdown("---")
    sugar_max   = st.slider("MAX SUGAR g/100g",   0, 100, 100, 5)
    protein_min = st.slider("MIN PROTEIN g/100g", 0,  50,   0, 2)
    st.markdown("---")
    sample_size = st.slider("SAMPLE SIZE / CATEGORY", 100, 800, 400, 100)
    st.markdown("---")
    st.markdown('<p style="font-size:0.7rem;letter-spacing:0.08em;color:#3A3D42;">SOURCE: OPEN FOOD FACTS<br>HELIX CPG PARTNERS · 2024</p>', unsafe_allow_html=True)


# ── Filter ────────────────────────────────────────────────
df_filtered = df[
    (df["primary_category"].isin(selected_cats)) &
    (df["sugars_100g"]   <= sugar_max) &
    (df["proteins_100g"] >= protein_min)
].copy()

blue_ocean = df_filtered[
    (df_filtered["proteins_100g"] >= PROTEIN_THRESHOLD) &
    (df_filtered["sugars_100g"]   <= SUGAR_THRESHOLD)
]
pct_bo = len(blue_ocean) / max(len(df_filtered), 1) * 100


# ── Header ────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <div class="page-eyebrow">Market Intelligence · Snack Category Analysis</div>
  <div class="page-title">The <em>Sugar Trap</em></div>
  <div class="page-desc">Mapping the whitespace between consumer health demand and current product supply — where is the Blue Ocean in the snack aisle?</div>
</div>
""", unsafe_allow_html=True)


# ── KPIs ──────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="kpi-wrap"><div class="kpi-label">Products Analysed</div><div class="kpi-value">{len(df_filtered):,}</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="kpi-wrap"><div class="kpi-label">In Blue Ocean Quadrant</div><div class="kpi-value">{len(blue_ocean):,}</div><div class="kpi-delta">↑ {pct_bo:.1f}% of selection</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="kpi-wrap"><div class="kpi-label">Avg Sugar</div><div class="kpi-value">{df_filtered["sugars_100g"].mean():.1f}<span class="kpi-unit">g/100g</span></div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="kpi-wrap"><div class="kpi-label">Avg Protein</div><div class="kpi-value">{df_filtered["proteins_100g"].mean():.1f}<span class="kpi-unit">g/100g</span></div></div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── Scatter — built with go.Scatter to avoid px.scatter hover bug ──
st.markdown('<div class="section-label">Section 01</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Nutrient Matrix</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Sugar (x) vs. Protein (y) — each point is one product. Click legend entries to isolate categories.</div>', unsafe_allow_html=True)

df_plot = (
    df_filtered
    .groupby("primary_category", group_keys=False)
    .apply(lambda x: x.sample(min(len(x), sample_size), random_state=42))
    .copy()
    .reset_index(drop=True)
)

fig_scatter = go.Figure()

for cat, color in CATEGORY_COLORS.items():
    subset = df_plot[df_plot["primary_category"] == cat]
    if subset.empty:
        continue
    fig_scatter.add_trace(go.Scatter(
        x=subset["sugars_100g"],
        y=subset["proteins_100g"],
        mode="markers",
        name=cat,
        marker=dict(color=color, size=6, opacity=0.7, line=dict(width=0)),
        customdata=subset[["product_name", "sugars_100g", "proteins_100g", "fat_100g", "fiber_100g"]].values,
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Sugar: %{customdata[1]:.1f}g<br>"
            "Protein: %{customdata[2]:.1f}g<br>"
            "Fat: %{customdata[3]:.1f}g<br>"
            "Fiber: %{customdata[4]:.1f}g"
            "<extra></extra>"
        ),
    ))

fig_scatter.add_vline(x=SUGAR_THRESHOLD,   line_dash="dot", line_color="#C9A84C", line_width=1)
fig_scatter.add_hline(y=PROTEIN_THRESHOLD, line_dash="dot", line_color="#C9A84C", line_width=1)
fig_scatter.add_shape(
    type="rect", x0=0, x1=SUGAR_THRESHOLD, y0=PROTEIN_THRESHOLD, y1=70,
    fillcolor="rgba(201,168,76,0.06)",
    line=dict(color="#C9A84C", width=0.5, dash="dot"),
    layer="below",
)
fig_scatter.add_annotation(
    x=7.5, y=56,
    text="<b>BLUE OCEAN</b><br>High Protein · Low Sugar",
    showarrow=False,
    font=dict(size=10.5, color="#C9A84C", family="DM Sans"),
    bgcolor="rgba(14,15,17,0.85)",
    bordercolor="#C9A84C",
    borderwidth=1,
    borderpad=8,
)
fig_scatter.update_layout(
    xaxis=dict(range=[-1,65], gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR,
               title="Sugar (g/100g)", title_font=dict(color=FONT_COLOR, size=11),
               tickfont=dict(color=FONT_COLOR, size=10)),
    yaxis=dict(range=[-1,70], gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR,
               title="Protein (g/100g)", title_font=dict(color=FONT_COLOR, size=11),
               tickfont=dict(color=FONT_COLOR, size=10)),
    legend=dict(title=dict(text="CATEGORY", font=dict(size=10, color=FONT_COLOR)),
                font=dict(size=10, color=TEXT_COLOR),
                bgcolor="rgba(22,23,25,0.9)", bordercolor=GRID_COLOR, borderwidth=1),
    margin=dict(l=60, r=40, t=20, b=60),
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PAPER_BG,
    height=580,
)
st.plotly_chart(fig_scatter, use_container_width=True)


# ── Insight ───────────────────────────────────────────────
if len(opp_df) > 0:
    best_cat = opp_df.iloc[0]["Category"]
    bo_cat   = df[
        (df["primary_category"] == best_cat) &
        (df["proteins_100g"]    >= PROTEIN_THRESHOLD) &
        (df["sugars_100g"]      <= SUGAR_THRESHOLD)
    ]
    target_p = bo_cat["proteins_100g"].median() if len(bo_cat) > 0 else PROTEIN_THRESHOLD
    target_s = bo_cat["sugars_100g"].median()   if len(bo_cat) > 0 else SUGAR_THRESHOLD
    st.markdown(f"""
    <div class="insight-card">
      <div class="insight-eyebrow">◈ Key Finding</div>
      <div class="insight-body">
        The biggest market opportunity is in <strong>{best_cat}</strong> —
        specifically products with <strong>~{target_p:.0f}g protein</strong> and
        <strong>under {target_s:.0f}g sugar</strong> per 100g.
        Only <strong>{len(bo_cat):,} products</strong> currently occupy this quadrant,
        against hundreds of high-sugar alternatives. The supply gap is structural and actionable.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── Scorecard ─────────────────────────────────────────────
st.markdown('<div class="section-label">Section 02</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Opportunity Scorecard</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Categories ranked by composite investment priority score.</div>', unsafe_allow_html=True)

cats_s     = opp_df["Category"].tolist()
scores_s   = opp_df["Opportunity Score"].tolist()
top_cat    = cats_s[0]
bar_colors = ["#C9A84C" if c == top_cat else "#2A2D32" for c in cats_s]
txt_colors = ["#C9A84C" if c == top_cat else "#7A7670" for c in cats_s]

fig_lollipop = go.Figure()
for i, (cat, score) in enumerate(zip(cats_s, scores_s)):
    fig_lollipop.add_shape(type="line", x0=0, x1=score, y0=i, y1=i,
                            line=dict(color=bar_colors[i], width=1.5))
fig_lollipop.add_trace(go.Scatter(
    x=scores_s, y=cats_s,
    mode="markers+text",
    marker=dict(size=14,
                color=["#C9A84C" if c == top_cat else "#1E2024" for c in cats_s],
                line=dict(color=["#C9A84C" if c == top_cat else "#4A4D52" for c in cats_s], width=1.5)),
    text=[f"  {s:.2f}" for s in scores_s],
    textposition="middle right",
    textfont=dict(size=11, color=txt_colors, family="DM Sans"),
    hovertemplate="%{y}: %{x:.3f}<extra></extra>",
))
fig_lollipop.update_layout(
    xaxis=dict(title="Opportunity Score", range=[0,1.25], showgrid=True, gridcolor=GRID_COLOR,
               zeroline=False, title_font=dict(color=FONT_COLOR, size=10),
               tickfont=dict(color=FONT_COLOR, size=10)),
    yaxis=dict(autorange="reversed", tickfont=dict(size=11, color=TEXT_COLOR), showgrid=False),
    showlegend=False,
    margin=dict(l=10, r=100, t=10, b=40),
    plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
    height=360,
)
fig_lollipop.add_annotation(x=scores_s[0]+0.01, y=0, text="  #1", showarrow=False,
                              font=dict(size=10, color="#C9A84C"), xanchor="left")

chart_col, method_col = st.columns([3, 1])
with chart_col:
    st.plotly_chart(fig_lollipop, use_container_width=True)
with method_col:
    st.markdown("""
    <div class="method-card">
      <div class="method-title">Scoring Methodology</div>
      <div class="method-row"><span class="method-name">Gap Size</span><span class="method-weight">50%</span></div>
      <div class="method-row"><span class="method-name">Demand Proxy</span><span class="method-weight">30%</span></div>
      <div class="method-row"><span class="method-name">Market Size</span><span class="method-weight">20%</span></div>
    </div>
    """, unsafe_allow_html=True)

st.dataframe(
    opp_df[["Category","Total Products","Blue Ocean Count","Gap %","Opportunity Score"]]
    .style.background_gradient(subset=["Opportunity Score"], cmap="YlOrBr")
    .format({"Opportunity Score":"{:.3f}","Gap %":"{:.1f}%"}),
    use_container_width=True,
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── Protein sources ───────────────────────────────────────
st.markdown('<div class="section-label">Section 03 · Bonus</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Protein Sources</div>', unsafe_allow_html=True)
st.markdown('<div class="section-sub">Ingredients most common in high-protein / low-sugar products — R&D intelligence.</div>', unsafe_allow_html=True)

PROTEIN_KEYWORDS = [
    "whey","peanut","soy","soya","almond","cashew",
    "protein","egg","milk protein","casein","hemp",
    "pea protein","sunflower seed","chia","quinoa",
]

hp_products = df[
    (df["proteins_100g"] >= PROTEIN_THRESHOLD) &
    (df["sugars_100g"]   <= SUGAR_THRESHOLD) &
    (df["ingredients_text"].notna())
].copy()

keyword_counts = Counter()
for ingredients in hp_products["ingredients_text"].str.lower():
    for kw in PROTEIN_KEYWORDS:
        if kw in str(ingredients):
            keyword_counts[kw] += 1

top_ingr    = keyword_counts.most_common(8)
ingr_labels = [k.title() for k, _ in top_ingr]
ingr_vals   = [v for _, v in top_ingr]
bar_opacities = [1.0 if i < 3 else 0.4 for i in range(len(ingr_vals))]
bar_col_list  = [f"rgba(201,168,76,{o})" for o in bar_opacities]

fig_ingr = go.Figure(go.Bar(
    x=ingr_labels, y=ingr_vals,
    marker=dict(color=bar_col_list, line=dict(width=0)),
    text=[f"{v:,}" for v in ingr_vals],
    textposition="outside",
    textfont=dict(color=FONT_COLOR, size=10),
    hovertemplate="%{x}: %{y:,} products<extra></extra>",
))
fig_ingr.update_layout(
    xaxis=dict(tickfont=dict(color=TEXT_COLOR, size=11), showgrid=False, zeroline=False),
    yaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR, size=10),
               zeroline=False, title="Products", title_font=dict(color=FONT_COLOR, size=10)),
    margin=dict(l=50, r=30, t=20, b=40),
    plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
    height=340, bargap=0.35,
)
st.plotly_chart(fig_ingr, use_container_width=True)

if top_ingr:
    top3  = [k.title() for k, _ in top_ingr[:3]]
    pills = "".join([f'<span class="top3-pill">{p}</span>' for p in top3])
    st.markdown(f'<div class="top3-bar"><span class="top3-label">Top 3 Sources</span><div class="top3-items">{pills}</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<p style="font-size:0.72rem;letter-spacing:0.08em;color:#3A3D42;text-align:center;">HELIX CPG PARTNERS · DATA: OPEN FOOD FACTS · BUILT WITH STREAMLIT</p>', unsafe_allow_html=True)
