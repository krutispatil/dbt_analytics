import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64

st.set_page_config(
    page_title="E-Commerce Analytics Platform",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #080c14;
    color: #e2e8f0;
}
.main { background-color: #080c14; }
.block-container { padding: 1.5rem 2.5rem 4rem; max-width: 1400px; }

/* ── Global project header ── */
.global-header {
    padding: 1.1rem 0 1.4rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid #1e2d45;
}
.global-title {
    font-size: 1.75rem;
    font-weight: 600;
    color: #f8fafc;
    letter-spacing: -0.02em;
    margin: 0 0 0.55rem;
    line-height: 1.2;
}
.global-desc {
    font-size: 0.85rem;
    color: #64748b;
    margin: 0;
    line-height: 1.75;
    max-width: 920px;
}
.global-desc .hl  { color: #6366f1; font-weight: 500; }
.global-desc .arr { color: #1e2d45; margin: 0 5px; font-size: 0.75rem; }

/* ── Page header ── */
.page-header { margin-bottom: 1.5rem; }
.page-title {
    font-size: 1.3rem;
    font-weight: 600;
    color: #f8fafc;
    letter-spacing: -0.02em;
    margin: 0 0 0.25rem;
    line-height: 1.2;
}
.page-subtitle { font-size: 0.8rem; color: #475569; margin: 0; }

/* ── KPI boxes ── */
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 1.75rem; }
.kpi-box {
    background: #0f1623;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    height: 108px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-sizing: border-box;
}
.kpi-label { font-size: 0.68rem; font-weight: 500; color: #475569; text-transform: uppercase; letter-spacing: 0.09em; }
.kpi-value { font-size: 1.65rem; font-weight: 600; color: #f8fafc; font-family: 'JetBrains Mono', monospace; letter-spacing: -0.02em; line-height: 1; }
.kpi-delta { font-size: 0.7rem; font-weight: 400; }
.kpi-delta.green { color: #4ade80; }
.kpi-delta.warn  { color: #fb923c; }
.kpi-delta.neutral { color: #475569; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #0a0f1a !important; border-right: 1px solid #1e2d45 !important; }
[data-testid="stSidebar"] * { color: #94a3b8 !important; }
div[data-testid="stRadio"] > div { gap: 4px; }
div[data-testid="stRadio"] label {
    background: transparent !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 9px 14px !important;
    font-size: 0.83rem !important;
    cursor: pointer;
    color: #64748b !important;
}
div[data-testid="stRadio"] label:hover { background: #0f1623 !important; color: #e2e8f0 !important; }
div[data-testid="stRadio"] label[data-checked="true"] {
    background: #0f1623 !important;
    color: #6366f1 !important;
    border-left: 2px solid #6366f1 !important;
}
.sidebar-project-title { font-size: 0.78rem; font-weight: 600; color: #f8fafc; letter-spacing: 0.01em; line-height: 1.4; margin-bottom: 0.25rem; }
.sidebar-project-sub { font-size: 0.68rem; color: #334155; margin-bottom: 1.5rem; line-height: 1.4; }
.sidebar-nav-label { font-size: 0.65rem; font-weight: 500; color: #334155; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.5rem; padding-left: 2px; }
.sidebar-divider { border: none; border-top: 1px solid #1e2d45; margin: 1.25rem 0; }
.sidebar-stat-block { margin-bottom: 1.25rem; }
.sidebar-stat-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #0f1623; }
.sidebar-stat-label { font-size: 0.7rem; color: #334155; }
.sidebar-stat-value { font-size: 0.7rem; color: #6366f1; font-weight: 500; font-family: 'JetBrains Mono', monospace; }
.sidebar-tech-row { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 0.75rem; }
.sidebar-tech-pill { font-size: 0.65rem; font-weight: 500; padding: 3px 9px; border-radius: 20px; border: 1px solid #1e2d45; color: #475569; background: #0f1623; }
.sidebar-footer { font-size: 0.65rem; color: #1e2d45; text-align: center; margin-top: 1rem; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter, sans-serif", size=12),
    margin=dict(l=48, r=24, t=12, b=48),
    xaxis=dict(showgrid=False, zeroline=False, showline=True,
               linecolor="#1e2d45", title_text="",
               tickfont=dict(size=12, color="#94a3b8")),
    yaxis=dict(showgrid=False, zeroline=False, showline=True,
               linecolor="#1e2d45", title_text="",
               tickfont=dict(size=12, color="#94a3b8")),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2d45", font=dict(size=11)),
    coloraxis_colorbar=dict(title_text="", tickfont=dict(size=11, color="#94a3b8")),
)

C = {
    "indigo": "#6366f1", "green": "#4ade80",
    "amber": "#fb923c",  "red": "#f87171",
    "cyan": "#22d3ee",   "slate": "#475569",
}

@st.cache_resource
def get_conn():
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    return duckdb.connect(f"md:olist?motherduck_token={token}")

@st.cache_data(ttl=3600)
def load(query):
    return get_conn().execute(query).df()

@st.cache_data(ttl=3600)
def load_all():
    sales     = load("SELECT * FROM dbt_kpatil.mart_sales WHERE order_month IS NOT NULL ORDER BY order_month")
    customers = load("SELECT * FROM dbt_kpatil.mart_customers")
    sellers   = load("SELECT * FROM dbt_kpatil.mart_sellers ORDER BY total_revenue DESC")
    delivery  = load("SELECT * FROM dbt_kpatil.mart_delivery WHERE order_month IS NOT NULL ORDER BY order_month")
    reviews   = load("SELECT review_score, COUNT(*) as cnt FROM olist.main.raw_reviews GROUP BY review_score ORDER BY review_score")
    payments  = load("SELECT payment_type, SUM(payment_value) as total, COUNT(*) as cnt FROM olist.main.raw_payments GROUP BY payment_type ORDER BY total DESC")
    return sales, customers, sellers, delivery, reviews, payments

def kpi(label, value, delta="", cls="neutral"):
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta {cls}">{delta}&nbsp;</div>
    </div>""", unsafe_allow_html=True)

def chart(title, insight, fig, key, height=300, left_margin=48):
    fig.update_layout(height=height)
    lyt = {**CHART_LAYOUT}
    lyt["margin"] = dict(l=left_margin, r=24, t=12, b=48)
    fig.update_layout(**lyt)
    fig.update_xaxes(title_text="", showgrid=False, zeroline=False,
                     tickfont=dict(size=12, color="#94a3b8"))
    fig.update_yaxes(title_text="", showgrid=False, zeroline=False,
                     tickfont=dict(size=12, color="#94a3b8"))
    img_bytes = fig.to_image(format="png", width=700, height=height, scale=2)
    img_b64 = base64.b64encode(img_bytes).decode()
    st.markdown(f"""
    <div style="background:#0f1623;border:1px solid #1e2d45;border-radius:10px;
                padding:1rem 1.5rem 1rem;margin-bottom:20px;">
        <div style="font-size:0.72rem;font-weight:500;color:#64748b;
                    text-transform:uppercase;letter-spacing:0.09em;margin-bottom:0.4rem;">
            {title}</div>
        <div style="font-size:0.78rem;color:#475569;line-height:1.55;
                    padding:0.5rem 0.75rem;background:#080c14;border-radius:6px;
                    border-left:2px solid #1e2d45;margin-bottom:0.85rem;">
            {insight}</div>
        <img src="data:image/png;base64,{img_b64}"
             style="width:100%;border-radius:6px;display:block;" />
    </div>""", unsafe_allow_html=True)

# ── Load all data once ────────────────────────────────────────────────────────
with st.spinner("Loading data..."):
    sales, customers, sellers, delivery, reviews, payments = load_all()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-project-title">End-to-End E-Commerce<br>Analytics Platform</div>
    <div class="sidebar-project-sub">dbt · MotherDuck · Streamlit</div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sidebar-nav-label">Navigation</div>', unsafe_allow_html=True)
    page = st.radio("nav", ["Overview", "Revenue", "Customers", "Sellers", "Delivery"],
                    label_visibility="collapsed")
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-nav-label">Project Stats</div>
    <div class="sidebar-stat-block">
        <div class="sidebar-stat-row"><span class="sidebar-stat-label">Dataset</span><span class="sidebar-stat-value">Olist 2016–2018</span></div>
        <div class="sidebar-stat-row"><span class="sidebar-stat-label">Orders</span><span class="sidebar-stat-value">100,245</span></div>
        <div class="sidebar-stat-row"><span class="sidebar-stat-label">dbt Models</span><span class="sidebar-stat-value">15 models</span></div>
        <div class="sidebar-stat-row"><span class="sidebar-stat-label">Data Tests</span><span class="sidebar-stat-value">44 passing</span></div>
        <div class="sidebar-stat-row"><span class="sidebar-stat-label">Architecture</span><span class="sidebar-stat-value">ELT · 4 layers</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-nav-label">Tech Stack</div>
    <div class="sidebar-tech-row">
        <span class="sidebar-tech-pill">dbt Core</span>
        <span class="sidebar-tech-pill">MotherDuck</span>
        <span class="sidebar-tech-pill">DuckDB</span>
        <span class="sidebar-tech-pill">Streamlit</span>
        <span class="sidebar-tech-pill">Python</span>
        <span class="sidebar-tech-pill">Plotly</span>
        <span class="sidebar-tech-pill">GitHub</span>
    </div>
    <div class="sidebar-footer">github.com/krutispatil/dbt_analytics</div>
    """, unsafe_allow_html=True)

# ── Global header (shown on every page) ──────────────────────────────────────
st.markdown("""
<div class="global-header">
    <div class="global-title">End-to-End E-Commerce Analytics Platform</div>
    <div class="global-desc">
        100,245 orders from the <span class="hl">Olist Brazilian marketplace (2016–2018)</span>
        are ingested into <span class="hl">MotherDuck</span> as raw CSV tables, then transformed
        through a production-grade <span class="hl">ELT pipeline</span> authored in
        <span class="hl">dbt Core</span> across four modular layers —
        <span class="hl">Staging</span> (type casting, deduplication, null handling)
        <span class="arr">→</span>
        <span class="hl">Intermediate</span> (multi-table joins, business logic, customer segmentation)
        <span class="arr">→</span>
        <span class="hl">Marts</span> (aggregated, analytics-ready tables for revenue, customers, sellers, and delivery)
        — validated by <span class="hl">44 automated dbt tests</span>, all passing,
        and served live through this <span class="hl">Streamlit</span> dashboard.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Overview ──────────────────────────────────────────────────────────────────
if page == "Overview":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Platform Overview</div>
        <div class="page-subtitle">High-level KPIs across the entire Olist marketplace — revenue, customers, sellers, and delivery</div>
    </div>""", unsafe_allow_html=True)

    try:
        sales["order_month"] = pd.to_datetime(sales["order_month"])
        total_gmv       = sales["total_revenue"].sum()
        total_orders    = sales["total_orders"].sum()
        total_customers = len(customers)
        total_sellers   = len(sellers)
        avg_review      = sellers["avg_review_score"].mean()
        avg_ontime      = delivery.groupby("order_month").apply(
            lambda x: (x["on_time_deliveries"].sum() / x["delivered_orders"].sum() * 100)
        ).mean()
        canceled        = sales["canceled_orders"].sum()
        cancel_rate     = canceled / total_orders * 100

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi("Total GMV", f"R${total_gmv:,.0f}", "Gross merchandise value · Brazilian Real", "neutral")
        with c2: kpi("Total Orders", f"{total_orders:,}", f"Cancellation rate: {cancel_rate:.1f}%", "neutral")
        with c3: kpi("Unique Customers", f"{total_customers:,}", "Individuals who placed orders", "neutral")
        with c4: kpi("Active Sellers", f"{total_sellers:,}", f"Avg review: {avg_review:.2f}/5", "neutral")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c5,c6,c7,c8 = st.columns(4)
        repeat_loyal = len(customers[customers["customer_segment"].isin(["repeat","loyal"])])
        with c5: kpi("Avg Order Value", f"R${total_gmv/total_orders:,.0f}", "Revenue per order · Brazilian Real", "neutral")
        with c6: kpi("On-Time Delivery", f"{avg_ontime:.1f}%", "% orders delivered on time", "green" if avg_ontime>=80 else "warn")
        with c7: kpi("Repeat + Loyal", f"{repeat_loyal/total_customers*100:.1f}%", "Customers who came back", "green")
        with c8: kpi("Avg Health Score", f"{sellers['seller_health_score'].mean():.1f}/100", "Composite seller score", "neutral")
        st.markdown('</div>', unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        with col1:
            m = sales.groupby("order_month")["total_revenue"].sum().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=m["order_month"], y=m["total_revenue"],
                mode="lines+markers",
                line=dict(color=C["indigo"], width=2),
                marker=dict(size=4),
                fill="tozeroy", fillcolor="rgba(99,102,241,0.07)"
            ))
            chart("GMV Over Time",
                  "Monthly revenue across the entire platform. Strong growth through 2017 with peak in Nov 2017 (Black Friday), followed by stabilization.",
                  fig, "ov1")
        with col2:
            seg = customers["customer_segment"].value_counts().reset_index()
            seg.columns = ["segment","count"]
            fig2 = px.pie(seg, values="count", names="segment", hole=0.55,
                         color_discrete_sequence=[C["indigo"], C["green"], C["amber"]],
                         labels={"segment":"","count":""})
            fig2.update_traces(textfont_size=12)
            fig2.update_xaxes(showline=False)
            fig2.update_yaxes(showline=False)
            chart("Customer Segment Mix",
                  "Majority of customers are one-time buyers — a key retention challenge. Growing the repeat and loyal share is the highest-leverage growth lever.",
                  fig2, "ov2")

        col3,col4 = st.columns(2)
        with col3:
            pay = payments.copy()
            pay["payment_type"] = pay["payment_type"].str.replace("_"," ").str.title()
            fig3 = px.bar(pay, x="payment_type", y="cnt",
                         color_discrete_sequence=[C["cyan"]],
                         labels={"payment_type":"","cnt":""})
            chart("Payment Method Mix",
                  "Credit card dominates Brazilian e-commerce. Boleto (bank slip) is a cash-equivalent popular with unbanked customers — important for market reach.",
                  fig3, "ov3")
        with col4:
            rev = reviews.copy()
            rev["review_score"] = rev["review_score"].astype(str)
            colors = ["#f87171","#fb923c","#fbbf24","#a3e635","#4ade80"]
            fig4 = px.bar(rev, x="review_score", y="cnt",
                         color="review_score",
                         color_discrete_sequence=colors,
                         labels={"review_score":"","cnt":""})
            fig4.update_layout(showlegend=False)
            chart("Review Score Distribution",
                  "Strong skew toward 5-star reviews indicates overall customer satisfaction. High 1-star volume alongside 5-stars suggests a polarized experience worth investigating.",
                  fig4, "ov4")

    except Exception as e:
        st.error(f"Error loading overview: {e}")

# ── Revenue ───────────────────────────────────────────────────────────────────
elif page == "Revenue":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Revenue & Sales</div>
        <div class="page-subtitle">Gross merchandise value, order volume, and category breakdown across all states</div>
    </div>""", unsafe_allow_html=True)

    try:
        sales["order_month"] = pd.to_datetime(sales["order_month"])
        m = sales.groupby("order_month").agg(
            total_revenue=("total_revenue","sum"),
            total_orders=("total_orders","sum"),
        ).reset_index()
        m["aov"] = (m["total_revenue"] / m["total_orders"]).round(2)

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi("Total GMV", f"R${m['total_revenue'].sum():,.0f}", "All orders · Brazilian Real")
        with c2: kpi("Total Orders", f"{m['total_orders'].sum():,}", "Across all states & categories")
        with c3: kpi("Avg Order Value", f"R${m['aov'].mean():,.0f}", "Per order · Brazilian Real")
        with c4: kpi("Peak Month", f"R${m['total_revenue'].max():,.0f}",
                     m.loc[m['total_revenue'].idxmax(),'order_month'].strftime('%b %Y') + " · Brazilian Real", "green")
        st.markdown('</div>', unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=m["order_month"], y=m["total_revenue"],
                mode="lines+markers",
                line=dict(color=C["indigo"], width=2),
                marker=dict(size=4),
                fill="tozeroy", fillcolor="rgba(99,102,241,0.07)"
            ))
            chart("Monthly GMV Trend",
                  "Total revenue each month. A rising trend signals healthy growth; sharp dips may reflect seasonal slowdowns or fulfillment issues.",
                  fig, "r1")
        with col2:
            fig2 = go.Figure(go.Bar(
                x=m["order_month"], y=m["total_orders"],
                marker_color=C["indigo"], marker_opacity=0.7
            ))
            chart("Monthly Order Volume",
                  "Number of orders placed each month. Compare with GMV — divergence between the two reveals shifts in average order value.",
                  fig2, "r2")

        col3,col4 = st.columns(2)
        with col3:
            top_cats = sales.groupby("category_name_english")["total_revenue"].sum().nlargest(10).reset_index()
            top_cats["category_name_english"] = top_cats["category_name_english"].str.replace("_"," ").str.title()
            fig3 = px.bar(top_cats, x="total_revenue", y="category_name_english",
                         orientation="h",
                         color_discrete_sequence=[C["indigo"]],
                         labels={"total_revenue":"","category_name_english":""})
            chart("Top 10 Categories by Revenue",
                  "Highest-earning product categories overall. These categories deserve priority in inventory planning and promotional spend.",
                  fig3, "r3", left_margin=160)
        with col4:
            state_rev = sales.groupby("customer_state")["total_revenue"].sum().reset_index().sort_values("total_revenue", ascending=False).head(15)
            fig4 = px.bar(state_rev, x="customer_state", y="total_revenue",
                         color_discrete_sequence=[C["cyan"]],
                         labels={"customer_state":"","total_revenue":""})
            chart("Revenue by State",
                  "Geographic spread of revenue. SP and RJ dominate as Brazil's largest consumer markets — other states signal expansion opportunities.",
                  fig4, "r4")

        col5,col6 = st.columns(2)
        with col5:
            cancel = sales.groupby("order_month").agg(
                total=("total_orders","sum"),
                canceled=("canceled_orders","sum")
            ).reset_index()
            cancel["cancel_rate"] = (cancel["canceled"] / cancel["total"] * 100).round(2)
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(
                x=cancel["order_month"], y=cancel["cancel_rate"],
                mode="lines+markers",
                line=dict(color=C["red"], width=2),
                fill="tozeroy", fillcolor="rgba(248,113,113,0.07)"
            ))
            chart("Cancellation Rate Trend",
                  "% of orders canceled each month. Spikes may indicate stockout issues, payment failures, or seller fulfillment problems worth investigating.",
                  fig5, "r5")
        with col6:
            pay = payments.copy()
            pay["payment_type"] = pay["payment_type"].str.replace("_"," ").str.title()
            fig6 = px.bar(pay, x="payment_type", y="total",
                         color_discrete_sequence=[C["amber"]],
                         labels={"payment_type":"","total":""})
            chart("Payment Method by GMV",
                  "Revenue split by payment method. Credit card dominates; boleto (bank slip) serves unbanked customers — both are critical for market coverage in Brazil.",
                  fig6, "r6")

    except Exception as e:
        st.error(f"Error loading revenue data: {e}")

# ── Customers ─────────────────────────────────────────────────────────────────
elif page == "Customers":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Customer Analytics</div>
        <div class="page-subtitle">Lifetime value, segmentation, and purchasing behaviour across the customer base</div>
    </div>""", unsafe_allow_html=True)

    try:
        total    = len(customers)
        one_time = len(customers[customers["customer_segment"]=="one_time"])
        repeat   = len(customers[customers["customer_segment"]=="repeat"])
        loyal    = len(customers[customers["customer_segment"]=="loyal"])
        avg_ltv  = customers["lifetime_revenue"].mean()

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi("Total Customers", f"{total:,}", "Unique individuals")
        with c2: kpi("One-time", f"{one_time:,}", f"{one_time/total*100:.1f}% bought only once", "warn")
        with c3: kpi("Repeat + Loyal", f"{repeat+loyal:,}", f"{(repeat+loyal)/total*100:.1f}% returned", "green")
        with c4: kpi("Avg LTV", f"R${avg_ltv:,.0f}", "Avg spend per customer · Brazilian Real")
        st.markdown('</div>', unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        with col1:
            seg = customers["customer_segment"].value_counts().reset_index()
            seg.columns = ["segment","count"]
            fig = px.pie(seg, values="count", names="segment", hole=0.55,
                        color_discrete_sequence=[C["indigo"], C["green"], C["amber"]],
                        labels={"segment":"","count":""})
            fig.update_traces(textfont_size=12)
            fig.update_xaxes(showline=False)
            fig.update_yaxes(showline=False)
            chart("Customer Segment Mix",
                  "Split of one-time, repeat (2–3 orders), and loyal (4+ orders) buyers. A healthy business grows its repeat and loyal share over time.",
                  fig, "c1")
        with col2:
            fig2 = px.histogram(
                customers[customers["lifetime_revenue"] < customers["lifetime_revenue"].quantile(0.95)],
                x="lifetime_revenue", nbins=50,
                color_discrete_sequence=[C["indigo"]],
                labels={"lifetime_revenue":"","count":""})
            fig2.update_xaxes(showline=True, linecolor="#1e2d45")
            fig2.update_yaxes(showline=False)
            chart("LTV Distribution",
                  "Spread of lifetime spend across all customers (top 5% removed as outliers). Right-skew means most customers spend modestly — a few drive outsized value.",
                  fig2, "c2")

        col3,col4 = st.columns(2)
        with col3:
            fig3 = px.box(customers, x="customer_segment", y="avg_order_value",
                         color="customer_segment",
                         color_discrete_sequence=[C["indigo"], C["green"], C["amber"]],
                         labels={"customer_segment":"","avg_order_value":""})
            fig3.update_xaxes(showline=True, linecolor="#1e2d45",
                               tickfont=dict(size=13, color="#cbd5e1"))
            fig3.update_yaxes(showline=True, linecolor="#1e2d45")
            chart("Avg Order Value by Segment",
                  "Do loyal customers spend more per order? A higher AOV in the loyal segment confirms retention investment pays off through bigger basket sizes.",
                  fig3, "c3")
        with col4:
            fig4 = px.scatter(
                customers[customers["total_orders"]<=10],
                x="total_orders", y="lifetime_revenue",
                color="customer_segment",
                color_discrete_sequence=[C["indigo"], C["green"], C["amber"]],
                opacity=0.55,
                labels={"total_orders":"","lifetime_revenue":"","customer_segment":"Segment"})
            fig4.update_xaxes(showline=True, linecolor="#1e2d45", dtick=1)
            fig4.update_yaxes(showline=True, linecolor="#1e2d45")
            chart("Orders vs Lifetime Revenue",
                  "Each dot is a customer. Steep upward clusters confirm more orders reliably predict higher LTV — every repeat purchase compounds total value.",
                  fig4, "c4")

    except Exception as e:
        st.error(f"Error loading customer data: {e}")

# ── Sellers ───────────────────────────────────────────────────────────────────
elif page == "Sellers":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Seller Performance</div>
        <div class="page-subtitle">GMV, review scores, delivery reliability, and composite health scores across all active sellers</div>
    </div>""", unsafe_allow_html=True)

    try:
        avg_health = sellers["seller_health_score"].mean()
        avg_review = sellers["avg_review_score"].mean()

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi("Active Sellers", f"{len(sellers):,}", "Sellers with at least 1 order")
        with c2: kpi("Platform GMV", f"R${sellers['total_revenue'].sum():,.0f}", "Total revenue · Brazilian Real")
        with c3: kpi("Avg Health Score", f"{avg_health:.1f}/100", "Reviews + on-time rate + volume", "green" if avg_health>=60 else "warn")
        with c4: kpi("Avg Review Score", f"{avg_review:.2f}/5", "Customer satisfaction average", "green" if avg_review>=4 else "warn")
        st.markdown('</div>', unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        with col1:
            fig = px.histogram(sellers, x="seller_health_score", nbins=30,
                              color_discrete_sequence=[C["indigo"]],
                              labels={"seller_health_score":"","count":""})
            fig.update_xaxes(showline=True, linecolor="#1e2d45")
            fig.update_yaxes(showline=False)
            chart("Seller Health Score Distribution",
                  "Composite 0–100 score: review rating (40%) + on-time delivery rate (40%) + order volume (20%). Sellers below 50 are flagged as at-risk.",
                  fig, "s1")
        with col2:
            fig2 = px.scatter(sellers, x="avg_review_score", y="total_revenue",
                             size="total_orders", color="on_time_rate",
                             color_continuous_scale=["#f87171","#fb923c","#4ade80"],
                             hover_data=["seller_id","seller_state"], opacity=0.65,
                             labels={"avg_review_score":"","total_revenue":"",
                                     "on_time_rate":"On-time %","total_orders":"Orders"})
            fig2.update_xaxes(showline=True, linecolor="#1e2d45")
            fig2.update_yaxes(showline=True, linecolor="#1e2d45")
            chart("Review Score vs GMV",
                  "Bubble size = order volume, color = on-time delivery rate. High-revenue sellers with low scores are a reputation risk that needs account management.",
                  fig2, "s2")

        fig3 = px.bar(sellers.head(20), x="seller_id", y="total_revenue",
                     color="seller_health_score",
                     color_continuous_scale=["#f87171","#fb923c","#4ade80"],
                     labels={"seller_id":"","total_revenue":"","seller_health_score":"Health Score"})
        fig3.update_xaxes(tickangle=45, tickfont=dict(size=9, color="#94a3b8"),
                           showline=True, linecolor="#1e2d45")
        fig3.update_yaxes(showline=False)
        chart("Top 20 Sellers by GMV",
              "Highest-revenue sellers colored by health score. Red bars with high GMV are high-risk — strong revenue but poor service quality threatens long-term retention.",
              fig3, "s3", height=340)

    except Exception as e:
        st.error(f"Error loading seller data: {e}")

# ── Delivery ──────────────────────────────────────────────────────────────────
elif page == "Delivery":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Delivery SLA</div>
        <div class="page-subtitle">On-time delivery rates, average transit times, and late delivery patterns by month and state</div>
    </div>""", unsafe_allow_html=True)

    try:
        delivery["order_month"] = pd.to_datetime(delivery["order_month"])
        md = delivery.groupby("order_month").agg(
            delivered_orders=("delivered_orders","sum"),
            on_time_deliveries=("on_time_deliveries","sum"),
            avg_days=("avg_days_to_deliver","mean"),
            late_deliveries=("late_deliveries","sum")
        ).reset_index()
        md["on_time_rate"] = (md["on_time_deliveries"]/md["delivered_orders"]*100).round(1)

        avg_ontime  = md["on_time_rate"].mean()
        avg_days    = md["avg_days"].mean()
        total_late  = int(md["late_deliveries"].sum())
        total_deliv = int(md["delivered_orders"].sum())

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1,c2,c3,c4 = st.columns(4)
        with c1: kpi("Avg On-Time Rate", f"{avg_ontime:.1f}%", "% delivered before estimated date", "green" if avg_ontime>=80 else "warn")
        with c2: kpi("Avg Days to Deliver", f"{avg_days:.1f} days", "Order placed → customer received")
        with c3: kpi("Total Delivered", f"{total_deliv:,}", "Successfully fulfilled orders", "green")
        with c4: kpi("Late Deliveries", f"{total_late:,}", f"{total_late/total_deliv*100:.1f}% of all deliveries", "warn")
        st.markdown('</div>', unsafe_allow_html=True)

        col1,col2 = st.columns(2)
        with col1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=md["order_month"], y=md["on_time_rate"],
                mode="lines+markers",
                line=dict(color=C["green"], width=2),
                fill="tozeroy", fillcolor="rgba(74,222,128,0.07)"
            ))
            fig.add_hline(y=80, line_dash="dash", line_color=C["amber"],
                          annotation_text="80% target", annotation_font_color=C["amber"])
            chart("Monthly On-Time Delivery Rate",
                  "Percentage of orders delivered on or before the estimated date. Months below the 80% dashed line indicate SLA breaches requiring logistics review.",
                  fig, "d1")
        with col2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=md["order_month"], y=md["avg_days"],
                mode="lines+markers",
                line=dict(color=C["amber"], width=2),
                marker=dict(size=4)
            ))
            chart("Avg Days to Deliver Over Time",
                  "Average calendar days from order placement to delivery. A rising trend may signal carrier capacity issues or shift toward more distant locations.",
                  fig2, "d2")

        state_del = delivery.groupby("customer_state").agg(
            on_time_deliveries=("on_time_deliveries","sum"),
            delivered_orders=("delivered_orders","sum"),
            avg_days=("avg_days_to_deliver","mean")
        ).reset_index()
        state_del["on_time_rate"] = (state_del["on_time_deliveries"]/state_del["delivered_orders"]*100).round(1)
        fig3 = px.bar(state_del.sort_values("on_time_rate", ascending=False),
                     x="customer_state", y="on_time_rate",
                     color="avg_days",
                     color_continuous_scale=["#4ade80","#fb923c","#f87171"],
                     labels={"customer_state":"","on_time_rate":"","avg_days":"Avg Days"})
        fig3.add_hline(y=80, line_dash="dash", line_color=C["amber"],
                       annotation_text="80% target", annotation_font_color=C["amber"])
        fig3.update_xaxes(showline=True, linecolor="#1e2d45")
        fig3.update_yaxes(showline=False)
        chart("On-Time Rate by State",
              "States ranked by on-time delivery rate, colored by avg days to deliver. Red states below 80% are the highest-priority logistics problem areas.",
              fig3, "d3", height=340)

    except Exception as e:
        st.error(f"Error loading delivery data: {e}")