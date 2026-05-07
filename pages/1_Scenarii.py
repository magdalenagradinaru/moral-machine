import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Scenarii — Moral Machine", page_icon=" ", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
}
[data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e3a5f; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

.scenario-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.scenario-card:hover {
    border-color: #3b82f6;
    box-shadow: 0 0 20px rgba(59,130,246,0.15);
}
.sc-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}
.sc-num {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white;
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.95rem;
    flex-shrink: 0;
}
.sc-title { font-size: 1.1rem; font-weight: 700; color: #e2e8f0; }
.sc-category {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #1e3a5f;
    color: #93c5fd;
    border: 1px solid #3b82f6;
    margin-left: auto;
}
.sc-desc { color: #94a3b8; font-size: 0.95rem; margin-bottom: 16px; line-height: 1.6; }
.option-box {
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.9rem;
    font-weight: 500;
}
.option-a {
    background: rgba(59,130,246,0.12);
    border: 1px solid rgba(59,130,246,0.4);
    color: #93c5fd;
}
.option-b {
    background: rgba(139,92,246,0.12);
    border: 1px solid rgba(139,92,246,0.4);
    color: #c4b5fd;
}
.opt-label {
    font-weight: 800;
    font-size: 0.85rem;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}
.filter-bar {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 24px;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

st.markdown('<div class="page-title">Cele 20 de Scenarii Morale</div>', unsafe_allow_html=True)
st.markdown("Fiecare scenariu prezintă o dilemă etică pentru un vehicul autonom. Studiază-le înainte de a-ți completa răspunsurile.", unsafe_allow_html=False)

# Load scenarios
scenarii_path = os.path.join(DATA_DIR, "scenarii.csv")
try:
    df = pd.read_csv(scenarii_path)
except FileNotFoundError:
    st.error("Fișierul `data/scenarii.csv` nu a fost găsit.")
    st.stop()





# ── Filters ──────────────────────────────────────────────────────────────────
st.markdown('<div class="filter-bar">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    search = st.text_input("Caută în scenarii", placeholder="ex: copii, doctor, animal...")
with col2:
    categorii = ["Toate"] + sorted(df["categorie"].unique().tolist())
    selected_cat = st.selectbox("Filtrează după categorie", categorii)
with col3:
    view_mode = st.radio("Vizualizare", ["Carduri", "Tabel"], horizontal=True)
st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
filtered = df.copy()
if search:
    mask = (
        df["titlu"].str.contains(search, case=False, na=False) |
        df["descriere"].str.contains(search, case=False, na=False) |
        df["optiunea_A"].str.contains(search, case=False, na=False) |
        df["optiunea_B"].str.contains(search, case=False, na=False)
    )
    filtered = df[mask]
if selected_cat != "Toate":
    filtered = filtered[filtered["categorie"] == selected_cat]

st.markdown(f"**{len(filtered)} scenarii** afișate din {len(df)} total")




# ── Render ────────────────────────────────────────────────────────────────────

for _, row in filtered.iterrows():
    st.markdown(f"""
    <div class="scenario-card">
        <div class="sc-header">
            <div class="sc-num">{int(row['id'])}</div>
            <div class="sc-title">{row['titlu']}</div>
            <div class="sc-category">{row['categorie']}</div>
        </div>
        <div class="sc-desc"> {row['descriere']}</div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px;">
            <div class="option-box option-a">
                <div class="opt-label"> OPȚIUNEA A</div>
                {row['optiunea_A']}
            </div>
            <div class="option-box option-b">
                <div class="opt-label"> OPȚIUNEA B</div>
                {row['optiunea_B']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


