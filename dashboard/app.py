import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import base64

st.set_page_config(
    page_title="Olist Analytics",
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
.block-container { padding: 2rem 2.5rem 4rem; max-width: 1400px; }

.page-header { margin-bottom: 1.75rem; margin-top: 0.5rem; }
.page-title {
    font-size: 1.5rem;
    font-weight: 600;
    color: #f8fafc;
    letter-spacing: -0.02em;
    margin: 0 0 0.3rem;
    line-height: 1.2;
}
.page-subtitle {
    font-size: 0.82rem;
    color: #475569;
    margin: 0;
    font-weight: 400;
}

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

[data-testid="stSidebar"] { background-color: #0a0f1a !important; border-right: 1px solid #1e2d45 !important; }
[data-testid="stSidebar"] * { color: #94a3b8 !important; }

div[data-testid="stRadio"] > div { gap: 6px; }
div[data-testid="stRadio"] label {
    background: #0f1623 !important;
    border: 1px solid #1e2d45 !important;
    border-radius: 8px !important;
    padding: 8px 14px !important;
    font-size: 0.82rem !important;
    cursor: pointer;
}
div[data-testid="stRadio"] label:hover { border-color: #6366f1 !important; }

.sidebar-meta {
    background: #0f1623;
    border: 1px solid #1e2d45;
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 1.25rem;
    font-size: 0.73rem;
    line-height: 2;
}
.sidebar-meta .ml { color: #475569; }
.sidebar-meta .mv { color: #6366f1; font-weight: 500; }
</style>
""", unsafe_allow_html=True)

# ── Base chart layout ─────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#94a3b8", family="Inter, sans-serif", size=12),
    margin=dict(l=48, r=24, t=12, b=48),
    xaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor="#1e2d45",
        title_text="",
        tickfont=dict(size=12, color="#94a3b8"),
    ),
    yaxis=dict(
        showgrid=False,
        zeroline=False,
        showline=True,
        linecolor="#1e2d45",
        title_text="",
        tickfont=dict(size=12, color="#94a3b8"),
    ),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2d45", font=dict(size=11)),
    coloraxis_colorbar=dict(
        title_text="",
        tickfont=dict(size=11, color="#94a3b8"),
    ),
)

C = {
    "indigo": "#6366f1",
    "green":  "#4ade80",
    "amber":  "#fb923c",
    "red":    "#f87171",
    "cyan":   "#22d3ee",
    "slate":  "#475569",
}

@st.cache_resource
def get_conn():
    token = os.environ.get("MOTHERDUCK_TOKEN", "")
    return duckdb.connect(f"md:olist?motherduck_token={token}")

@st.cache_data(ttl=3600)
def load(query):
    return get_conn().execute(query).df()

def kpi(label, value, delta="", cls="neutral"):
    st.markdown(f"""
    <div class="kpi-box">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-delta {cls}">{delta}&nbsp;</div>
    </div>""", unsafe_allow_html=True)

def chart(title, insight, fig, key, height=300):
    fig.update_layout(height=height)
    fig.update_layout(**CHART_LAYOUT)
    # Clean up axis titles only — do NOT override showline so per-chart settings survive
    fig.update_xaxes(title_text="", showgrid=False, zeroline=False,
                     tickfont=dict(size=12, color="#94a3b8"))
    fig.update_yaxes(title_text="", showgrid=False, zeroline=False,
                     tickfont=dict(size=12, color="#94a3b8"))
    img_bytes = fig.to_image(format="png", width=700, height=height, scale=2)
    img_b64 = base64.b64encode(img_bytes).decode()
    st.markdown(f"""
    <div style="
        background: #0f1623;
        border: 1px solid #1e2d45;
        border-radius: 10px;
        padding: 1rem 1.5rem 1rem;
        margin-bottom: 20px;
    ">
        <div style="font-size:0.72rem;font-weight:500;color:#64748b;
                    text-transform:uppercase;letter-spacing:0.09em;margin-bottom:0.4rem;">
            {title}
        </div>
        <div style="font-size:0.78rem;color:#475569;line-height:1.55;
                    padding:0.5rem 0.75rem;background:#080c14;border-radius:6px;
                    border-left:2px solid #1e2d45;margin-bottom:0.85rem;">
            {insight}
        </div>
        <img src="data:image/png;base64,{img_b64}"
             style="width:100%;border-radius:6px;display:block;" />
    </div>""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:1rem;font-weight:600;color:#f8fafc;margin-bottom:1.25rem;padding-top:0.5rem">Olist Analytics</div>', unsafe_allow_html=True)
    page = st.radio("nav", ["Revenue", "Customers", "Sellers", "Delivery"], label_visibility="collapsed")
    st.markdown("""
    <div class="sidebar-meta">
        <span class="ml">Dataset&nbsp;&nbsp;</span><span class="mv">Olist E-Commerce</span><br>
        <span class="ml">Orders&nbsp;&nbsp;&nbsp;</span><span class="mv">100K · 2016–2018</span><br>
        <span class="ml">Pipeline&nbsp;</span><span class="mv">dbt Core + MotherDuck</span><br>
        <span class="ml">Models&nbsp;&nbsp;</span><span class="mv">15 models · 44 tests</span>
    </div>""", unsafe_allow_html=True)

# ── Revenue ───────────────────────────────────────────────────────────────────
if page == "Revenue":
    st.markdown("""
    <div class="page-header">
        <div class="page-title">Revenue & Sales</div>
        <div class="page-subtitle">Gross merchandise value, order volume, and category breakdown across all states</div>
    </div>""", unsafe_allow_html=True)

    try:
        sales = load("SELECT * FROM dbt_kpatil.mart_sales WHERE order_month IS NOT NULL ORDER BY order_month")
        sales["order_month"] = pd.to_datetime(sales["order_month"])
        m = sales.groupby("order_month").agg(
            total_revenue=("total_revenue", "sum"),
            total_orders=("total_orders", "sum"),
        ).reset_index()
        m["aov"] = (m["total_revenue"] / m["total_orders"]).round(2)

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi("Total GMV", f"R${m['total_revenue'].sum():,.0f}", "All orders · entire period", "neutral")
        with c2: kpi("Total Orders", f"{m['total_orders'].sum():,}", "Across all states & categories", "neutral")
        with c3: kpi("Avg Order Value", f"R${m['aov'].mean():,.0f}", "Revenue per order placed", "neutral")
        with c4: kpi("Peak Month", f"R${m['total_revenue'].max():,.0f}", m.loc[m['total_revenue'].idxmax(), 'order_month'].strftime('%b %Y'), "green")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
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

        col3, col4 = st.columns(2)
        with col3:
            top_cats = sales.groupby("category_name_english")["total_revenue"].sum().nlargest(10).reset_index()
            fig3 = px.bar(
                top_cats, x="total_revenue", y="category_name_english",
                orientation="h",
                color_discrete_sequence=[C["indigo"]],
                labels={"total_revenue": "", "category_name_english": ""},
            )
            chart("Top 10 Categories by Revenue",
                  "Highest-earning product categories overall. These categories deserve priority in inventory planning and promotional spend.",
                  fig3, "r3")

        with col4:
            state_rev = (
                sales.groupby("customer_state")["total_revenue"]
                .sum().reset_index()
                .sort_values("total_revenue", ascending=False)
                .head(15)
            )
            fig4 = px.bar(
                state_rev, x="customer_state", y="total_revenue",
                color_discrete_sequence=[C["cyan"]],
                labels={"customer_state": "", "total_revenue": ""},
            )
            chart("Revenue by State",
                  "Geographic spread of revenue. SP and RJ dominate as Brazil's largest consumer markets — other states signal expansion opportunities.",
                  fig4, "r4")

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
        customers = load("SELECT * FROM dbt_kpatil.mart_customers")
        total    = len(customers)
        one_time = len(customers[customers["customer_segment"] == "one_time"])
        repeat   = len(customers[customers["customer_segment"] == "repeat"])
        loyal    = len(customers[customers["customer_segment"] == "loyal"])
        avg_ltv  = customers["lifetime_revenue"].mean()

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi("Total Customers", f"{total:,}", "Unique individuals", "neutral")
        with c2: kpi("One-time", f"{one_time:,}", f"{one_time/total*100:.1f}% bought only once", "warn")
        with c3: kpi("Repeat + Loyal", f"{repeat+loyal:,}", f"{(repeat+loyal)/total*100:.1f}% returned to buy again", "green")
        with c4: kpi("Avg LTV", f"R${avg_ltv:,.0f}", "Avg total spend per customer", "neutral")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            seg = customers["customer_segment"].value_counts().reset_index()
            seg.columns = ["segment", "count"]
            fig = px.pie(
                seg, values="count", names="segment", hole=0.55,
                color_discrete_sequence=[C["indigo"], C["green"], C["amber"]],
                labels={"segment": "", "count": ""},
            )
            fig.update_traces(textfont_size=12)
            # Pie has no axes — disable showline so it doesn't draw a box
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
                labels={"lifetime_revenue": "", "count": ""},
            )
            # Show baseline only on x for histogram
            fig2.update_xaxes(showline=True, linecolor="#1e2d45")
            fig2.update_yaxes(showline=False)
            chart("LTV Distribution",
                  "Spread of lifetime spend across all customers (top 5% removed as outliers). Right-skew means most customers spend modestly — a few drive outsized value.",
                  fig2, "c2")

        col3, col4 = st.columns(2)
        with col3:
            fig3 = px.box(
                customers, x="customer_segment", y="avg_order_value",
                color="customer_segment",
                color_discrete_sequence=[C["indigo"], C["green"], C["amber"]],
                labels={"customer_segment": "", "avg_order_value": ""},
            )
            # Both axes visible so box positions and values read clearly
            fig3.update_xaxes(showline=True, linecolor="#1e2d45",
                               tickfont=dict(size=13, color="#cbd5e1"))
            fig3.update_yaxes(showline=True, linecolor="#1e2d45",
                               tickfont=dict(size=12, color="#94a3b8"))
            chart("Avg Order Value by Segment",
                  "Do loyal customers spend more per order? A higher AOV in the loyal segment confirms that retention investment pays off through bigger basket sizes.",
                  fig3, "c3")

        with col4:
            fig4 = px.scatter(
                customers[customers["total_orders"] <= 10],
                x="total_orders", y="lifetime_revenue",
                color="customer_segment",
                color_discrete_sequence=[C["indigo"], C["green"], C["amber"]],
                opacity=0.55,
                labels={"total_orders": "", "lifetime_revenue": "", "customer_segment": "Segment"},
            )
            # Integer ticks on x (order counts), baseline on both axes
            fig4.update_xaxes(showline=True, linecolor="#1e2d45", dtick=1,
                               tickfont=dict(size=12, color="#94a3b8"))
            fig4.update_yaxes(showline=True, linecolor="#1e2d45",
                               tickfont=dict(size=12, color="#94a3b8"))
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
        sellers = load("SELECT * FROM dbt_kpatil.mart_sellers ORDER BY total_revenue DESC")
        avg_health = sellers["seller_health_score"].mean()
        avg_review = sellers["avg_review_score"].mean()

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi("Active Sellers", f"{len(sellers):,}", "Sellers with at least 1 order", "neutral")
        with c2: kpi("Platform GMV", f"R${sellers['total_revenue'].sum():,.0f}", "Total seller revenue combined", "neutral")
        with c3: kpi("Avg Health Score", f"{avg_health:.1f}/100", "Reviews + on-time rate + volume", "green" if avg_health >= 60 else "warn")
        with c4: kpi("Avg Review Score", f"{avg_review:.2f}/5", "Customer satisfaction average", "green" if avg_review >= 4 else "warn")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                sellers, x="seller_health_score", nbins=30,
                color_discrete_sequence=[C["indigo"]],
                labels={"seller_health_score": "", "count": ""},
            )
            fig.update_xaxes(showline=True, linecolor="#1e2d45")
            fig.update_yaxes(showline=False)
            chart("Seller Health Score Distribution",
                  "Composite 0–100 score: review rating (40%) + on-time delivery rate (40%) + order volume (20%). Sellers below 50 are flagged as at-risk.",
                  fig, "s1")

        with col2:
            fig2 = px.scatter(
                sellers,
                x="avg_review_score", y="total_revenue",
                size="total_orders", color="on_time_rate",
                color_continuous_scale=["#f87171", "#fb923c", "#4ade80"],
                hover_data=["seller_id", "seller_state"],
                opacity=0.65,
                labels={
                    "avg_review_score": "",
                    "total_revenue": "",
                    "on_time_rate": "On-time %",
                    "total_orders": "Orders",
                },
            )
            fig2.update_xaxes(showline=True, linecolor="#1e2d45")
            fig2.update_yaxes(showline=True, linecolor="#1e2d45")
            chart("Review Score vs GMV",
                  "Bubble size = order volume, color = on-time delivery rate. High-revenue sellers with low scores are a reputation risk that needs account management.",
                  fig2, "s2")

        top20 = sellers.head(20).copy()
        fig3 = px.bar(
            top20, x="seller_id", y="total_revenue",
            color="seller_health_score",
            color_continuous_scale=["#f87171", "#fb923c", "#4ade80"],
            labels={
                "seller_id": "",
                "total_revenue": "",
                "seller_health_score": "Health Score",
            },
        )
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
        delivery = load("SELECT * FROM dbt_kpatil.mart_delivery WHERE order_month IS NOT NULL ORDER BY order_month")
        delivery["order_month"] = pd.to_datetime(delivery["order_month"])

        md = delivery.groupby("order_month").agg(
            delivered_orders=("delivered_orders", "sum"),
            on_time_deliveries=("on_time_deliveries", "sum"),
            avg_days=("avg_days_to_deliver", "mean"),
            late_deliveries=("late_deliveries", "sum")
        ).reset_index()
        md["on_time_rate"] = (md["on_time_deliveries"] / md["delivered_orders"] * 100).round(1)

        avg_ontime  = md["on_time_rate"].mean()
        avg_days    = md["avg_days"].mean()
        total_late  = int(md["late_deliveries"].sum())
        total_deliv = int(md["delivered_orders"].sum())

        st.markdown('<div class="kpi-row">', unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: kpi("Avg On-Time Rate", f"{avg_ontime:.1f}%", "% delivered before estimated date", "green" if avg_ontime >= 80 else "warn")
        with c2: kpi("Avg Days to Deliver", f"{avg_days:.1f} days", "Order placed → customer received", "neutral")
        with c3: kpi("Total Delivered", f"{total_deliv:,}", "Successfully fulfilled orders", "green")
        with c4: kpi("Late Deliveries", f"{total_late:,}", f"{total_late/total_deliv*100:.1f}% of all deliveries", "warn")
        st.markdown('</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
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
                  "Average calendar days from order placement to delivery. A rising trend may signal carrier capacity issues or a shift toward more distant customer locations.",
                  fig2, "d2")

        state_del = delivery.groupby("customer_state").agg(
            on_time_deliveries=("on_time_deliveries", "sum"),
            delivered_orders=("delivered_orders", "sum"),
            avg_days=("avg_days_to_deliver", "mean")
        ).reset_index()
        state_del["on_time_rate"] = (state_del["on_time_deliveries"] / state_del["delivered_orders"] * 100).round(1)

        fig3 = px.bar(
            state_del.sort_values("on_time_rate", ascending=False),
            x="customer_state", y="on_time_rate",
            color="avg_days",
            color_continuous_scale=["#4ade80", "#fb923c", "#f87171"],
            labels={
                "customer_state": "",
                "on_time_rate": "",
                "avg_days": "Avg Days",
            },
        )
        fig3.add_hline(y=80, line_dash="dash", line_color=C["amber"],
                       annotation_text="80% target", annotation_font_color=C["amber"])
        fig3.update_xaxes(showline=True, linecolor="#1e2d45")
        fig3.update_yaxes(showline=False)
        chart("On-Time Rate by State",
              "States ranked by on-time delivery rate, colored by avg days to deliver. Red states below the 80% line are the highest-priority logistics problem areas.",
              fig3, "d3", height=340)

    except Exception as e:
        st.error(f"Error loading delivery data: {e}")