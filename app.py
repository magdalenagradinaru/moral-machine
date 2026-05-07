import streamlit as st
import pandas as pd
import os

st.set_page_config(
    page_title="Moral Machine — Om vs. AI",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Base */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
}
[data-testid="stSidebar"] {
    background: #0f172a;
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

/* Cards */
.mm-card {
    background: linear-gradient(135deg, #1e293b, #0f172a);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
    transition: box-shadow 0.3s;
}
.mm-card:hover { box-shadow: 0 0 24px rgba(59,130,246,0.2); }

/* Hero */
.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.2;
    margin-bottom: 12px;
}
.hero-sub {
    font-size: 1.2rem;
    color: #94a3b8;
    margin-bottom: 32px;
}

/* Step cards */
.step-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    height: 100%;
}
.step-num {
    font-size: 2rem;
    font-weight: 900;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.step-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 8px 0 6px;
}
.step-desc { font-size: 0.85rem; color: #94a3b8; }

/* Status pill */
.pill {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
}
.pill-done { background: #14532d; color: #86efac; border: 1px solid #22c55e; }
.pill-todo { background: #1e3a5f; color: #93c5fd; border: 1px solid #3b82f6; }
.pill-warn { background: #78350f; color: #fcd34d; border: 1px solid #f59e0b; }

/* Divider */
.mm-divider {
    border: none;
    border-top: 1px solid #334155;
    margin: 28px 0;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: check progress ───────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def get_progress():
    progress = {
        "scenarii": False,
        "human": 0,
        "llm": 0
    }
    
    scenarii_path = os.path.join(DATA_DIR, "scenarii.csv")
    if os.path.exists(scenarii_path):
        progress["scenarii"] = True
    
    human_path = os.path.join(DATA_DIR, "human_responses.csv")
    if os.path.exists(human_path):
        df = pd.read_csv(human_path)
        progress["human"] = len(df)
    
    llm_path = os.path.join(DATA_DIR, "llm_responses.csv")
    if os.path.exists(llm_path):
        df = pd.read_csv(llm_path)
        progress["llm"] = len(df)
    
    return progress


# ── Page Content ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="mm-card">
    <div class="hero-title"> Moral Machine</div>
    <div class="hero-sub">
        Decizii Etice: Om vs. Inteligență Artificială<br>
    </div>
</div>
""", unsafe_allow_html=True)

