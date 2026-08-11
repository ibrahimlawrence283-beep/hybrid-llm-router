import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import base64
import os

st.set_page_config(
    page_title="Meridian Data Assurance | Telemetry Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

logo_b64 = get_base64_image("logo.png.jpg") or get_base64_image("logo.png.jpg")

st.markdown("""
    <style>
    /* Retain top header area so the sidebar toggle arrow remains visible */
    header[data-testid="stHeader"] {
        background-color: #0b0f17 !important;
    }
    
    /* Global App Background */
    .stApp { background-color: #0b0f17 !important; color: #f1f5f9 !important; }
    .block-container { padding-top: 2rem !important; padding-bottom: 2rem !important; background-color: #0b0f17 !important; }
    section[data-testid="stSidebar"] { background-color: #080b11 !important; border-right: 1px solid #1e293b !important; }

    .brand-logo {
        width: 150px;
        margin-bottom: 12px;
        display: block;
        border-radius: 8px;
        filter: drop-shadow(0px 0px 8px rgba(0, 245, 212, 0.3));
    }

    div[data-testid="stMetric"] {
        background-color: #111827 !important;
        border: 1px solid #00a896 !important;
        border-radius: 8px !important;
        padding: 14px 18px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5) !important;
    }
    div[data-testid="stMetricLabel"] > div {
        font-size: 0.8rem !important;
        color: #94a3b8 !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.6rem !important;
        color: #00f5d4 !important;
        font-weight: 700 !important;
    }

    div[data-testid="stForm"] {
        background-color: #111827 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
    }
    input[type="text"] {
        background-color: #0b0f17 !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
    }

    .stButton>button {
        background-color: #00a896 !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        width: 100%;
    }
    .stButton>button:hover { background-color: #02c39a !important; }

    .status-badge {
        background-color: #111827;
        border: 1px solid #00a896;
        border-radius: 8px;
        padding: 12px;
        margin-top: 15px;
    }
    .status-title { color: #00f5d4; font-weight: 700; font-size: 0.88rem; }
    .status-sub { color: #94a3b8; font-size: 0.78rem; margin-top: 2px; }
    
    .footnote {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: -10px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)
API_URL = "http://127.0.0.1:8000"

with st.sidebar:
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" class="brand-logo">', unsafe_allow_html=True)
    else:
        st.markdown("## 🛡️")
        
    st.markdown("### **Meridian Data Assurance**")
    st.caption("AI Infrastructure & Risk Assurance Engine")
    st.markdown("---")
    
    st.markdown("""
        <div class="status-badge">
            <div class="status-title">⚡ Gateway Operational</div>
            <div class="status-sub">Hybrid ML + LLM Router v1.1</div>
            <div class="status-sub">Vector Similarity Cache Active</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("# **Meridian Data Assurance — Infrastructure Telemetry**")
st.markdown("<p style='color: #94a3b8;'>Real-time cost governance, latency benchmarking (p50/p95), and vector semantic caching.</p>", unsafe_allow_html=True)
st.markdown("---")

@st.cache_data(ttl=1)
def fetch_telemetry():
    try:
        response = requests.get(f"{API_URL}/stats", timeout=2)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return {
        "total_requests": 0, "cache_hits": 0, "light_model_requests": 0,
        "heavy_model_requests": 0, "total_cost_kes": 0.0,
        "estimated_cost_saved_kes": 0.0, "latency_p50_ms": 0.0,
        "latency_p95_ms": 0.0, "recent_history": []
    }

data = fetch_telemetry()

total_reqs = data.get("total_requests", 0)
cache_hits = data.get("cache_hits", 0)
cache_misses = total_reqs - cache_hits
hit_rate = (cache_hits / total_reqs * 100) if total_reqs > 0 else 0.0

light_reqs = data.get("light_model_requests", 0)
heavy_reqs = data.get("heavy_model_requests", 0)
total_spend = data.get("total_cost_kes", 0.0)
total_saved = data.get("estimated_cost_saved_kes", 0.0)
p50 = data.get("latency_p50_ms", 0.0)
p95 = data.get("latency_p95_ms", 0.0)

# Metric Row 1: Costs in KSh
c1, c2, c3, c4 = st.columns(4)
c1.metric(label="Total Gateway Requests", value=f"{total_reqs:,}")
c2.metric(label="Cache Hit Rate", value=f"{hit_rate:.1f}%", delta=f"{cache_hits} Hits")
c3.metric(label="Actual API Spend", value=f"KSh {total_spend:.4f}")
c4.metric(label="Cost Savings Avoided*", value=f"KSh {total_saved:.4f}")

st.markdown("""
    <div class="footnote">
        * Cost savings estimated in KSh based on token counts multiplied by published model rates (1 USD = 130 KES).
    </div>
""", unsafe_allow_html=True)

# Metric Row 2: Latency
l1, l2 = st.columns(2)
l1.metric(label="p50 Latency (Median)", value=f"{p50} ms", delta="Fast response")
l2.metric(label="p95 Latency (Tail)", value=f"{p95} ms", delta="Tail latency")

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("### 🎯 **Cache Hit vs Miss Distribution**")
    cache_df = pd.DataFrame({
        "Type": ["Cache Hits", "Model Inferences"],
        "Count": [cache_hits, cache_misses]
    })
    
    fig_cache = px.pie(
        cache_df, names="Type", values="Count", hole=0.6,
        color="Type", color_discrete_map={"Cache Hits": "#00f5d4", "Model Inferences": "#1e293b"}
    )
    fig_cache.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#0b0f17', width=2)))
    fig_cache.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9', size=14), showlegend=False, margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_cache, use_container_width=True)

with col_right:
    st.markdown("### 🔀 **Model Routing Breakdown**")
    route_df = pd.DataFrame({
        "Model Tier": ["Light (8B Instant)", "Heavy (70B Versatile)"],
        "Executions": [light_reqs, heavy_reqs]
    })
    
    fig_route = px.bar(
        route_df, x="Model Tier", y="Executions", color="Model Tier",
        color_discrete_map={"Light (8B Instant)": "#00a896", "Heavy (70B Versatile)": "#3b82f6"}
    )
    fig_route.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#f1f5f9', size=14), xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#1e293b'), showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10)
    )
    st.plotly_chart(fig_route, use_container_width=True)

st.markdown("---")

# Routing History Table
st.markdown("### 📜 **Recent Routing Decisions & Proof Ledger**")
history = data.get("recent_history", [])

if history:
    history_df = pd.DataFrame(history)
    history_df = history_df[["prompt", "model_used", "cached", "similarity_score", "latency_ms", "cost_kes", "reason"]]
    history_df.columns = ["Prompt", "Model Used", "Cached?", "Similarity", "Latency (ms)", "Cost (KSh)", "Routing Rationale"]
    st.dataframe(history_df, use_container_width=True, hide_index=True)
else:
    st.info("No routing history available yet.")

st.markdown("---")

# Live Sandbox
st.markdown("### ⚡ **Live Request Sandbox**")

with st.form("chat_form"):
    user_input = st.text_input("Enter test query:", placeholder="e.g., What is the capital city of Kenya?")
    submitted = st.form_submit_button("Run Assessment")

if submitted and user_input:
    try:
        res = requests.post(f"{API_URL}/chat", json={"prompt": user_input}, timeout=5)
        if res.status_code == 200:
            res_data = res.json()
            st.success("Execution Complete")
            
            c1, c2, c3 = st.columns(3)
            c1.info(f"**Model Used:** `{res_data.get('model_used')}`")
            c2.warning(f"**Cached:** `{res_data.get('cached', False)}`")
            c3.success(f"**Latency:** `{res_data.get('latency_ms')} ms`")
            
            st.json(res_data)
            st.rerun()
        else:
            st.error(f"Error {res.status_code}: Could not reach router backend.")
    except Exception as e:
        st.error(f"Connection Error: {e}")