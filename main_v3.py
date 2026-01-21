import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calcolo ENPAP Forfettario", layout="centered")
st.title("Calcolo netto ENPAP (forfettario)")

# =========================
# PARAMETRI ENPAP (AGGIORNA SE CAMBIANO ANNO/VALORI)
# =========================
ALIQUOTA_INTEGRATIVO = 0.02

MIN_SOGGETTIVO = 856.0      # <-- aggiorna con valore corretto annuo
MIN_INTEGRATIVO = 66.0      # <-- aggiorna con valore corretto annuo
MATERNITA = 91.0            # <-- aggiorna con valore corretto annuo (iscrizione annuale)

# Prudenza: integrativo NON deducibile (rivalsa in fattura)
INTEGRATIVO_DEDUCIBILE = False

st.caption(
    "Assunzioni: Incassi annui (R) includono già la rivalsa ENPAP 2% (contributo integrativo). "
    "Regime forfettario: imponibile = (compenso base × coeff. redditività) - contributi deducibili."
)

# =========================
# INPUT
# =========================
incassi_R = st.slider("Incassi annui (R) € — includono già il 2% integrativo ENPAP", 0, 85000, 52000, 500)
spese_studio = st.slider("Spese fisse di studio annue €", 0, 50000, 12000, 500)
soggettivo_pct = st.slider("% contributo soggettivo ENPAP", 10, 30, 18, 2)

# --- Warning regime forfettario (soglie 85k / 100k) ---
st.divider()
st.info(f"Incassi totali (inclusa rivalsa integrativo): {incassi_R:,.0f} €".replace(",", "."))

if incassi_R > 100000:
    st.error("⚠️ Superi €100.000: in genere si esce dal forfettario in corso d'anno (attenzione a IVA/adempimenti).")
elif incassi_R > 85000:
    st.warning("⚠️ Superi €85.000: in genere si esce dal forfettario dall'anno successivo (se resti ≤ €100.000).")
else:
    st.success("✅ Entro il limite €85.000 per permanenza nel forfettario.")

st.divider()

# Campi editabili (non slider, così non si “sballano” per errore)
aliquota_imposta = st.number_input(
    "Aliquota imposta sostitutiva (es. 0.15 = 15%)",
    min_value=0.0, max_value=0.5, value=0.15, step=0.01, format="%.2f"
)
coeff_redd = st.number_input(
    "Coeff. redditività (es. 0.78)",
    min_value=0.40, max_value=1.00, value=0.78, step=0.01, format="%.2f"
)

# =========================
# CALCOLI
# =========================
# Se incassi includono rivalsa integrativo: R = compenso_base * (1 + 0.02)
compenso_base = incassi_R / (1.0 + ALIQUOTA_INTEGRATIVO) if (1.0 + ALIQUOTA_INTEGRATIVO) else incassi_R

# Integrativo dovuto: 2% del compenso base (con minimo)
integrativo = max(ALIQUOTA_INTEGRATIVO * compenso_base, MIN_INTEGRATIVO)

# Reddito forfettario "figurativo"
base_forf = compenso_base * coeff_redd

# Soggettivo: % scelta sulla base forf (con minimo)
soggettivo = max((soggettivo_pct / 100.0) * base_forf, MIN_SOGGETTIVO)

# Maternità: quota fissa annuale
maternita = MATERNITA

# Totale contributi ENPAP da versare
contributi_tot = soggettivo + integrativo + maternita

# Deducibili per imposta sostitutiva: soggettivo + maternità (+ integrativo se mai deducibile)
deducibili = soggettivo + maternita + (integrativo if INTEGRATIVO_DEDUCIBILE else 0.0)

imponibile = max(base_forf - deducibili, 0.0)
imposta = aliquota_imposta * imponibile

netto_annuo_lordo_spese = incassi_R - contributi_tot - imposta
netto_annuo_netto_spese = netto_annuo_lordo_spese - spese_studio

# =========================
# OUTPUT (METRICHE GRANDI)
# =========================
c1, c2, c3 = st.columns(3)
c1.metric("Soggettivo ENPAP", f"{soggettivo:,.0f} €".replace(",", "."))
c2.metric("Integrativo ENPAP (2%)", f"{integrativo:,.0f} €".replace(",", "."))
c3.metric("Maternità ENPAP", f"{maternita:,.0f} €".replace(",", "."))

c4, c5 = st.columns(2)
c4.metric("Totale contributi ENPAP da versare", f"{contributi_tot:,.0f} €".replace(",", "."))
c5.metric("Imposta dovuta (forfettario)", f"{imposta:,.0f} €".replace(",", "."))

c6, c7 = st.columns(2)
c6.metric("Netto mensile (lordo spese studio)", f"{netto_annuo_lordo_spese/12:,.0f} €".replace(",", "."))
c7.metric("Netto mensile (netto spese studio)", f"{netto_annuo_netto_spese/12:,.0f} €".replace(",", "."))

# =========================
# DETTAGLIO
# =========================
df = pd.DataFrame([{
    "Incassi annui (R)": incassi_R,
    "Compenso base (R/1,02)": round(compenso_base, 2),
    "Coeff. redditività": round(coeff_redd, 2),
    "Base forfettaria": round(base_forf, 2),
    "% soggettivo": soggettivo_pct,
    "Contributo soggettivo": round(soggettivo, 2),
    "Contributo integrativo (2%)": round(integrativo, 2),
    "Contributo maternità": round(maternita, 2),
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
- Qui **Incassi (R)** includono la rivalsa **integrativo 2%**.
- **Totale contributi ENPAP** = soggettivo + integrativo + maternità (iscrizione annuale).
- Le **spese di studio** riducono il netto disponibile ma non l’imponibile forfettario (coeff. redditività).
""")
