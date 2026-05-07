import streamlit as st
import pandas as pd
import os
import sys

st.set_page_config(page_title="Analiză — Moral Machine", page_icon="📊", layout="wide")

st.markdown("""
<style>
[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: #f1f5f9;
}
[data-testid="stSidebar"] { background: #0f172a; border-right: 1px solid #1e3a5f; }
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

.metric-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 20px 16px;
    text-align: center;
}
.metric-val {
    font-size: 2.4rem;
    font-weight: 900;
    background: linear-gradient(90deg, #3b82f6, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.metric-label { font-size: 0.85rem; color: #94a3b8; margin-top: 4px; }

.table-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 24px;
}
.match-yes { color: #22c55e; font-weight: 700; }
.match-no  { color: #ef4444; font-weight: 700; }

.comparison-row {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 14px;
}
.comparison-row.match { border-left: 4px solid #22c55e; }
.comparison-row.nomatch { border-left: 4px solid #ef4444; }

.dec-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    border-radius: 10px;
    font-weight: 900;
    font-size: 1.3rem;
    border: 2px solid;
}
.dp-a { background: rgba(59,130,246,0.2); color: #93c5fd; border-color: #3b82f6; }
.dp-b { background: rgba(139,92,246,0.2); color: #c4b5fd; border-color: #8b5cf6; }

.principle-tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #1e3a5f;
    color: #93c5fd;
    border: 1px solid #3b82f6;
}
.page-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #f59e0b, #ef4444);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 8px;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #e2e8f0;
    margin: 24px 0 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.analysis-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
}
.analysis-box p { color: #94a3b8; line-height: 1.7; margin-bottom: 12px; }
.analysis-box strong { color: #e2e8f0; }
</style>
""", unsafe_allow_html=True)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
sys.path.insert(0, BASE_DIR)

SCENARII_PATH = os.path.join(DATA_DIR, "scenarii.csv")
HUMAN_PATH = os.path.join(DATA_DIR, "human_responses.csv")
LLM_PATH = os.path.join(DATA_DIR, "llm_responses.csv")

st.markdown('<div class="page-title">Analiză Comparativă: Om vs. AI</div>', unsafe_allow_html=True)

# ── Check data availability ───────────────────────────────────────────────────
has_human = os.path.exists(HUMAN_PATH)
has_llm = os.path.exists(LLM_PATH)

if not has_human:
    st.warning(" Răspunsurile umane lipsesc. Mergi la **Pagina 2** pentru a le completa.")
if not has_llm:
    st.warning(" Răspunsurile AI lipsesc. Mergi la **Pagina 3** pentru a rula modelul.")
if not has_human and not has_llm:
    st.stop()

# ── Load & merge data ──────────────────────────────────────────────────────────
from utils.analysis import (
    load_data, compute_stats,
    fig_concordanta_pie, fig_principii_bar,
    fig_decizii_grouped, fig_match_by_category,
    export_to_excel
)

df = load_data(SCENARII_PATH, HUMAN_PATH, LLM_PATH)
stats = compute_stats(df)


# ── Comparative table ──────────────────────────────────────────────────────────
st.markdown('<div class="section-title"> Tabel Comparativ Complet</div>', unsafe_allow_html=True)

view_filter = st.radio(
    "Filtrează:",
    ["Toate", " Concordanțe", " Divergențe"],
    horizontal=True
)

display_df = df.copy()
if view_filter == " Concordanțe":
    display_df = df[df.get("match", pd.Series()) == " DA"]
elif view_filter == " Divergențe":
    display_df = df[df.get("match", pd.Series()) == " NU"]

