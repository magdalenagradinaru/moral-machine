import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Răspuns Uman — Moral Machine", page_icon=" ", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
}
[data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e3a5f; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

.scenario-form-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 28px;
    margin-bottom: 20px;
}
.scenario-form-card.answered {
    border-color: #22c55e;
    background: linear-gradient(135deg, #1e293b, #0f2a1a);
}
.sf-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}
.sf-num {
    background: linear-gradient(135deg, #3b82f6, #8b5cf6);
    color: white;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 1rem;
    flex-shrink: 0;
}
.sf-title { font-size: 1.15rem; font-weight: 700; color: #e2e8f0; }
.sf-category {
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
.sf-desc { color: #94a3b8; font-size: 0.95rem; margin-bottom: 16px; line-height: 1.6; }
.option-preview {
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 0.88rem;
    margin-bottom: 14px;
}
.op-a { background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.4); color: #93c5fd; }
.op-b { background: rgba(139,92,246,0.12); border: 1px solid rgba(139,92,246,0.4); color: #c4b5fd; }
.answered-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    background: #14532d;
    color: #86efac;
    border: 1px solid #22c55e;
    margin-left: 8px;
}
.progress-bar-container {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
}
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #22c55e, #3b82f6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
HUMAN_PATH = os.path.join(DATA_DIR, "human_responses.csv")
SCENARII_PATH = os.path.join(DATA_DIR, "scenarii.csv")


def load_existing_responses():
    if os.path.exists(HUMAN_PATH):
        return pd.read_csv(HUMAN_PATH).set_index("id").to_dict("index")
    return {}


def save_responses(responses: dict):
    records = []
    for id_, data in responses.items():
        records.append({
            "id": id_,
            "human_decision": data.get("human_decision", ""),
            "human_reasoning": data.get("human_reasoning", "")
        })
    df = pd.DataFrame(records)
    df.to_csv(HUMAN_PATH, index=False)


# ── Load data ─────────────────────────────────────────────────────────────────
try:
    scenarii_df = pd.read_csv(SCENARII_PATH)
except FileNotFoundError:
    st.error(" Fișierul `data/scenarii.csv` nu a fost găsit.")
    st.stop()

existing = load_existing_responses()

# Session state for responses
if "responses" not in st.session_state:
    st.session_state.responses = {
        row["id"]: {
            "human_decision": existing.get(row["id"], {}).get("human_decision", ""),
            "human_reasoning": existing.get(row["id"], {}).get("human_reasoning", "")
        }
        for _, row in scenarii_df.iterrows()
    }

#  Header ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title"> Răspunsurile Tale Umane</div>', unsafe_allow_html=True)
st.markdown("Citește fiecare scenariu cu atenție și alege **A** sau **B**, explicând raționamentul tău moral.", unsafe_allow_html=False)

# Progress
answered = sum(1 for v in st.session_state.responses.values() if v["human_decision"] in ["A", "B"])
total = len(scenarii_df)

st.markdown(f"""
<div class="progress-bar-container">
    <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
        <span style="font-weight:700; color:#e2e8f0;">Progres: {answered}/{total} scenarii completate</span>
        <span style="color:#22c55e; font-weight:700;">{int(answered/total*100)}%</span>
    </div>
</div>
""", unsafe_allow_html=True)

progress_bar = st.progress(answered / total if total > 0 else 0)

# Quick jump
st.markdown("**Salt rapid la scenariu:**")
jump_cols = st.columns(10)
for i, (_, row) in enumerate(scenarii_df.iterrows()):
    sid = row["id"]
    is_answered = st.session_state.responses.get(sid, {}).get("human_decision", "") in ["A", "B"]
    emoji = "✅" if is_answered else "⬜"
    with jump_cols[i % 10]:
        if st.button(f"{emoji}{sid}", key=f"jump_{sid}", help=row["titlu"]):
            st.session_state.jump_to = sid

st.markdown("---")



# ── Render each scenario ───────────────────────────────────────────────────────
for _, row in scenarii_df.iterrows():
    sid = row["id"]
    current = st.session_state.responses.get(sid, {})
    is_answered = current.get("human_decision", "") in ["A", "B"]
    
    answered_html = '<span class="answered-badge">Completat</span>' if is_answered else ''
    card_class = "scenario-form-card answered" if is_answered else "scenario-form-card"
    
    # Anchor for jump
    st.markdown(f'<div id="sc_{sid}"></div>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="{card_class}">
        <div class="sf-header">
            <div class="sf-num">{int(sid)}</div>
            <div class="sf-title">{row['titlu']} {answered_html}</div>
            <div class="sf-category">{row['categorie']}</div>
        </div>
        <div class="sf-desc"> {row['descriere']}</div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:16px;">
            <div class="option-preview op-a"><strong>🅐 A:</strong> {row['optiunea_A']}</div>
            <div class="option-preview op-b"><strong>🅑 B:</strong> {row['optiunea_B']}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        decision_options = ["— Alege —", "A", "B"]
        current_decision = current.get("human_decision", "")
        default_idx = decision_options.index(current_decision) if current_decision in decision_options else 0
        
        decision = st.selectbox(
            f"Decizia ta pentru scenariul #{sid}",
            decision_options,
            index=default_idx,
            key=f"dec_{sid}",
            label_visibility="collapsed"
        )
    
    with col2:
        reasoning = st.text_area(
            f"Raționamentul tău pentru #{sid}",
            value=current.get("human_reasoning", ""),
            placeholder="Explică de ce ai ales această opțiune. Ce principii morale ai aplicat? (2-5 propoziții)",
            key=f"rea_{sid}",
            height=100,
            label_visibility="collapsed"
        )
    
    # Update session state
    if decision != "— Alege —":
        st.session_state.responses[sid] = {
            "human_decision": decision,
            "human_reasoning": reasoning
        }
    elif reasoning:
        st.session_state.responses[sid] = {
            "human_decision": current.get("human_decision", ""),
            "human_reasoning": reasoning
        }
    
    st.markdown("<br>", unsafe_allow_html=True)




# ── Save button ────────────────────────────────────────────────────────────────
st.markdown("---")
col_save1, col_save2, col_save3 = st.columns([1, 2, 1])

with col_save2:
    answered_now = sum(1 for v in st.session_state.responses.values() if v["human_decision"] in ["A", "B"])
    
    if st.button(
        f" Salvează Răspunsurile ({answered_now}/{total} completate)",
        type="primary",
        use_container_width=True
    ):
        save_responses(st.session_state.responses)
        progress_bar.progress(answered_now / total)
        
        if answered_now == total:
            st.success(f"Toate cele {total} răspunsuri au fost salvate! Mergi la **Pagina 3** pentru a rula AI-ul.")
            st.balloons()
        elif answered_now > 0:
            missing = [sid for sid, v in st.session_state.responses.items() if v["human_decision"] not in ["A", "B"]]
            st.warning(f" Salvat {answered_now}/{total}. Scenarii incomplete: {missing}")
        else:
            st.info("ℹNicio decizie selectată încă.")
    
    if answered_now > 0 and os.path.exists(HUMAN_PATH):
        with open(HUMAN_PATH, "rb") as f:
            st.download_button(
                "Descarcă CSV cu răspunsurile tale",
                f,
                file_name="human_responses.csv",
                mime="text/csv",
                use_container_width=True
            )
