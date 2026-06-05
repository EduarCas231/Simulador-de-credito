import streamlit as st
import pandas as pd
from calculo import calcular_tabla, resumen, calcular_tcl

st.set_page_config(page_title="Crédito Personal Banamex", page_icon="🏦", layout="wide")
st.title("🏦 Simulador de Crédito Personal Banamex")
st.caption("Amortización constante · Interés sobre saldo insoluto · IVA sobre intereses · TCL")

# ── Datos personales ──────────────────────────────────────────────────────────
st.subheader("📋 Datos del Solicitante")
c1, c2, c3 = st.columns(3)
nombre     = c1.text_input("Nombre completo")
curp       = c2.text_input("CURP")
rfc        = c3.text_input("RFC")
c4, c5, c6 = st.columns(3)
telefono   = c4.text_input("Teléfono")
correo     = c5.text_input("Correo electrónico")
ocupacion  = c6.selectbox("Ocupación", ["Empleado", "Independiente", "Empresario", "Otro"])

st.divider()

# ── Parámetros del crédito ────────────────────────────────────────────────────
st.subheader("💳 Parámetros del Crédito")
p1, p2, p3, p4 = st.columns(4)

monto  = p1.number_input("Monto del crédito ($)", min_value=5_000.0, max_value=500_000.0,
                          value=50_000.0, step=1_000.0)
tasa   = p2.number_input("Tasa de interés ordinaria anual (%)", min_value=1.0, max_value=100.0,
                          value=36.0, step=0.5)
plazo  = p3.selectbox("Plazo (meses)", [6, 12, 18, 24, 36, 48, 60], index=1)
iva_pct = p4.selectbox("IVA sobre intereses (%)", [0.0, 8.0, 16.0], index=2,
                        format_func=lambda x: f"{x:.0f}%")

st.divider()

# ── Cálculos ──────────────────────────────────────────────────────────────────
tabla = calcular_tabla(monto, tasa, plazo, iva_pct)
res   = resumen(tabla, iva_pct)
tcl   = calcular_tcl(monto, tabla, plazo)

# ── Indicadores clave ─────────────────────────────────────────────────────────
st.subheader("📊 Indicadores Clave")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Pago 1er Mes",      f"${tabla[0]['Pago Total']:,.2f}")
k2.metric("Pago Último Mes",   f"${tabla[-1]['Pago Total']:,.2f}")
k3.metric("Total Pagado",      f"${res['Total Pagado']:,.2f}")
k4.metric("Costo Financiero",  f"${res['Costo Financiero']:,.2f}")
k5.metric("TCL (TEA)",         f"{tcl:.2f}%")

st.divider()

# ── Resumen financiero ────────────────────────────────────────────────────────
st.subheader("💰 Resumen Financiero")
rcols = st.columns(len(res))
for col, (label, valor) in zip(rcols, res.items()):
    col.metric(label, f"${valor:,.2f}")

st.divider()

# ── Tabla de amortización ─────────────────────────────────────────────────────
st.subheader("📅 Tabla de Amortización")
df = pd.DataFrame(tabla)
money_cols = [c for c in df.columns if c != "Mes"]
fmt = {col: "${:,.2f}" for col in money_cols}
st.dataframe(df.style.format(fmt), use_container_width=True)
