import streamlit as st
import pandas as pd
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
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --bg:       #F7F5F0;
  --white:    #FFFFFF;
  --surface:  #EFECE5;
  --border:   #DDD9CF;
  --border2:  #C8C4BA;
  --ink:      #1C1B18;
  --ink-mid:  #4A4844;
  --ink-dim:  #8A8680;
  --gold:     #B8860B;
  --gold-lt:  #F5EDD5;
  --green:    #2D6A4F;
  --green-lt: #D8EFE4;
  --red:      #9B2226;
}

html, body, .stApp, [class*="css"] {
  background-color: var(--bg) !important;
  font-family: 'IBM Plex Sans', sans-serif;
  color: var(--ink);
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* Sidebar */
[data-testid="stSidebar"] {
  background-color: var(--white) !important;
  border-right: 1px solid var(--border) !important;
  padding: 0 !important;
}
[data-testid="stSidebar"] > div { padding: 2rem 1.5rem !important; }
[data-testid="stSidebar"] * { color: var(--ink) !important; font-family: 'IBM Plex Sans', sans-serif !important; }
[data-testid="stSidebar"] label {
  font-size: 0.7rem !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--ink-dim) !important;
  font-weight: 500 !important;
}
[data-testid="stSidebar"] .stSlider [data-testid="stThumbValue"] { color: var(--gold) !important; }

/* Multiselect */
[data-testid="stMultiSelect"] span[data-baseweb="tag"] {
  background-color: var(--gold-lt) !important;
  border: 1px solid var(--gold) !important;
  color: var(--gold) !important;
  font-size: 0.75rem !important;
  border-radius: 2px !important;
}

/* Metric override */
[data-testid="metric-container"] { background: transparent !important; border: none !important; padding: 0 !important; }

