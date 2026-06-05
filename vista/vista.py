import streamlit as st
import pandas as pd
from calculo import calcular_tabla, resumen, calcular_cat

LOGO_URL = "https://images.seeklogo.com/logo-png/1/2/banamex-logo-png_seeklogo-15893.png"
st.set_page_config(page_title="Crédito Personal Banamex", page_icon=LOGO_URL, layout="wide")

st.markdown("""
    <style>
    .banamex-header {
        background-color: #002F6C;
        color: white;
        padding: 8px 12px;
        font-weight: bold;
        font-size: 18px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    .nota-roja {
        border: 2px solid #A52A2A;
        padding: 10px 14px;
        border-radius: 4px;
        font-size: 13px;
        color: white;
        margin-bottom: 8px;
    }
    .nota-azul {
        background-color: #002F6C;
        color: white;
        padding: 6px 12px;
        font-weight: bold;
        font-size: 14px;
        margin-bottom: 6px;
    }
    .cuadro-instrucciones {
        border: 2px solid #8B4513;
        padding: 15px;
        border-radius: 4px;
        color: white;
        font-size: 13px;
        margin-top: 10px;
    }
    .resultado-calc {
        background-color: #1a1a2e;
        border: 1px solid #FFD700;
        color: #FFD700;
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 15px;
        text-align: center;
        margin-top: 4px;
    }
    input[type="text"], input[type="number"] {
        background-color: #FFFF99 !important;
        color: #000 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    f'<div style="display:flex; align-items:center; gap:14px; margin-bottom:8px;">'
    f'<span style="font-size:26px; font-weight:bold;">CRÉDITO PERSONAL</span>'
    f'<img src="{LOGO_URL}" style="height:150px; object-fit:contain;">'
    f'</div>',
    unsafe_allow_html=True
)


if "limpiar" not in st.session_state:
    st.session_state.limpiar = False

if st.session_state.limpiar:
    st.session_state.limpiar   = False
    st.session_state.nombre    = ""
    st.session_state.monto     = 0.0
    st.session_state.comision  = 0.0
    st.session_state.plazo     = 6
    st.session_state.tasa      = 15.0
    st.session_state.cat_sel   = 15.0

iva_general = 16.0
COMISIONES  = [0.0, 1.0, 2.0, 3.0]
PLAZOS      = [6, 12, 18, 24, 36, 48, 60]
TASAS       = [15.0, 20.0, 25.0, 30.0, 35.0, 40.0]

st.markdown('<div class="banamex-header">DATOS DEL CRÉDITO</div>', unsafe_allow_html=True)

col_form, col_btns = st.columns([5, 1])

with col_btns:
    btn_cotizar = st.button("Cotiza",   use_container_width=True)
    btn_limpiar = st.button("Limpiar",  use_container_width=True)

if btn_limpiar:
    st.session_state.limpiar = True
    st.rerun()

with col_form:

    nombre = st.text_input("Nombre del cliente:", value=st.session_state.get("nombre", ""))

    monto_autorizado = st.number_input(
        "Monto autorizado ($):",
        min_value=0.0, value=st.session_state.get("monto", 0.0),
        step=5000.0, format="%.2f"
    )

    c_com, c_res_com = st.columns([2, 1])
    with c_com:
        comision_pct = st.selectbox(
            "Comisión por apertura con IVA:",
            COMISIONES, format_func=lambda x: f"{x:.0f}%",
            index=COMISIONES.index(st.session_state.get("comision", 0.0))
        )
    comision_con_iva = monto_autorizado * (comision_pct / 100) * (1 + iva_general / 100)
    with c_res_com:
        st.write("Comisión calculada:")
        st.markdown(f'<div class="resultado-calc">${comision_con_iva:,.2f}</div>', unsafe_allow_html=True)

    total_financiar = monto_autorizado + comision_con_iva
    st.markdown(f"**Total a financiar:** &nbsp; <span style='color:#FFD700; font-size:16px; font-weight:bold'>${total_financiar:,.2f}</span>", unsafe_allow_html=True)

    st.write("")

    plazo = st.selectbox(
        "Plazo del crédito:",
        PLAZOS, format_func=lambda x: f"{x} meses",
        index=PLAZOS.index(st.session_state.get("plazo", 6))
    )

    tasa_anual = st.selectbox(
        "Tasa de interés anual:",
        TASAS, format_func=lambda x: f"{x:.0f}%",
        index=TASAS.index(st.session_state.get("tasa", 15.0))
    )

    cat_opciones = [15.0, 20.0, 25.0, 29.0, 30.0, 35.0, 40.0, 45.0, 50.0]
    cat_sel = st.selectbox(
        "CAT (Costo Anual Total):",
        cat_opciones, format_func=lambda x: f"{x:.1f}%",
        index=cat_opciones.index(st.session_state.get("cat_sel", 15.0)) if st.session_state.get("cat_sel", 15.0) in cat_opciones else 0
    )

tabla_datos, comision_calc = calcular_tabla(monto_autorizado, tasa_anual, plazo, comision_pct, iva_general)
res       = resumen(tabla_datos, comision_calc)
cat_calc  = calcular_cat(monto_autorizado, tabla_datos, plazo)
pago_por_mil = (tabla_datos[0]["Pago Fijo Mensual"] / res["Total a Financiar"]) * 1000 if res["Total a Financiar"] > 0 else 0.0

st.markdown("---")
st.markdown('<div class="banamex-header">RESUMEN DE CÁLCULOS</div>', unsafe_allow_html=True)

r1, r2, r3, r4 = st.columns(4)
with r1:
    st.metric("Comisión con IVA",    f"${comision_con_iva:,.2f}")
with r2:
    st.metric("Total a financiar",   f"${total_financiar:,.2f}")
with r3:
    st.metric("Pago por mil",        f"${pago_por_mil:,.2f}")
with r4:
    st.metric("CAT calculado",       f"{cat_calc:.1f}%")

st.write("")
n1, n2 = st.columns(2)
with n1:
    st.markdown('<div class="nota-roja"><b>El monto otorgado puede variar dependiendo de la capacidad de pago del cliente</b></div>', unsafe_allow_html=True)
with n2:
    st.markdown('<div class="nota-roja"><b>La tasa de interés es de referencia, la tasa se otorga en base a evaluación crediticia</b></div>', unsafe_allow_html=True)

st.write("")
st.markdown('<div class="nota-azul">Notas:</div>', unsafe_allow_html=True)
st.markdown("<span style='color:red; font-weight:bold;'>- Recuerda que Top Up no cobra comisión por apertura (0%)</span>", unsafe_allow_html=True)
st.write("")

st.markdown("""
<div class="cuadro-instrucciones">
    <p style='margin: 0;'>- Elige la comisión, el plazo y la tasa de referencia desplegando los combos (presiona la flecha).</p>
    <p style='margin: 5px 0;'>- La tasa de interés es de referencia, ésta se otorgará en base a evaluación crediticia.</p>
    <p style='margin: 5px 0;'>- El monto otorgado puede variar dependiendo de la capacidad de pago del cliente.</p>
    <p style='margin: 0;'>- Para ver tu cotización presiona el botón <b>Cotiza</b>.</p>
</div>
""", unsafe_allow_html=True)

if btn_cotizar:
    errores = []
    if not nombre.strip():
        errores.append("⚠️ El nombre del cliente es obligatorio.")
    if monto_autorizado <= 0:
        errores.append("⚠️ El monto autorizado debe ser mayor a $0.")

    if errores:
        for e in errores:
            st.error(e)
    else:
        st.write("")
        st.markdown('<div class="banamex-header">Cotización Generada</div>', unsafe_allow_html=True)
        df = pd.DataFrame(tabla_datos)
        money_cols = ["Saldo de Capital", "Pago a Capital", "Pago de Interés Ordinarios",
                      "Pago Fijo Mensual", "Pago IVA Intereses*", "Pago Mensual Total**"]
        fmt = {col: "${:,.2f}" for col in money_cols}
        st.dataframe(df.style.format(fmt), use_container_width=True, hide_index=True)
