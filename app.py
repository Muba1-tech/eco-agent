"""
app.py - EcoAgent: Enterprise AI Sustainability & Carbon Advisor.
Multi-Agent Sustainability Platform aligned with UN SDG 12 & SDG 13.
Built for IBM SkillsBuild & Enterprise Sustainability Auditing.
"""

import os
import sys

# Critical Windows OpenMP & threading configuration
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import time
import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

from agents.diagnosis_agent import run_diagnosis
from agents.recommendation_agent import generate_recommendations
from agents.impact_agent import calculate_impact, generate_pdf_report
from agents.monte_carlo import run_monte_carlo_simulation
from agents.knowledge_graph import generate_knowledge_graph_figure
from build_index import query_hybrid_rag, query_knowledge_base
from db import save_audit, get_all_audits, get_community_impact
from llm_connector import is_ollama_available

# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EcoAgent — AI Carbon Advisor",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# High-Contrast Enterprise UI/UX Theme & Styling System
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Outfit:wght@400;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Plus Jakarta Sans', 'Outfit', 'Inter', sans-serif;
    }
    
    /* Sleek High-Contrast Dark Theme with Radial Emerald Accent */
    .main {
        background: radial-gradient(circle at 50% 0%, #064e3b 0%, #090d16 45%, #05070c 100%);
        color: #f8fafc;
    }

    /* Force All Markdown Headings & Paragraphs to Crisp High Contrast */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6, [data-testid="stMarkdownContainer"] h1, [data-testid="stMarkdownContainer"] h2, [data-testid="stMarkdownContainer"] h3, [data-testid="stMarkdownContainer"] h4, [data-testid="stMarkdownContainer"] h5, [data-testid="stMarkdownContainer"] h6 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.3px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.6);
    }

    [data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li {
        color: #f1f5f9 !important;
        font-size: 14px;
        font-weight: 500;
    }

    .stCaption, [data-testid="stCaptionContainer"] {
        color: #cbd5e1 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    /* High-Contrast Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(13, 148, 136, 0.95) 50%, rgba(147, 51, 234, 0.9) 100%);
        border: 2px solid rgba(52, 211, 153, 0.5);
        border-radius: 18px;
        padding: 24px 32px;
        color: #ffffff;
        margin-bottom: 20px;
        box-shadow: 0 12px 32px -6px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        backdrop-filter: blur(16px);
    }
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 32px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin: 0 0 6px 0;
        color: #ffffff !important;
        text-shadow: 0 2px 12px rgba(0, 0, 0, 0.7);
    }
    .hero-subtitle {
        font-size: 15px;
        color: #f0fdf4 !important;
        margin: 0;
        font-weight: 600;
        line-height: 1.4;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
    }

    /* Streamlit Tab Buttons High-Contrast Overrides */
    button[data-baseweb="tab"] {
        background: rgba(15, 23, 42, 0.8) !important;
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border-radius: 12px !important;
        padding: 8px 18px !important;
        margin-right: 8px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        transition: all 0.2s ease !important;
    }
    button[data-baseweb="tab"]:hover {
        background: rgba(13, 148, 136, 0.4) !important;
        color: #ffffff !important;
        border-color: rgba(52, 211, 153, 0.5) !important;
    }
    button[aria-selected="true"] {
        background: linear-gradient(135deg, #0d9488, #059669) !important;
        color: #ffffff !important;
        border: 1.5px solid #5eead4 !important;
        box-shadow: 0 4px 16px rgba(45, 212, 191, 0.4) !important;
    }

    /* Metric Cards - High-Contrast Dark Surface */
    .metric-card {
        background: rgba(15, 23, 42, 0.88);
        border: 1.5px solid rgba(52, 211, 153, 0.4);
        border-top: 4px solid #34d399;
        border-radius: 16px;
        padding: 16px 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(12px);
        transition: all 0.25s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: #5eead4;
        box-shadow: 0 12px 30px rgba(45, 212, 191, 0.35);
    }
    .metric-label {
        font-size: 12px;
        font-weight: 800;
        color: #67e8f9 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 4px;
        text-shadow: 0 1px 3px rgba(0,0,0,0.8);
    }
    .metric-value {
        font-family: 'Outfit', sans-serif;
        font-size: 28px;
        font-weight: 800;
        color: #ffffff !important;
        line-height: 1.1;
        text-shadow: 0 2px 8px rgba(0,0,0,0.6);
    }
    .metric-delta {
        font-size: 12px;
        font-weight: 700;
        margin-top: 6px;
    }
    .delta-good { color: #34d399 !important; }
    .delta-warn { color: #fde047 !important; }
    .delta-bad  { color: #fb7185 !important; }

    /* Recommendation & Inefficiency Cards */
    .rec-card {
        background: rgba(15, 23, 42, 0.88);
        border-left: 5px solid #2dd4bf;
        border-top: 1px solid rgba(255, 255, 255, 0.12);
        border-right: 1px solid rgba(255, 255, 255, 0.12);
        border-bottom: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 12px;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(12px);
    }
    .rec-card-high { border-left-color: #fb7185; }
    .rec-card-med { border-left-color: #fde047; }
    .rec-card-low { border-left-color: #34d399; }
    
    .govt-tag {
        display: inline-block;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        padding: 4px 12px;
        border-radius: 9999px;
        background: rgba(45, 212, 191, 0.25);
        color: #5eead4 !important;
        border: 1px solid rgba(45, 212, 191, 0.5);
    }
    
    .scope-card {
        background: rgba(15, 23, 42, 0.88);
        border-radius: 12px;
        padding: 14px 18px;
        border: 1px solid rgba(255, 255, 255, 0.15);
        font-size: 14px;
        color: #ffffff !important;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* Expanders & Form Input Overrides */
    div[data-testid="stExpander"] {
        background: rgba(15, 23, 42, 0.88) !important;
        border: 1px solid rgba(52, 211, 153, 0.35) !important;
        border-radius: 14px !important;
        color: #ffffff !important;
    }

    div[data-testid="stExpander"] summary span {
        color: #5eead4 !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    .stTextInput label, .stSelectbox label, .stNumberInput label, .stSlider label {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 14px !important;
    }

    /* Sidebar High Contrast */
    [data-testid="stSidebar"] {
        background-color: rgba(9, 13, 22, 0.96) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4 {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Demo Presets
# -----------------------------------------------------------------------------
DEMO_PRESETS = {
    "🏢 Urban Retail Store & Office (Bengaluru)": {
        "user_name": "Koramangala Commercial Mart",
        "property_type": "Small Business / Commercial",
        "occupants": 8,
        "city_state": "Bengaluru, Karnataka",
        "monthly_kwh": 1150.0,
        "monthly_bill": 9800.0,
        "tariff_inr_per_kwh": 8.5,
        "ac_count": 3,
        "ac_star_rating": "Unrated / >5 yrs old",
        "ac_temp_setting": 20,
        "fan_count": 6,
        "fan_type": "Conventional Induction (75W)",
        "lighting_type": "Mixed",
        "has_solar": False,
        "rooftop_sqft": 650.0,
        "water_consumption_lpcd": 190.0,
        "has_water_aerators": False,
        "has_rainwater_harvesting": False,
        "segregates_waste": False,
        "home_composting": False,
        "single_use_plastic_usage": "Frequent"
    },
    "🏡 High-Consumption Family Villa (South Delhi)": {
        "user_name": "Sharma Household",
        "property_type": "Residential Household",
        "occupants": 4,
        "city_state": "South Delhi, Delhi NCR",
        "monthly_kwh": 650.0,
        "monthly_bill": 5400.0,
        "tariff_inr_per_kwh": 8.0,
        "ac_count": 2,
        "ac_star_rating": "1-2 Star",
        "ac_temp_setting": 21,
        "fan_count": 5,
        "fan_type": "Conventional Induction (75W)",
        "lighting_type": "Mixed",
        "has_solar": False,
        "rooftop_sqft": 450.0,
        "water_consumption_lpcd": 180.0,
        "has_water_aerators": False,
        "has_rainwater_harvesting": False,
        "segregates_waste": False,
        "home_composting": False,
        "single_use_plastic_usage": "Moderate"
    },
    "🏙️ Suburban Apartment (Thane, Mumbai)": {
        "user_name": "Verma Family",
        "property_type": "Residential Apartment",
        "occupants": 3,
        "city_state": "Mumbai MMR, Maharashtra",
        "monthly_kwh": 380.0,
        "monthly_bill": 3200.0,
        "tariff_inr_per_kwh": 8.4,
        "ac_count": 1,
        "ac_star_rating": "3 Star",
        "ac_temp_setting": 23,
        "fan_count": 3,
        "fan_type": "Conventional Induction (75W)",
        "lighting_type": "Mixed",
        "has_solar": False,
        "rooftop_sqft": 200.0,
        "water_consumption_lpcd": 170.0,
        "has_water_aerators": False,
        "has_rainwater_harvesting": False,
        "segregates_waste": True,
        "home_composting": False,
        "single_use_plastic_usage": "Moderate"
    },
    "🌿 Eco-Conscious Studio & Office (Pune)": {
        "user_name": "GreenTech Studio",
        "property_type": "Small Business / Commercial",
        "occupants": 5,
        "city_state": "Pune, Maharashtra",
        "monthly_kwh": 320.0,
        "monthly_bill": 2600.0,
        "tariff_inr_per_kwh": 8.0,
        "ac_count": 1,
        "ac_star_rating": "5 Star Inverter",
        "ac_temp_setting": 25,
        "fan_count": 4,
        "fan_type": "5-Star BLDC (28W)",
        "lighting_type": "100% BEE LED",
        "has_solar": False,
        "rooftop_sqft": 350.0,
        "water_consumption_lpcd": 130.0,
        "has_water_aerators": True,
        "has_rainwater_harvesting": False,
        "segregates_waste": True,
        "home_composting": True,
        "single_use_plastic_usage": "Rare / Avoided"
    }
}

# -----------------------------------------------------------------------------
# Fast Cached Audit Pipeline
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def cached_run_full_audit(data_dict: dict):
    t0 = time.time()
    p = run_diagnosis(data_dict)
    r = generate_recommendations(p, custom_gemini_key=os.environ.get("GEMINI_API_KEY", ""))
    i = calculate_impact(p, r)
    elapsed = round(time.time() - t0, 3)
    return p, r, i, elapsed

if "current_preset_name" not in st.session_state:
    st.session_state.current_preset_name = list(DEMO_PRESETS.keys())[0]

if "form_data" not in st.session_state:
    st.session_state.form_data = DEMO_PRESETS[st.session_state.current_preset_name].copy()

if "profile" not in st.session_state:
    init_data = st.session_state.form_data
    init_prof, init_recs, init_impact, elapsed = cached_run_full_audit(init_data)
    st.session_state.profile = init_prof
    st.session_state.recommendations = init_recs
    st.session_state.impact = init_impact
    st.session_state.last_exec_time = elapsed

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "👋 **EcoBot Online:** Ask me about solar subsidies, BEE star ratings, or statutory waste rules!"}
    ]

# -----------------------------------------------------------------------------
# SIDEBAR CONTROLS
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/leaf.png", width=44)
    st.markdown("### 🌿 **EcoAgent AI**")
    
    st.markdown("---")
    st.markdown("#### ⚡ **Select Test Scenario**")
    preset_choice = st.selectbox(
        "Facility Preset:",
        options=list(DEMO_PRESETS.keys()),
        index=list(DEMO_PRESETS.keys()).index(st.session_state.current_preset_name)
    )
    
    if preset_choice != st.session_state.current_preset_name:
        st.session_state.current_preset_name = preset_choice
        st.session_state.form_data = DEMO_PRESETS[preset_choice].copy()
        with st.spinner("Analyzing profile..."):
            p, r, i, elapsed = cached_run_full_audit(st.session_state.form_data)
            st.session_state.profile = p
            st.session_state.recommendations = r
            st.session_state.impact = i
            st.session_state.last_exec_time = elapsed
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🤖 **AI Engine**")
    st.success("⚡ Hybrid RAG Active")

    st.markdown("---")
    st.markdown("#### 🌐 **Collective Impact**")
    comm_stats = get_community_impact()
    st.metric("Total Audits", f"{comm_stats['total_audits']:,}")
    st.metric("CO₂ Avoided", f"{comm_stats['total_annual_co2_kg']:,.0f} kg")
    st.metric("Cost Saved", f"₹{comm_stats['total_annual_savings_inr']:,.0f}")

# -----------------------------------------------------------------------------
# MAIN HERO HEADER
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🌱 EcoAgent — Real-Time Sustainability & Carbon Advisor</div>
    <div class="hero-subtitle">Autonomous 3-Agent Carbon Intelligence Grounded in Indian Statutory Policies (BEE, MNRE, CPCB, CEA) & GHG Protocol Scopes 1-3.</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4 MASTER TABS
# -----------------------------------------------------------------------------
tab_twin, tab_recs, tab_impact, tab_copilot = st.tabs([
    "🏢 1. Diagnostics",
    "💡 2. Policy RAG",
    "📈 3. Carbon & ROI",
    "🤖 4. AI Co-Pilot"
])

# =============================================================================
# TAB 1: DIAGNOSTICS
# =============================================================================
with tab_twin:
    prof = st.session_state.profile
    metrics = prof.get("metrics", {})
    
    score = metrics.get("sustainability_score", 50)
    score_grade = "A (Exemplary)" if score >= 85 else ("B (Good)" if score >= 70 else ("C (Sub-Optimal)" if score >= 50 else "D (High Waste)"))
    score_color = "#34d399" if score >= 70 else ("#fde047" if score >= 50 else "#fb7185")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🌱 Sustainability Score</div>
            <div class="metric-value" style="color: {score_color};">{score} <span style="font-size: 14px; color: #a7f3d0;">/ 100</span></div>
            <div class="metric-delta delta-warn">Rating: {score_grade}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        kwh_capita = metrics.get("per_capita_kwh", 0)
        kwh_diff = metrics.get("kwh_vs_benchmark_pct", 0)
        delta_cls = "delta-bad" if kwh_diff > 15 else ("delta-warn" if kwh_diff > 0 else "delta-good")
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #38bdf8;">
            <div class="metric-label">⚡ Power Draw</div>
            <div class="metric-value">{kwh_capita} <span style="font-size: 14px; color: #bae6fd;">kWh/mo</span></div>
            <div class="metric-delta {delta_cls}">{'+' if kwh_diff > 0 else ''}{kwh_diff}% vs CEA Baseline</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        w_val = metrics.get("water_lpcd", 135)
        w_diff = metrics.get("water_vs_benchmark_pct", 0)
        w_cls = "delta-bad" if w_diff > 15 else ("delta-warn" if w_diff > 0 else "delta-good")
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #67e8f9;">
            <div class="metric-label">💧 Water Draw</div>
            <div class="metric-value">{w_val} <span style="font-size: 14px; color: #cffafe;">LPCD</span></div>
            <div class="metric-delta {w_cls}">{'+' if w_diff > 0 else ''}{w_diff}% vs CPHEEO Std</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #fb7185;">
            <div class="metric-label">🚩 Inefficiencies</div>
            <div class="metric-value" style="color: #fb7185;">{prof.get('total_inefficiencies_flagged', 0)} <span style="font-size: 14px; color: #fecdd3;">Gaps</span></div>
            <div class="metric-delta delta-warn">Mapped to Statutory Acts</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.markdown("##### 📊 **Facility vs National Baseline**")
        df_bench = pd.DataFrame({
            "Metric": ["Electricity (kWh)", "Water (LPCD)", "Waste (kg/day)"],
            "Facility": [kwh_capita, w_val, round(metrics.get("waste_kg_day", 1.8) / max(1, prof.get("occupants", 4)), 2)],
            "Benchmark": [95.0, 135.0, 0.45]
        })
        fig_bench = go.Figure(data=[
            go.Bar(name='Facility', x=df_bench['Metric'], y=df_bench['Facility'], marker_color='#38bdf8'),
            go.Bar(name='CEA Baseline', x=df_bench['Metric'], y=df_bench['Benchmark'], marker_color='#34d399')
        ])
        fig_bench.update_layout(barmode='group', height=260, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_bench, use_container_width=True)

    with col_c2:
        st.markdown("##### 🔌 **Power Load Breakdown**")
        inv = prof.get("inventory", {})
        ac_cnt = inv.get("ac_count", 0)
        fan_cnt = inv.get("fan_count", 4)
        
        est_ac_kwh = ac_cnt * (180 if "5 Star" in inv.get("ac_rating", "") else 320)
        est_fan_kwh = fan_cnt * (15 if "BLDC" in inv.get("fan_type", "") else 45)
        est_light_kwh = 35 if "LED" in inv.get("lighting", "") else 75
        est_other_kwh = max(40.0, metrics.get("monthly_kwh", 450) - (est_ac_kwh + est_fan_kwh + est_light_kwh))
        
        df_pie = pd.DataFrame({
            "Appliance": ["AC", "Fans", "Lighting", "Other"],
            "Monthly kWh": [est_ac_kwh, est_fan_kwh, est_light_kwh, est_other_kwh]
        })
        fig_pie = px.pie(df_pie, names="Appliance", values="Monthly kWh", color_discrete_sequence=['#fb7185', '#fde047', '#38bdf8', '#34d399'], hole=0.5)
        fig_pie.update_layout(height=260, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown("##### 🚩 **Flagged Inefficiencies:**")
    for item in prof.get("flagged_inefficiencies", []):
        prio_color = "#fb7185" if item["severity"] == "HIGH" else ("#fde047" if item["severity"] == "MEDIUM" else "#34d399")
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.88); border-left: 4px solid {prio_color}; border: 1px solid rgba(255,255,255,0.12); border-left-width: 5px; border-left-color: {prio_color}; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-weight: 700; font-size: 14px; color: #ffffff;">{item['title']}</span>
            <span style="background: {prio_color}25; color: {prio_color}; font-size: 11px; font-weight: 800; padding: 3px 10px; border-radius: 9999px;">{item['severity']} PRIORITY</span>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("⚙️ Customize Facility Inputs"):
        form_data = st.session_state.form_data
        with st.form("audit_form_tab1"):
            col1, col2 = st.columns(2)
            with col1:
                u_name = st.text_input("Name:", value=form_data.get("user_name", "Eco User"))
                m_kwh = st.number_input("Monthly kWh:", min_value=0.0, value=float(form_data.get("monthly_kwh", 450.0)))
                m_bill = st.number_input("Monthly Bill (₹):", min_value=0.0, value=float(form_data.get("monthly_bill", 3500.0)))
            with col2:
                ac_cnt = st.number_input("AC Count:", min_value=0, value=int(form_data.get("ac_count", 2)))
                w_lpcd = st.number_input("Water LPCD:", min_value=30.0, value=float(form_data.get("water_consumption_lpcd", 175.0)))
                seg_w = st.checkbox("Segregates Waste?", value=bool(form_data.get("segregates_waste", False)))
            
            if st.form_submit_button("⚡ Run Diagnosis"):
                form_data["user_name"] = u_name
                form_data["monthly_kwh"] = m_kwh
                form_data["monthly_bill"] = m_bill
                form_data["ac_count"] = ac_cnt
                form_data["water_consumption_lpcd"] = w_lpcd
                form_data["segregates_waste"] = seg_w
                p, r, i, elapsed = cached_run_full_audit(form_data)
                st.session_state.profile = p
                st.session_state.recommendations = r
                st.session_state.impact = i
                st.rerun()

# =============================================================================
# TAB 2: POLICY RAG
# =============================================================================
with tab_recs:
    recs = st.session_state.recommendations
    st.markdown("### 💡 **Policy-Grounded Action Plan**")

    for r in recs:
        prio_border = "rec-card-high" if r.get("severity") == "HIGH" else ("rec-card-med" if r.get("severity") == "MEDIUM" else "rec-card-low")
        score_pct = int(r.get("rag_similarity_score", 0.0) * 100)
        
        st.markdown(f"""
        <div class="rec-card {prio_border}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 15px; font-weight: 800; color: #ffffff;">{r['title']}</span>
                <span class="govt-tag">🏛️ {r['source_authority']}</span>
            </div>
            <div style="font-size: 13px; color: #f1f5f9; margin-top: 6px; font-weight: 500;">
                <b style="color: #5eead4;">Action:</b> {r['action']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("🕸️ Statutory Knowledge Graph Visualizer"):
        kg_fig = generate_knowledge_graph_figure(st.session_state.recommendations)
        st.plotly_chart(kg_fig, use_container_width=True)

# =============================================================================
# TAB 3: CARBON & ROI
# =============================================================================
with tab_impact:
    impact = st.session_state.impact
    summary = impact.get("summary", {})
    ranked_recs = impact.get("ranked_recommendations", [])
    
    st.markdown("### 📈 **Financial ROI & Carbon Accounting**")

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #34d399;">
            <div class="metric-label">💰 Annual Savings</div>
            <div class="metric-value" style="color: #34d399;">₹{summary.get('total_annual_cost_savings_inr', 0):,.0f}</div>
            <div class="metric-delta delta-good">Payback ~1.5 yrs</div>
        </div>
        """, unsafe_allow_html=True)
        
    with k2:
        co2_kg = summary.get("total_annual_co2_reduction_kg", 0)
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #38bdf8;">
            <div class="metric-label">🌍 CO₂ Avoided</div>
            <div class="metric-value" style="color: #38bdf8;">{co2_kg:,.0f} <span style="font-size: 14px; color: #bae6fd;">kg</span></div>
            <div class="metric-delta delta-good">{summary.get('total_annual_co2_reduction_tonnes', 0)} tCO₂e/yr</div>
        </div>
        """, unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #a7f3d0;">
            <div class="metric-label">🌳 Trees Equiv.</div>
            <div class="metric-value" style="color: #a7f3d0;">{summary.get('trees_equivalent_annual', 0):,.0f}</div>
            <div class="metric-delta delta-good">Trees Planted</div>
        </div>
        """, unsafe_allow_html=True)

    with k4:
        st.markdown(f"""
        <div class="metric-card" style="border-top-color: #c084fc;">
            <div class="metric-label">💧 Water & Waste</div>
            <div class="metric-value" style="color: #c084fc;">{summary.get('total_water_saved_liters_year', 0):,.0f} <span style="font-size: 14px; color: #e9d5ff;">L</span></div>
            <div class="metric-delta delta-good">{summary.get('total_waste_diverted_kg_year', 0):,.0f} kg Diverted</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(f"<div class='scope-card' style='border-left: 4px solid #fb7185;'><b>🌸 Scope 1 (Direct):</b> {summary.get('scope1_co2_kg', 0):,.0f} kg CO₂</div>", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"<div class='scope-card' style='border-left: 4px solid #38bdf8;'><b>✨ Scope 2 (Energy):</b> {summary.get('scope2_co2_kg', 0):,.0f} kg CO₂</div>", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"<div class='scope-card' style='border-left: 4px solid #34d399;'><b>🍃 Scope 3 (Value Chain):</b> {summary.get('scope3_co2_kg', 0):,.0f} kg CO₂</div>", unsafe_allow_html=True)

    st.markdown("---")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        st.markdown("##### 💰 **Savings by Intervention (₹)**")
        df_sav = pd.DataFrame([{"Intervention": r["title"][:18], "Annual Savings (₹)": r["cost_saved_year_inr"]} for r in ranked_recs if r["cost_saved_year_inr"] > 0])
        if not df_sav.empty:
            fig_sav = px.bar(df_sav, x="Annual Savings (₹)", y="Intervention", orientation='h', color_discrete_sequence=['#38bdf8'])
            fig_sav.update_layout(height=240, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_sav, use_container_width=True)

    with col_p2:
        st.markdown("##### 📊 **MACC Abatement Curve**")
        df_macc = pd.DataFrame([{"Intervention": r["title"][:18], "Abatement Cost (₹/tCO2)": r["abatement_cost_per_ton_inr"]} for r in ranked_recs if r["co2_reduced_year_kg"] > 0])
        if not df_macc.empty:
            fig_macc = px.bar(df_macc, x="Intervention", y="Abatement Cost (₹/tCO2)", color_discrete_sequence=['#34d399'])
            fig_macc.update_layout(height=240, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_macc, use_container_width=True)

    with st.expander("🎲 Monte Carlo Risk & PDF Report Download"):
        pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", f"EcoAgent_Audit_Report.pdf")
        if st.button("📥 Prepare PDF Report", type="primary"):
            generate_pdf_report(st.session_state.profile, impact, pdf_path)
            st.success("✅ Executive Report Ready!")
            with open(pdf_path, "rb") as f:
                st.download_button("⬇️ Download PDF Report", f.read(), file_name="EcoAgent_Report.pdf", mime="application/pdf")

# =============================================================================
# TAB 4: AI CO-PILOT
# =============================================================================
with tab_copilot:
    st.markdown("### 🤖 **EcoBot AI Co-Pilot**")

    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if user_input := st.chat_input("Ask EcoBot e.g., 'How do I apply for PM-Surya Ghar subsidy?'"):
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            rag_res = query_hybrid_rag(user_input, top_k=1)
            top_match = rag_res[0] if rag_res else None
            ans = f"Based on **{top_match['authority']}** guidelines:\n\n> \"{top_match['text']}\"" if top_match else "Under CEA/CPCB benchmarks, implement energy conservation and waste segregation."
            st.markdown(ans)
            st.session_state.chat_messages.append({"role": "assistant", "content": ans})
