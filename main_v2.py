import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calcolo ENPAP Forfettario", layout="centered")
st.title("Calcolo netto ENPAP (forfettario)")

# =========================
# Parametri ENPAP (MODIFICA QUI se cambiano anno/valori)
# =========================
ALIQUOTA_INTEGRATIVO = 0.02
MIN_INTEGRATIVO = 66.0
MIN_SOGGETTIVO = 856.0

# Prudenza: integrativo NON deducibile (di norma è rivalsa in fattura)
INTEGRATIVO_DEDUCIBILE = False

st.caption(
    "Assunzioni: Incassi annui includono la rivalsa 2% ENPAP. "
    "Regime forfettario: imponibile = (compenso base × coeff. redditività) - contributi deducibili."
)

# =========================
# Input UI
# =========================
incassi_R = st.slider("Incassi annui (includono 2% integrativo) €", 0, 85000, 48000, 500)
spese_studio = st.slider("Spese fisse di studio annue €", 0, 30000, 0, 500)
soggettivo_pct = st.slider("% contributo soggettivo ENPAP", 10, 30, 20, 1)

st.divider()

# Campi editabili (meno rischiosi di uno slider)
aliquota_imposta = st.number_input(
    "Aliquota imposta sostitutiva (es. 0.15 = 15%)",
    min_value=0.0, max_value=0.5, value=0.15, step=0.01, format="%.2f"
)

coeff_redd = st.number_input(
    "Coeff. redditività (es. 0.78)",
    min_value=0.40, max_value=1.00, value=0.78, step=0.01, format="%.2f"
)

# =========================
# Calcoli
# =========================
# Incassi includono rivalsa: R = compenso_base * (1 + 0.02)
compenso_base = incassi_R / (1.0 + ALIQUOTA_INTEGRATIVO) if (1.0 + ALIQUOTA_INTEGRATIVO) else incassi_R

integrativo = max(ALIQUOTA_INTEGRATIVO * compenso_base, MIN_INTEGRATIVO)
base_forf = compenso_base * coeff_redd

soggettivo = max((soggettivo_pct / 100.0) * base_forf, MIN_SOGGETTIVO)

# >>> Questo è ciò che versi alla cassa (ENPAP): soggettivo + integrativo (qui NON includiamo quote facoltative)
contributi_tot = soggettivo + integrativo

deducibili = soggettivo + (integrativo if INTEGRATIVO_DEDUCIBILE else 0.0)
imponibile = max(base_forf - deducibili, 0.0)
imposta = aliquota_imposta * imponibile

netto_annuo_lordo_spese = incassi_R - contributi_tot - imposta
netto_annuo_netto_spese = netto_annuo_lordo_spese - spese_studio

# =========================
# Output "in grande"
# =========================
colA, colB = st.columns(2)
colA.metric("Totale contributi ENPAP da versare", f"{contributi_tot:,.0f} €".replace(",", "."))
colB.metric("Imposta dovuta (forfettario)", f"{imposta:,.0f} €".replace(",", "."))

col1, col2 = st.columns(2)
col1.metric("Netto mensile (lordo spese studio)", f"{netto_annuo_lordo_spese/12:,.0f} €".replace(",", "."))
col2.metric("Netto mensile (netto spese studio)", f"{netto_annuo_netto_spese/12:,.0f} €".replace(",", "."))

# Tabella dettagli
df = pd.DataFrame([{
    "Incassi annui (R)": incassi_R,
    "Compenso base (R/1,02)": round(compenso_base, 2),
    "Coeff. redditività": round(coeff_redd, 2),
    "Base forfettaria": round(base_forf, 2),
    "% soggettivo": soggettivo_pct,
    "Soggettivo": round(soggettivo, 2),
    "Integrativo (2%)": round(integrativo, 2),
    "Totale contributi ENPAP": round(contributi_tot, 2),
    "Deducibili usati": round(deducibili, 2),
    "Imponibile forf": round(imponibile, 2),
    "Aliquota imposta": round(aliquota_imposta, 2),
    "Imposta": round(imposta, 2),
    "Spese studio": round(spese_studio, 2),
    "Netto annuo (lordo spese)": round(netto_annuo_lordo_spese, 2),
    "Netto annuo (netto spese)": round(netto_annuo_netto_spese, 2),
}])

st.dataframe(df, use_container_width=True)

with st.expander("Note"):
    st.write("""
- **Totale contributi ENPAP da versare** = soggettivo + integrativo (nessuna quota facoltativa inclusa).
- Le **spese di studio** qui riducono solo il tuo netto disponibile, non l’imponibile forfettario (che usa il coefficiente di redditività).
- Se vuoi un bottone “Ripristina valori standard” per aliquota e coefficiente, lo aggiungo.
""")
