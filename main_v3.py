import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calcolo ENPAP Forfettario", layout="centered")
st.title("Calcolo netto ENPAP (forfettario)")

# =========================
# PARAMETRI ENPAP (AGGIORNA SE CAMBIANO)
# =========================
MIN_SOGGETTIVO = 856.0      # esempio
MIN_INTEGRATIVO = 150.0     # dal testo che hai incollato (se diverso, cambia qui)
MATERNITA = 91.0            # inserisci valore corretto dell'anno

# Integrativo deducibile? prudenza: no
INTEGRATIVO_DEDUCIBILE = False

st.caption(
    "Assunzioni: separazione incassi PRIVATI (rivalsa 4%) e PA (rivalsa 2%). "
    "Regime forfettario: imponibile = (compenso base × coeff. redditività) - contributi deducibili."
)

# =========================
# INPUT
# =========================
R_priv = st.slider("Incassi PRIVATI annui (includono 4% integrativo) €", 0, 200000, 40000, 500)
R_pa   = st.slider("Incassi PA annui (includono 2% integrativo) €", 0, 200000, 12000, 500)

spese_studio = st.slider("Spese fisse di studio annue €", 0, 100000, 0, 500)
soggettivo_pct = st.slider("% contributo soggettivo ENPAP", 10, 30, 10, 1)

st.divider()

aliquota_imposta = st.number_input(
    "Aliquota imposta sostitutiva (es. 0.15 = 15%)",
    min_value=0.0, max_value=0.5, value=0.15, step=0.01, format="%.2f"
)
coeff_redd = st.number_input(
    "Coeff. redditività (es. 0.78)",
    min_value=0.40, max_value=1.00, value=0.78, step=0.01, format="%.2f"
)

# =========================
# CALCOLI: basi e integrativo
# =========================
# Ricostruisci i compensi base (al netto della rivalsa)
base_priv = R_priv / 1.04 if R_priv > 0 else 0.0
base_pa   = R_pa   / 1.02 if R_pa > 0 else 0.0

# Integrativo dovuto
integr_priv = 0.04 * base_priv
integr_pa   = 0.02 * base_pa
integrativo_tot = integr_priv + integr_pa

# Applica minimo integrativo complessivo (se previsto come minimo annuo totale)
if (R_priv + R_pa) > 0:
    integrativo_tot = max(integrativo_tot, MIN_INTEGRATIVO)

# Quota integrativo che va a MONTANTE (dal tuo testo: 2% a montante quando l'integrativo è 4%)
quota_integrativo_a_montante = 0.02 * base_priv  # = 50% dell'integrativo privati

# =========================
# CALCOLI: forfettario e soggettivo
# =========================
incassi_tot = R_priv + R_pa
compenso_base_tot = base_priv + base_pa

base_forf = compenso_base_tot * coeff_redd

soggettivo = max((soggettivo_pct / 100.0) * base_forf, MIN_SOGGETTIVO)
maternita = MATERNITA

contributi_tot = soggettivo + integrativo_tot + maternita

# Deducibili: soggettivo + maternità (+ integrativo se mai deducibile)
deducibili = soggettivo + maternita + (integrativo_tot if INTEGRATIVO_DEDUCIBILE else 0.0)

imponibile = max(base_forf - deducibili, 0.0)
imposta = aliquota_imposta * imponibile

netto_annuo_lordo_spese = incassi_tot - contributi_tot - imposta
netto_annuo_netto_spese = netto_annuo_lordo_spese - spese_studio

# Contributi che incrementano il montante (stima, da regola: soggettivo + quota integrativo montante)
contributi_a_montante = soggettivo + quota_integrativo_a_montante

# =========================
# OUTPUT (METRICHE)
# =========================
c1, c2, c3 = st.columns(3)
c1.metric("Integrativo PRIVATI (4%)", f"{integr_priv:,.0f} €".replace(",", "."))
c2.metric("Integrativo PA (2%)", f"{integr_pa:,.0f} €".replace(",", "."))
c3.metric("Quota integrativo a montante", f"{quota_integrativo_a_montante:,.0f} €".replace(",", "."))

c4, c5, c6 = st.columns(3)
c4.metric("Soggettivo ENPAP", f"{soggettivo:,.0f} €".replace(",", "."))
c5.metric("Maternità ENPAP", f"{maternita:,.0f} €".replace(",", "."))
c6.metric("Totale contributi ENPAP", f"{contributi_tot:,.0f} €".replace(",", "."))

c7, c8 = st.columns(2)
c7.metric("Imposta dovuta", f"{imposta:,.0f} €".replace(",", "."))
c8.metric("Contributi che incrementano montante", f"{contributi_a_montante:,.0f} €".replace(",", "."))

c9, c10 = st.columns(2)
c9.metric("Netto mensile (lordo spese studio)", f"{netto_annuo_lordo_spese/12:,.0f} €".replace(",", "."))
c10.metric("Netto mensile (netto spese studio)", f"{netto_annuo_netto_spese/12:,.0f} €".replace(",", "."))

# =========================
# DETTAGLIO
# =========================
df = pd.DataFrame([{
    "Incassi PRIVATI (incl. 4%)": R_priv,
    "Incassi PA (incl. 2%)": R_pa,
    "Incassi totali": incassi_tot,
    "Base privati (R/1,04)": round(base_priv, 2),
    "Base PA (R/1,02)": round(base_pa, 2),
    "Compenso base totale": round(compenso_base_tot, 2),
    "Coeff. redditività": round(coeff_redd, 2),
    "Base forfettaria": round(base_forf, 2),
    "% soggettivo": soggettivo_pct,
    "Soggettivo": round(soggettivo, 2),
    "Integrativo privati (4%)": round(integr_priv, 2),
    "Integrativo PA (2%)": round(integr_pa, 2),
    "Integrativo totale (min applicato)": round(integrativo_tot, 2),
    "Quota integrativo a montante": round(quota_integrativo_a_montante, 2),
    "Maternità": round(maternita, 2),
    "Totale contributi": round(contributi_tot, 2),
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
- Gli **incassi** sono separati: PRIVATI (rivalsa 4%) e PA (rivalsa 2%).
- **Totale contributi ENPAP** = soggettivo + integrativo totale + maternità.
- **Contributi che incrementano montante** (stima) = soggettivo + quota integrativo a montante (2% dei privati).
- Le **spese di studio** riducono solo il netto disponibile, non l’imponibile forfettario.
""")
