# ============================================================
# SUGAR TRAP MARKET GAP ANALYSIS
# Streamlit Dashboard  (app.py)
# ============================================================
#
# HOW TO RUN LOCALLY:
#   pip install streamlit plotly pandas
#   streamlit run app.py
#
# HOW TO DEPLOY FREE (Streamlit Cloud):
#   1. Push this file + sugar_trap_clean_data.csv + opportunity_scores.csv
#      + requirements.txt to a PUBLIC GitHub repo.
#   2. Go to share.streamlit.io → New App → connect your repo.
#   3. Set "Main file path" to app.py → Deploy.
#
# IMPORTANT: The app.py file must sit in the ROOT of the repo.
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import math

# ──────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Sugar Trap | Helix CPG Partners",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# CUSTOM CSS — clean, consultancy feel
# ──────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }
  .main { background-color: #FAFAF8; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
  h1 { color: #1A1A18; font-weight: 700; letter-spacing: -0.5px; }
  h2 { color: #1A1A18; font-weight: 600; }
  h3 { color: #444441; font-weight: 500; }

  /* KPI cards */
  .kpi-card {
    background: white;
    border-radius: 12px;
    padding: 18px 22px;
    border: 1px solid #E8E6DF;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }
  .kpi-number { font-size: 2rem; font-weight: 700; color: #185FA5; line-height: 1.1; }
  .kpi-label  { font-size: 0.82rem; color: #5F5E5A; margin-top: 4px; }

  /* Insight box */
  .insight-box {
    background: linear-gradient(135deg, #EBF4FD 0%, #EAF9F1 100%);
    border-left: 4px solid #185FA5;
    border-radius: 0 12px 12px 0;
    padding: 20px 24px;
    margin: 16px 0;
    font-size: 1.05rem;
    line-height: 1.65;
    color: #1A1A18;
  }
  .insight-box strong { color: #185FA5; }

  /* Section dividers */
  hr.section { border: none; border-top: 2px solid #E8E6DF; margin: 24px 0; }

  /* Streamlit metric override */
  [data-testid="metric-container"] {
    background: white;
    border: 1px solid #E8E6DF;
    border-radius: 12px;
    padding: 14px 18px;
  }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# DATA LOADING — cached for performance
# ──────────────────────────────────────────────
CATEGORY_COLORS = {
    "Chocolate & Candy":     "#E8593C",
    "Biscuits & Cookies":    "#F2A623",
    "Chips & Crisps":        "#EDD234",
    "Bars & Granola":        "#5DAA67",
    "Nuts & Seeds":          "#3B8BD4",
    "Dairy Snacks":          "#A77DC2",
    "Fruit & Veggie Snacks": "#E76F9A",
    "Other Snacks":          "#B0ADAA",
}

@st.cache_data(show_spinner="Loading dataset...")
def load_data():
    df = pd.read_csv("sugar_trap_clean_data.csv", low_memory=False)
    opp = pd.read_csv("opportunity_scores.csv", index_col=0)
    return df, opp

df, opp_df = load_data()

SUGAR_THRESHOLD   = 15
PROTEIN_THRESHOLD = 10


# ──────────────────────────────────────────────
# SIDEBAR — Filters
# ──────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/60/bullseye.png", width=50)
    st.markdown("## Sugar Trap Analysis")
    st.caption("Helix CPG Partners · Strategic Intelligence")
    st.markdown("---")

    st.markdown("### 🔍 Filters")

    all_categories = sorted(df["primary_category"].unique().tolist())
    selected_cats = st.multiselect(
        "Snack Categories",
        options=all_categories,
        default=all_categories,
        help="Select which categories to display on the scatter plot."
    )

    st.markdown("---")
    sugar_max = st.slider(
        "Max Sugar (g/100g)",
        min_value=0, max_value=100, value=100, step=5,
        help="Filter out products above this sugar level."
    )
    protein_min = st.slider(
        "Min Protein (g/100g)",
        min_value=0, max_value=50, value=0, step=2,
        help="Show only products above this protein level."
    )

    st.markdown("---")
    sample_size = st.slider(
        "Plot Sample Size (per category)",
        min_value=100, max_value=800, value=400, step=100,
        help="More points = slower render but better coverage."
    )

    st.markdown("---")
    st.caption("Data: Open Food Facts (openfoodfacts.org)")
    st.caption("Dashboard: Helix CPG Partners · 2024")


# ──────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────
st.markdown("# 🎯 The Sugar Trap: Market Gap Analysis")
st.markdown("**Where is the Blue Ocean in the snack aisle?** "
            "Mapping the whitespace between consumer health demand "
            "and current product supply.")
st.markdown('<hr class="section">', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# KPI ROW — 4 headline numbers
# ──────────────────────────────────────────────
df_filtered = df[
    (df["primary_category"].isin(selected_cats)) &
    (df["sugars_100g"]   <= sugar_max)           &
    (df["proteins_100g"] >= protein_min)
]

blue_ocean = df_filtered[
    (df_filtered["proteins_100g"] >= PROTEIN_THRESHOLD) &
    (df_filtered["sugars_100g"]   <= SUGAR_THRESHOLD)
]

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.metric("Total Products Analyzed", f"{len(df_filtered):,}")
with kpi2:
    pct_bo = len(blue_ocean) / max(len(df_filtered), 1) * 100
    st.metric("In Blue Ocean Quadrant", f"{len(blue_ocean):,}",
              delta=f"{pct_bo:.1f}% of selection")
with kpi3:
    avg_sugar = df_filtered["sugars_100g"].mean()
    st.metric("Avg Sugar (g/100g)", f"{avg_sugar:.1f}g")
with kpi4:
    avg_protein = df_filtered["proteins_100g"].mean()
    st.metric("Avg Protein (g/100g)", f"{avg_protein:.1f}g")

st.markdown('<hr class="section">', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# MAIN CHART — Nutrient Matrix Scatter Plot
# ──────────────────────────────────────────────
st.markdown("## 📊 Nutrient Matrix: Sugar vs. Protein")
st.caption("Each dot = one product. Hover for details. Use sidebar filters to explore.")

# Sample for performance
df_plot = (
    df_filtered
    .groupby("primary_category", group_keys=False)
    .apply(lambda x: x.sample(min(len(x), sample_size), random_state=42))
    .copy()
)

fig_scatter = px.scatter(
    df_plot,
    x="sugars_100g",
    y="proteins_100g",
    color="primary_category",
    hover_name="product_name",
    hover_data={
        "sugars_100g":   ":.1f",
        "proteins_100g": ":.1f",
        "fat_100g":      ":.1f",
        "fiber_100g":    ":.1f",
        "primary_category": False,
    },
    color_discrete_map=CATEGORY_COLORS,
    opacity=0.65,
    labels={
        "sugars_100g":    "Sugar per 100g (g)",
        "proteins_100g":  "Protein per 100g (g)",
        "primary_category": "Category",
    },
    template="plotly_white",
    height=560,
)

fig_scatter.add_vline(x=SUGAR_THRESHOLD,   line_dash="dash", line_color="#999", line_width=1.2)
fig_scatter.add_hline(y=PROTEIN_THRESHOLD, line_dash="dash", line_color="#999", line_width=1.2)

fig_scatter.add_shape(
    type="rect", x0=0, x1=SUGAR_THRESHOLD, y0=PROTEIN_THRESHOLD, y1=70,
    fillcolor="rgba(59,139,212,0.08)", line_width=0, layer="below"
)
fig_scatter.add_annotation(
    x=7.5, y=52,
    text="<b>🎯 Blue Ocean</b><br>High Protein + Low Sugar",
    showarrow=False,
    font=dict(size=11.5, color="#185FA5"),
    bgcolor="rgba(230,241,251,0.92)",
    bordercolor="#B5D4F4",
    borderwidth=1,
    borderpad=7,
)

fig_scatter.update_layout(
    xaxis_range=[-1, 65],
    yaxis_range=[-1, 70],
    legend_title_text="Category",
    margin=dict(l=60, r=40, t=30, b=60),
    plot_bgcolor="#FAFAF8",
    paper_bgcolor="#FAFAF8",
)

st.plotly_chart(fig_scatter, use_container_width=True)


# ──────────────────────────────────────────────
# KEY INSIGHT BOX
# ──────────────────────────────────────────────
# Dynamically compute best category from current filters
if len(opp_df) > 0:
    best_cat  = opp_df.iloc[0]["Category"]
    best_score = opp_df.iloc[0]["Opportunity Score"]
    bo_cat = df[(df["primary_category"] == best_cat) &
                (df["proteins_100g"] >= PROTEIN_THRESHOLD) &
                (df["sugars_100g"] <= SUGAR_THRESHOLD)]
    target_p = bo_cat["proteins_100g"].median() if len(bo_cat) > 0 else PROTEIN_THRESHOLD
    target_s = bo_cat["sugars_100g"].median()   if len(bo_cat) > 0 else SUGAR_THRESHOLD

    st.markdown(f"""
    <div class="insight-box">
    💡 <strong>Key Insight</strong><br><br>
    Based on the data, the biggest market opportunity is in
    <strong>{best_cat}</strong>, specifically targeting products with
    <strong>~{target_p:.0f}g of protein</strong> and
    <strong>less than {target_s:.0f}g of sugar</strong> per 100g.
    <br><br>
    Only <strong>{len(bo_cat):,}</strong> products currently occupy this
    high-protein/low-sugar quadrant in this category, vs. hundreds of
    sugary alternatives — representing a clear supply gap.
    </div>
    """, unsafe_allow_html=True)

st.markdown('<hr class="section">', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# OPPORTUNITY SCORECARD (Candidate's Choice)
# ──────────────────────────────────────────────
st.markdown("## 🏆 Market Opportunity Scorecard")
st.caption("Candidate's Choice addition — composite score: Gap Size (50%) + Demand Proxy (30%) + Market Size (20%)")

cats_s   = opp_df["Category"].tolist()
scores_s = opp_df["Opportunity Score"].tolist()
top_cat  = cats_s[0]
bar_colors = ["#185FA5" if c == top_cat else "#B5D4F4" for c in cats_s]

fig_lollipop = go.Figure()
for i, (cat, score) in enumerate(zip(cats_s, scores_s)):
    fig_lollipop.add_shape(
        type="line", x0=0, x1=score, y0=i, y1=i,
        line=dict(color=bar_colors[i], width=2.5)
    )
fig_lollipop.add_trace(go.Scatter(
    x=scores_s, y=cats_s,
    mode="markers+text",
    marker=dict(size=15, color=bar_colors, line=dict(color="white", width=2)),
    text=[f"{s:.2f}" for s in scores_s],
    textposition="middle right",
    textfont=dict(size=11, color="#333"),
))
fig_lollipop.update_layout(
    xaxis=dict(title="Opportunity Score (0–1)", range=[0, 1.2],
               showgrid=True, gridcolor="#EEEEEE"),
    yaxis=dict(autorange="reversed", tickfont=dict(size=12)),
    showlegend=False,
    margin=dict(l=190, r=80, t=20, b=50),
    plot_bgcolor="#FAFAF8",
    paper_bgcolor="#FAFAF8",
    template="plotly_white",
    height=380,
)

st.plotly_chart(fig_lollipop, use_container_width=True)

col_tbl, col_exp = st.columns([2, 1])
with col_tbl:
    st.dataframe(
        opp_df[["Category", "Total Products", "Blue Ocean Count",
                "Gap %", "Opportunity Score"]]
        .style.background_gradient(subset=["Opportunity Score"], cmap="Blues"),
        use_container_width=True,
        hide_index=False,
    )
with col_exp:
    st.markdown("**How the score works:**")
    st.markdown("""
    - **Gap % (50%)** — what fraction of this category has NO high-protein/low-sugar options? Higher = more whitespace.
    - **Demand Proxy (30%)** — how protein-rich are the best existing products? Higher = consumers already buying some healthy options.
    - **Market Size (20%)** — log-scaled count of total products. Bigger category = more shelf space to disrupt.
    """)

st.markdown('<hr class="section">', unsafe_allow_html=True)


# ──────────────────────────────────────────────
# BONUS — Protein Source Ingredients
# ──────────────────────────────────────────────
st.markdown("## 🔬 Bonus: What's Driving Protein in Blue Ocean Products?")
st.caption("Top ingredients found in high-protein/low-sugar products — actionable for R&D.")

PROTEIN_KEYWORDS = [
    "whey", "peanut", "soy", "soya", "almond", "cashew",
    "protein", "egg", "milk protein", "casein", "hemp",
    "pea protein", "sunflower seed", "chia", "quinoa",
]

hp_products = df[
    (df["proteins_100g"] >= PROTEIN_THRESHOLD) &
    (df["sugars_100g"]   <= SUGAR_THRESHOLD)   &
    (df["ingredients_text"].notna())
].copy()

from collections import Counter
keyword_counts = Counter()
for ingredients in hp_products["ingredients_text"].str.lower():
    for kw in PROTEIN_KEYWORDS:
        if kw in str(ingredients):
            keyword_counts[kw] += 1

top_ingr = keyword_counts.most_common(8)
ingr_labels = [k.title() for k, _ in top_ingr]
ingr_vals   = [v         for _, v in top_ingr]

fig_ingr = go.Figure(go.Bar(
    x=ingr_labels, y=ingr_vals,
    marker=dict(
        color=ingr_vals,
        colorscale=[[0, "#B5D4F4"], [1, "#0C447C"]],
        showscale=False,
    ),
    text=[f"{v:,}" for v in ingr_vals],
    textposition="outside",
))
fig_ingr.update_layout(
    xaxis_title="Protein Source",
    yaxis_title="Number of Products",
    margin=dict(l=60, r=40, t=20, b=60),
    plot_bgcolor="#FAFAF8",
    paper_bgcolor="#FAFAF8",
    template="plotly_white",
    height=360,
)
st.plotly_chart(fig_ingr, use_container_width=True)

if top_ingr:
    top3 = [k.title() for k, _ in top_ingr[:3]]
    st.success(f"🏅 Top 3 protein sources in high-protein snacks: **{top3[0]}**, **{top3[1]}**, **{top3[2]}**")

st.markdown('<hr class="section">', unsafe_allow_html=True)
st.caption("Dashboard built by Candidate · Data: Open Food Facts · Powered by Streamlit + Plotly")