for _, row in display_df.iterrows():
    hd = str(row.get("human_decision", "—")).strip().upper()
    ld = str(row.get("llm_decision", "—")).strip().upper()
    match = row.get("match", "—")
    
    is_match = match == " DA"
    row_class = "comparison-row match" if is_match else ("comparison-row nomatch" if match == "❌ NU" else "comparison-row")
    
    hd_class = "dp-a" if hd == "A" else ("dp-b" if hd == "B" else "")
    ld_class = "dp-a" if ld == "A" else ("dp-b" if ld == "B" else "")
    
    match_icon = "✅" if is_match else ("❌" if match == "❌ NU" else "—")
    
    st.markdown(f"""
    <div class="{row_class}">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
            <div>
                <span style="font-weight:700; color:#e2e8f0; font-size:1rem;">#{int(row['id'])} — {row['titlu']}</span>
                <span style="font-size:0.8rem; color:#64748b; margin-left:8px;">{row['categorie']}</span>
            </div>
            <span style="font-size:1.2rem;">{match_icon} {'Concordanță' if is_match else ('Divergență' if match != '—' else '')}</span>
        </div>
        <div style="font-size:0.82rem; color:#64748b; margin-bottom:12px;">
             {row['descriere'][:120]}...
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px;">
            <div style="background:#0f172a; border-radius:10px; padding:14px;">
                <div style="font-size:0.75rem; color:#64748b; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.05em;">🧑 Decizie Om</div>
                <div style="display:flex; align-items:flex-start; gap:10px;">
                    <div class="dec-pill {hd_class}">{hd if hd in ['A','B'] else '?'}</div>
                    <div style="font-size:0.88rem; color:#94a3b8; line-height:1.5;">{row.get('human_reasoning', '—') or '—'}</div>
                </div>
            </div>
            <div style="background:#0f172a; border-radius:10px; padding:14px;">
                <div style="font-size:0.75rem; color:#64748b; margin-bottom:6px; text-transform:uppercase; letter-spacing:0.05em;">🤖 Decizie AI</div>
                <div style="display:flex; align-items:flex-start; gap:10px;">
                    <div class="dec-pill {ld_class}">{ld if ld in ['A','B'] else '?'}</div>
                    <div>
                        <span class="principle-tag" style="margin-bottom:6px;">⚖️ {row.get('llm_moral_principle', '—') or '—'}</span><br>
                        <span style="font-size:0.88rem; color:#94a3b8; line-height:1.5;">{row.get('llm_reasoning', '—') or '—'}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Auto Analysis ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title"> Analiză Automată</div>', unsafe_allow_html=True)

if stats.get("total_comparate", 0) > 0:
    pct = stats.get("concordanta_pct", 0)
    
    if pct >= 70:
        concordanta_text = f"ridicată ({pct}%), sugerând că AI-ul și omul împărtășesc valori morale similare în majoritate situațiilor"
    elif pct >= 40:
        concordanta_text = f"moderată ({pct}%), indicând atât puncte comune cât și divergențe semnificative"
    else:
        concordanta_text = f"scăzută ({pct}%), evidențiind diferențe fundamentale între raționamentul moral uman și cel al AI"
    
    divergente = df[df.get("match", pd.Series()) == "NU"]["titlu"].tolist() if "match" in df.columns else []
    divergente_str = ", ".join(f"*{t}*" for t in divergente[:5]) if divergente else "—"
    
    principii = stats.get("principii", {})
    top_3 = sorted(principii.items(), key=lambda x: x[1], reverse=True)[:3]
    top_3_str = ", ".join(f"**{p[0]}** ({p[1]} scenarii)" for p in top_3) if top_3 else "—"
    
    st.markdown(f"""
    <div class="analysis-box">
        <p><strong>1. Rata de Concordanță:</strong> Concordanța Om–AI este {concordanta_text}.</p>
        <p><strong>2. Divergențe Notabile:</strong> Cele mai semnificative diferențe s-au înregistrat în scenariile: {divergente_str}. 
        Aceste divergențe reflectă probabil diferențe în modul de ponderare a valorilor — AI-ul tinde să fie mai sistematic și consistent, 
        pe când omul poate fi influențat de empatie sau intuiție contextuală.</p>
        <p><strong>3. Principii Morale AI:</strong> Modelul AI a apelat predominant la: {top_3_str}. 
        Acest lucru sugerează că antrenamentul modelului încorporează o perspectivă mai degrabă {top_3[0][0].lower() if top_3 else 'utilitaristă'}, 
        prioritizând consecințele acțiunilor față de alte considerente morale.</p>
        <p><strong>4. Limitări:</strong> Rezultatele sunt influențate de formularea promptului, de modelul LLM folosit 
        și de subiectivitatea inerentă a răspunsului uman. Un studiu robust ar necesita mai mulți evaluatori umani 
        și multiple rulări ale modelului AI.</p>
    </div>
    """, unsafe_allow_html=True)

