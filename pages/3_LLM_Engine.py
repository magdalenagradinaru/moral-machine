import streamlit as st
import pandas as pd
import os
import sys
import time

st.set_page_config(page_title="LLM Engine — Moral Machine", page_icon="🤖", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
}
[data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e3a5f; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

.llm-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    animation: fadeIn 0.4s ease;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.llm-card.done { border-color: #8b5cf6; }
.result-row {
    display: grid;
    grid-template-columns: 80px 1fr 1fr;
    gap: 16px;
    align-items: start;
}
.decision-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    border-radius: 12px;
    font-size: 1.5rem;
    font-weight: 900;
    border: 2px solid;
}
.dec-a { background: rgba(59,130,246,0.2); color: #93c5fd; border-color: #3b82f6; }
.dec-b { background: rgba(139,92,246,0.2); color: #c4b5fd; border-color: #8b5cf6; }
.dec-err { background: rgba(239,68,68,0.2); color: #fca5a5; border-color: #ef4444; }
.principle-tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    background: #1e3a5f;
    color: #93c5fd;
    border: 1px solid #3b82f6;
    margin-bottom: 8px;
}
.reasoning-text { color: #94a3b8; font-size: 0.9rem; line-height: 1.6; }
.sc-title-sm { font-size: 1rem; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; }
.sc-options-sm { font-size: 0.8rem; color: #64748b; margin-bottom: 8px; }
.status-bar {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
}
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}
.warning-box {
    background: rgba(245,158,11,0.1);
    border: 1px solid #f59e0b;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
}
.success-box {
    background: rgba(34,197,94,0.1);
    border: 1px solid #22c55e;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
}
.error-box {
    background: rgba(239,68,68,0.1);
    border: 1px solid #ef4444;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
sys.path.insert(0, BASE_DIR)

SCENARII_PATH = os.path.join(DATA_DIR, "scenarii.csv")
LLM_PATH = os.path.join(DATA_DIR, "llm_responses.csv")

st.markdown('<div class="page-title">Moral Decision Engine — Claude AI</div>', unsafe_allow_html=True)
st.markdown("Trimite toate cele 20 de scenarii la Claude AI și obține deciziile, raționamentul și principiile morale folosite.", unsafe_allow_html=False)

# ── Load scenarios ────────────────────────────────────────────────────────────
try:
    scenarii_df = pd.read_csv(SCENARII_PATH)
except FileNotFoundError:
    st.error("Fișierul `data/scenarii.csv` nu a fost găsit.")
    st.stop()

# ── Load existing LLM responses ───────────────────────────────────────────────
existing_llm = {}
if os.path.exists(LLM_PATH):
    llm_df = pd.read_csv(LLM_PATH)
    existing_llm = llm_df.set_index("id").to_dict("index")

# ── API Key check ──────────────────────────────────────────────────────────────
from utils.llm_engine import validate_api_key

api_valid = validate_api_key()

if not api_valid:
    st.markdown("""
    <div class="warning-box">
         <strong>API Key lipsă!</strong> Creează fișierul <code>.env</code> în folderul proiectului cu:<br><br>
        <code>ANTHROPIC_API_KEY=sk-ant-CHEIA_TA_AICI</code><br><br>
        Obții un API key gratuit de la <a href="https://console.anthropic.com" target="_blank">console.anthropic.com</a>
    </div>
    """, unsafe_allow_html=True)

# ── Status ─────────────────────────────────────────────────────────────────────
total = len(scenarii_df)
done = len(existing_llm)
remaining = total - done

st.markdown(f"""
<div class="status-bar">
    <div style="display:flex; justify-content:space-between; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
        <span style="font-weight:700; color:#e2e8f0;">Scenarii procesate: {done}/{total}</span>
        <span style="color:#8b5cf6; font-weight:700;">{int(done/total*100)}% complet</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.progress(done / total if total > 0 else 0)

# ── Control panel ──────────────────────────────────────────────────────────────
st.markdown("---")
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)

with col_ctrl1:
    run_all = st.button(
        "Rulează AI pe Toate Scenariile" if done == 0 else f"Reîncarcă toate ({total} scenarii)",
        type="primary",
        use_container_width=True,
        disabled=not api_valid
    )

with col_ctrl2:
    run_missing = st.button(
        f"Continuă — {remaining} rămase",
        use_container_width=True,
        disabled=(remaining == 0 or not api_valid)
    )

with col_ctrl3:
    if done > 0:
        if st.button("Șterge răspunsurile AI", use_container_width=True):
            if os.path.exists(LLM_PATH):
                os.remove(LLM_PATH)
            existing_llm = {}
            st.rerun()

# ── Run LLM ───────────────────────────────────────────────────────────────────
def run_llm_on_scenarios(scenarios_to_run: list, existing: dict):
    from utils.llm_engine import get_llm_decision
    
    results = dict(existing)
    
    st.markdown("###Procesare în curs...")
    progress_placeholder = st.empty()
    status_placeholder = st.empty()
    results_container = st.container()
    
    for i, row in enumerate(scenarios_to_run):
        sid = row["id"]
        progress_placeholder.progress((i + 1) / len(scenarios_to_run))
        status_placeholder.markdown(f"Procesez scenariu **#{sid}: {row['titlu']}**... ({i+1}/{len(scenarios_to_run)})")
        
        try:
            result = get_llm_decision(row)
            results[sid] = result
            
            # Show result immediately
            dec = result.get("llm_decision", "?")
            dec_class = "dec-a" if dec == "A" else ("dec-b" if dec == "B" else "dec-err")
            
            with results_container:
                st.markdown(f"""
                <div class="llm-card done">
                    <div class="result-row">
                        <div style="text-align:center;">
                            <div class="decision-badge {dec_class}">{dec}</div>
                            <div style="font-size:0.7rem; color:#64748b; margin-top:4px;">Scenariu #{sid}</div>
                        </div>
                        <div>
                            <div class="sc-title-sm">{row['titlu']}</div>
                            <div class="sc-options-sm">A: {row['optiunea_A'][:60]}...</div>
                            <span class="principle-tag">⚖️ {result.get('llm_moral_principle', '—')}</span>
                        </div>
                        <div>
                            <div class="reasoning-text">{result.get('llm_reasoning', '—')}</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Save incrementally
            records = [{"id": k, **v} for k, v in results.items()]
            pd.DataFrame(records).to_csv(LLM_PATH, index=False)
            
            time.sleep(0.5)  # Rate limiting courtesy
            
        except ValueError as e:
            status_placeholder.error(f"{str(e)}")
            break
        except Exception as e:
            results[sid] = {
                "llm_decision": "EROARE",
                "llm_reasoning": str(e),
                "llm_moral_principle": "N/A"
            }
    
    progress_placeholder.empty()
    status_placeholder.empty()
    
    return results


if run_all or run_missing:
    if run_all:
        scenarios_to_run = scenarii_df.to_dict("records")
    else:
        already_done = set(existing_llm.keys())
        scenarios_to_run = [
            row for _, row in scenarii_df.iterrows()
            if row["id"] not in already_done
        ]
    
    with st.spinner(""):
        existing_llm = run_llm_on_scenarios(scenarios_to_run, existing_llm if run_missing else {})
    
    done = len(existing_llm)
    if done == total:
        st.markdown("""
        <div class="success-box">
            <strong>Toate scenariile au fost procesate!</strong> 
            Mergi la <strong>Pagina 4 — Analiză</strong> pentru tabelul comparativ și grafice.
        </div>
        """, unsafe_allow_html=True)
        st.balloons()
    
    st.rerun()

# ── Display existing results ───────────────────────────────────────────────────
if existing_llm:
    st.markdown("---")
    st.markdown("###Rezultate AI Salvate")
    
    for _, row in scenarii_df.iterrows():
        sid = row["id"]
        if sid not in existing_llm:
            continue
        
        result = existing_llm[sid]
        dec = result.get("llm_decision", "?")
        dec_class = "dec-a" if dec == "A" else ("dec-b" if dec == "B" else "dec-err")
        
        st.markdown(f"""
        <div class="llm-card done">
            <div class="result-row">
                <div style="text-align:center;">
                    <div class="decision-badge {dec_class}">{dec}</div>
                    <div style="font-size:0.7rem; color:#64748b; margin-top:4px;">#{sid}</div>
                </div>
                <div>
                    <div class="sc-title-sm">{row['titlu']}</div>
                    <div class="sc-options-sm">
                        <span style="color:#93c5fd;">A:</span> {row['optiunea_A'][:55]}...<br>
                        <span style="color:#c4b5fd;">B:</span> {row['optiunea_B'][:55]}...
                    </div>
                    <span class="principle-tag">{result.get('llm_moral_principle', '—')}</span>
                </div>
                <div>
                    <div class="reasoning-text">{result.get('llm_reasoning', '—')}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Download
    if os.path.exists(LLM_PATH):
        with open(LLM_PATH, "rb") as f:
            st.download_button(
                "Descarcă CSV răspunsuri AI",
                f,
                file_name="llm_responses.csv",
                mime="text/csv"
            )