/* Dataframe */
[data-testid="stDataFrame"] iframe { border: 1px solid var(--border) !important; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────
CATEGORY_COLORS = {
    "Chocolate & Candy":     "#8B3A2A",
    "Biscuits & Cookies":    "#A0622A",
    "Chips & Crisps":        "#8A7A1A",
    "Bars & Granola":        "#2D6A4F",
    "Nuts & Seeds":          "#1A5276",
    "Dairy Snacks":          "#5B2C6F",
    "Fruit & Veggie Snacks": "#922B5E",
    "Other Snacks":          "#555250",
}

SUGAR_THRESHOLD   = 15
PROTEIN_THRESHOLD = 10
PLOT_BG    = "#FFFFFF"
PAPER_BG   = "#FFFFFF"
GRID_COLOR = "#EDEAE3"
FONT_COLOR = "#8A8680"
TEXT_COLOR = "#1C1B18"

# ── Data ──────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading...")
def load_data():
    df  = pd.read_csv("sugar_trap_clean_data.csv", low_memory=False)
    opp = pd.read_csv("opportunity_scores.csv", index_col=0)
    return df, opp

df, opp_df = load_data()

# ── Sidebar ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="margin-bottom:1.5rem;">
      <div style="font-family:'Playfair Display',serif;font-size:1.3rem;color:#1C1B18;font-weight:600;">Sugar Trap</div>
      <div style="font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#B8860B;margin-top:2px;">Helix CPG Partners</div>
    </div>
    """, unsafe_allow_html=True)

    all_cats = sorted(df["primary_category"].unique().tolist())
    selected_cats = st.multiselect("Categories", options=all_cats, default=all_cats)
    st.markdown("<div style='margin:0.8rem 0;border-top:1px solid #DDD9CF;'></div>", unsafe_allow_html=True)
    sugar_max   = st.slider("Max Sugar  g/100g",   0, 100, 100, 5)
    protein_min = st.slider("Min Protein  g/100g", 0,  50,   0, 2)
    st.markdown("<div style='margin:0.8rem 0;border-top:1px solid #DDD9CF;'></div>", unsafe_allow_html=True)
    sample_size = st.slider("Sample size / category", 100, 800, 400, 100)
    st.markdown("<div style='margin:0.8rem 0;border-top:1px solid #DDD9CF;'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.68rem;letter-spacing:0.08em;color:#C8C4BA;line-height:1.6;'>SOURCE<br>Open Food Facts<br>openfoodfacts.org</div>", unsafe_allow_html=True)

# ── Filter data ───────────────────────────────────────────
mask = (
    df["primary_category"].isin(selected_cats) &
    (df["sugars_100g"]   <= sugar_max) &
    (df["proteins_100g"] >= protein_min)
)
df_filtered = df[mask].copy().reset_index(drop=True)

blue_ocean = df_filtered[
    (df_filtered["proteins_100g"] >= PROTEIN_THRESHOLD) &
    (df_filtered["sugars_100g"]   <= SUGAR_THRESHOLD)
].copy().reset_index(drop=True)

pct_bo = len(blue_ocean) / max(len(df_filtered), 1) * 100

# ── Sample for scatter — done BEFORE loop, no groupby ─────
pieces = []
for cat in selected_cats:
    chunk = df_filtered[df_filtered["primary_category"] == cat]
    if len(chunk) == 0:
        continue
    n = min(len(chunk), sample_size)
    pieces.append(chunk.sample(n=n, random_state=42))
df_plot = pd.concat(pieces, ignore_index=True) if pieces else df_filtered.head(0)

# ── Main layout wrapper ───────────────────────────────────
st.markdown("""
<div style="padding:2.5rem 3rem 0 3rem;">
  <div style="font-size:0.68rem;letter-spacing:0.18em;text-transform:uppercase;color:#B8860B;margin-bottom:0.4rem;font-weight:500;">
    Market Intelligence · Snack Category Analysis
  </div>
  <div style="font-family:'Playfair Display',serif;font-size:2.8rem;color:#1C1B18;line-height:1.1;margin-bottom:0.6rem;">
    The <em style="color:#B8860B;">Sugar Trap</em>
  </div>
  <div style="font-size:0.92rem;color:#8A8680;max-width:580px;line-height:1.65;margin-bottom:2rem;">
    Mapping the whitespace between consumer health demand and current product supply —
    where is the Blue Ocean in the snack aisle?
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPI row ───────────────────────────────────────────────
st.markdown("<div style='padding:0 3rem;'>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

def kpi(col, label, value, sub=None, sub_color="#2D6A4F"):
    with col:
        sub_html = f'<div style="font-size:0.8rem;color:{sub_color};margin-top:4px;">{sub}</div>' if sub else ""
        st.markdown(f"""
        <div style="background:#fff;border:1px solid #DDD9CF;border-top:2px solid #B8860B;padding:1.3rem 1.5rem 1.1rem;">
          <div style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#8A8680;margin-bottom:0.5rem;">{label}</div>
          <div style="font-family:'Playfair Display',serif;font-size:2.2rem;color:#1C1B18;line-height:1;">{value}</div>
          {sub_html}
        </div>""", unsafe_allow_html=True)

kpi(k1, "Products Analysed",     f"{len(df_filtered):,}")
kpi(k2, "In Blue Ocean Quadrant",f"{len(blue_ocean):,}",  sub=f"↑ {pct_bo:.1f}% of selection")
kpi(k3, "Avg Sugar",             f"{df_filtered['sugars_100g'].mean():.1f}<span style='font-size:0.9rem;color:#8A8680;'>g/100g</span>")
kpi(k4, "Avg Protein",           f"{df_filtered['proteins_100g'].mean():.1f}<span style='font-size:0.9rem;color:#8A8680;'>g/100g</span>")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='margin:2rem 3rem;border-top:1px solid #DDD9CF;'></div>", unsafe_allow_html=True)

# ── Section 01: Scatter ───────────────────────────────────
st.markdown("""
<div style="padding:0 3rem;">
  <div style="font-size:0.68rem;letter-spacing:0.16em;text-transform:uppercase;color:#B8860B;font-weight:500;margin-bottom:0.3rem;">Section 01</div>
  <div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:#1C1B18;margin-bottom:0.3rem;">Nutrient Matrix</div>
  <div style="font-size:0.85rem;color:#8A8680;font-style:italic;margin-bottom:1rem;">Sugar (x) vs. Protein (y) — each point is one product. Click legend entries to isolate categories.</div>
</div>
""", unsafe_allow_html=True)

with st.container():
    fig = go.Figure()

    for cat, color in CATEGORY_COLORS.items():
        if cat not in selected_cats:
            continue
        sub = df_plot[df_plot["primary_category"] == cat].reset_index(drop=True)
        if sub.empty:
            continue
        fig.add_trace(go.Scatter(
            x=sub["sugars_100g"].tolist(),
            y=sub["proteins_100g"].tolist(),
            mode="markers",
            name=cat,
            marker=dict(color=color, size=5, opacity=0.65, line=dict(width=0)),
            customdata=sub[["product_name","sugars_100g","proteins_100g","fat_100g","fiber_100g"]].values.tolist(),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Sugar: %{customdata[1]:.1f}g<br>"
                "Protein: %{customdata[2]:.1f}g<br>"
                "Fat: %{customdata[3]:.1f}g<br>"
                "Fiber: %{customdata[4]:.1f}g"
                "<extra></extra>"
            ),
        ))

    fig.add_vline(x=SUGAR_THRESHOLD,   line_dash="dot", line_color="#B8860B", line_width=1)
    fig.add_hline(y=PROTEIN_THRESHOLD, line_dash="dot", line_color="#B8860B", line_width=1)
    fig.add_shape(type="rect", x0=0, x1=SUGAR_THRESHOLD, y0=PROTEIN_THRESHOLD, y1=70,
                  fillcolor="rgba(184,134,11,0.05)", line=dict(color="#B8860B", width=0.5, dash="dot"), layer="below")
    fig.add_annotation(x=7.5, y=56,
        text="<b>BLUE OCEAN</b><br>High Protein · Low Sugar",
        showarrow=False,
        font=dict(size=10, color="#B8860B", family="IBM Plex Sans"),
        bgcolor="rgba(255,255,255,0.92)",
        bordercolor="#B8860B", borderwidth=1, borderpad=8)

    fig.update_layout(
        xaxis=dict(range=[-1,65], gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR,
                   title="Sugar (g/100g)", title_font=dict(color=FONT_COLOR, size=11, family="IBM Plex Sans"),
                   tickfont=dict(color=FONT_COLOR, size=10)),
        yaxis=dict(range=[-1,70], gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR,
                   title="Protein (g/100g)", title_font=dict(color=FONT_COLOR, size=11, family="IBM Plex Sans"),
                   tickfont=dict(color=FONT_COLOR, size=10)),
        legend=dict(title=dict(text="CATEGORY", font=dict(size=9, color=FONT_COLOR)),
                    font=dict(size=10, color=TEXT_COLOR, family="IBM Plex Sans"),
                    bgcolor="rgba(255,255,255,0.95)", bordercolor="#DDD9CF", borderwidth=1),
        margin=dict(l=60, r=40, t=20, b=60),
        plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
        height=540,
    )

    st.markdown("<div style='padding:0 3rem;'>", unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── Insight box ───────────────────────────────────────────
if len(opp_df) > 0:
    best_cat = opp_df.iloc[0]["Category"]
    bo_cat   = df[
        (df["primary_category"] == best_cat) &
        (df["proteins_100g"]    >= PROTEIN_THRESHOLD) &
        (df["sugars_100g"]      <= SUGAR_THRESHOLD)
    ].copy().reset_index(drop=True)
    target_p = bo_cat["proteins_100g"].median() if len(bo_cat) > 0 else PROTEIN_THRESHOLD
    target_s = bo_cat["sugars_100g"].median()   if len(bo_cat) > 0 else SUGAR_THRESHOLD
    st.markdown(f"""
    <div style="margin:0 3rem 0 3rem;background:#fff;border:1px solid #DDD9CF;border-left:3px solid #B8860B;padding:1.5rem 2rem;">
      <div style="font-size:0.68rem;letter-spacing:0.14em;text-transform:uppercase;color:#B8860B;margin-bottom:0.7rem;font-weight:500;">◈ Key Finding</div>
      <div style="font-size:1rem;line-height:1.75;color:#4A4844;">
        The biggest market opportunity is in <strong style="color:#1C1B18;">{best_cat}</strong> —
        specifically products with <strong style="color:#1C1B18;">~{target_p:.0f}g protein</strong> and
        <strong style="color:#1C1B18;">under {target_s:.0f}g sugar</strong> per 100g.
        Only <strong style="color:#1C1B18;">{len(bo_cat):,} products</strong> currently occupy this quadrant,
        against hundreds of high-sugar alternatives. The supply gap is structural and actionable.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin:2rem 3rem;border-top:1px solid #DDD9CF;'></div>", unsafe_allow_html=True)

# ── Section 02: Scorecard ─────────────────────────────────
st.markdown("""
<div style="padding:0 3rem;">
  <div style="font-size:0.68rem;letter-spacing:0.16em;text-transform:uppercase;color:#B8860B;font-weight:500;margin-bottom:0.3rem;">Section 02</div>
  <div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:#1C1B18;margin-bottom:0.3rem;">Opportunity Scorecard</div>
  <div style="font-size:0.85rem;color:#8A8680;font-style:italic;margin-bottom:1rem;">Categories ranked by composite investment priority score.</div>
</div>
""", unsafe_allow_html=True)

cats_s   = opp_df["Category"].tolist()
scores_s = opp_df["Opportunity Score"].tolist()
top_cat  = cats_s[0]

fig_l = go.Figure()
for i, (cat, score) in enumerate(zip(cats_s, scores_s)):
    clr = "#B8860B" if cat == top_cat else "#C8C4BA"
    fig_l.add_shape(type="line", x0=0, x1=score, y0=i, y1=i,
                    line=dict(color=clr, width=1.5))
fig_l.add_trace(go.Scatter(
    x=scores_s, y=cats_s,
    mode="markers+text",
    marker=dict(size=13,
                color=["#B8860B" if c == top_cat else "#EFECE5" for c in cats_s],
                line=dict(color=["#B8860B" if c == top_cat else "#C8C4BA" for c in cats_s], width=1.5)),
    text=[f"  {s:.2f}" for s in scores_s],
    textposition="middle right",
    textfont=dict(size=11, color=["#B8860B" if c == top_cat else "#8A8680" for c in cats_s], family="IBM Plex Mono"),
    hovertemplate="%{y}: %{x:.3f}<extra></extra>",
))
fig_l.update_layout(
    xaxis=dict(title="Opportunity Score", range=[0, 1.28], showgrid=True, gridcolor=GRID_COLOR,
               zeroline=False, title_font=dict(color=FONT_COLOR, size=10), tickfont=dict(color=FONT_COLOR, size=10)),
    yaxis=dict(autorange="reversed", tickfont=dict(size=11, color=TEXT_COLOR, family="IBM Plex Sans"), showgrid=False),
    showlegend=False,
    margin=dict(l=10, r=110, t=10, b=40),
    plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
    height=340,
)
fig_l.add_annotation(x=scores_s[0]+0.015, y=0, text="#1",
                      showarrow=False, font=dict(size=10, color="#B8860B", family="IBM Plex Mono"), xanchor="left")

st.markdown("<div style='padding:0 3rem;'>", unsafe_allow_html=True)
ch_col, me_col = st.columns([3, 1])
with ch_col:
    st.plotly_chart(fig_l, use_container_width=True)
with me_col:
    st.markdown("""
    <div style="background:#fff;border:1px solid #DDD9CF;padding:1.3rem 1.4rem;margin-top:0.5rem;">
      <div style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#8A8680;margin-bottom:1rem;font-weight:500;">Scoring Method</div>
      <div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #EFECE5;font-size:0.88rem;">
        <span style="color:#4A4844;">Gap Size</span><span style="color:#B8860B;font-weight:600;font-family:'Playfair Display',serif;">50%</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:0.5rem 0;border-bottom:1px solid #EFECE5;font-size:0.88rem;">
        <span style="color:#4A4844;">Demand Proxy</span><span style="color:#B8860B;font-weight:600;font-family:'Playfair Display',serif;">30%</span>
      </div>
      <div style="display:flex;justify-content:space-between;padding:0.5rem 0;font-size:0.88rem;">
        <span style="color:#4A4844;">Market Size</span><span style="color:#B8860B;font-weight:600;font-family:'Playfair Display',serif;">20%</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

st.dataframe(
    opp_df[["Category","Total Products","Blue Ocean Count","Gap %","Opportunity Score"]]
    .style.background_gradient(subset=["Opportunity Score"], cmap="YlOrBr")
    .format({"Opportunity Score":"{:.3f}","Gap %":"{:.1f}%"}),
    use_container_width=True,
)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin:2rem 3rem;border-top:1px solid #DDD9CF;'></div>", unsafe_allow_html=True)

# ── Section 03: Protein sources ───────────────────────────
st.markdown("""
<div style="padding:0 3rem;">
  <div style="font-size:0.68rem;letter-spacing:0.16em;text-transform:uppercase;color:#B8860B;font-weight:500;margin-bottom:0.3rem;">Section 03 · Bonus</div>
  <div style="font-family:'Playfair Display',serif;font-size:1.8rem;color:#1C1B18;margin-bottom:0.3rem;">Protein Sources</div>
  <div style="font-size:0.85rem;color:#8A8680;font-style:italic;margin-bottom:1rem;">Ingredients most common in high-protein / low-sugar products — R&D intelligence.</div>
</div>
""", unsafe_allow_html=True)

PROTEIN_KEYWORDS = [
    "whey","peanut","soy","soya","almond","cashew",
    "protein","egg","milk protein","casein","hemp",
    "pea protein","sunflower seed","chia","quinoa",
]

hp = df[
    (df["proteins_100g"] >= PROTEIN_THRESHOLD) &
    (df["sugars_100g"]   <= SUGAR_THRESHOLD) &
    (df["ingredients_text"].notna())
].copy().reset_index(drop=True)

kw_counts = Counter()
for row in hp["ingredients_text"].str.lower():
    for kw in PROTEIN_KEYWORDS:
        if kw in str(row):
            kw_counts[kw] += 1

top_ingr    = kw_counts.most_common(8)
ingr_labels = [k.title() for k, _ in top_ingr]
ingr_vals   = [v for _, v in top_ingr]
bar_cols    = ["#B8860B" if i < 3 else "#C8C4BA" for i in range(len(ingr_vals))]

fig_b = go.Figure(go.Bar(
    x=ingr_labels, y=ingr_vals,
    marker=dict(color=bar_cols, line=dict(width=0)),
    text=[f"{v:,}" for v in ingr_vals],
    textposition="outside",
    textfont=dict(color=FONT_COLOR, size=10, family="IBM Plex Mono"),
    hovertemplate="%{x}: %{y:,} products<extra></extra>",
))
fig_b.update_layout(
    xaxis=dict(tickfont=dict(color=TEXT_COLOR, size=11, family="IBM Plex Sans"), showgrid=False, zeroline=False),
    yaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(color=FONT_COLOR, size=10), zeroline=False,
               title="Products", title_font=dict(color=FONT_COLOR, size=10)),
    margin=dict(l=50, r=30, t=20, b=40),
    plot_bgcolor=PLOT_BG, paper_bgcolor=PAPER_BG,
    height=320, bargap=0.4,
)

st.markdown("<div style='padding:0 3rem;'>", unsafe_allow_html=True)
st.plotly_chart(fig_b, use_container_width=True)

if top_ingr:
    top3  = [k.title() for k, _ in top_ingr[:3]]
    pills = "".join([f'<span style="background:#D8EFE4;border:1px solid #2D6A4F;color:#2D6A4F;padding:0.3rem 1rem;font-size:0.83rem;font-weight:500;margin-right:0.5rem;">{p}</span>' for p in top3])
    st.markdown(f"""
    <div style="background:#fff;border:1px solid #DDD9CF;border-top:2px solid #2D6A4F;padding:1.1rem 1.5rem;display:flex;align-items:center;gap:1.5rem;margin-bottom:1rem;">
      <span style="font-size:0.68rem;letter-spacing:0.1em;text-transform:uppercase;color:#8A8680;font-weight:500;white-space:nowrap;">Top 3 Sources</span>
      <div>{pills}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div style='margin:2rem 3rem;border-top:1px solid #DDD9CF;'></div>", unsafe_allow_html=True)
st.markdown("<div style='padding:0 3rem 3rem 3rem;font-size:0.7rem;letter-spacing:0.08em;color:#C8C4BA;text-align:center;'>HELIX CPG PARTNERS · DATA: OPEN FOOD FACTS · BUILT WITH STREAMLIT</div>", unsafe_allow_html=True)
