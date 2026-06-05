def calcular_tabla(monto_autorizado: float, tasa_anual: float, plazo_meses: int, comision_apertura_pct: float, iva_general_pct: float) -> tuple[list[dict], float]:
    comision_base = monto_autorizado * (comision_apertura_pct / 100)
    comision_con_iva = comision_base * (1 + (iva_general_pct / 100))
    total_a_financiar = monto_autorizado + comision_con_iva
    
    tasa_mensual = tasa_anual / 12 / 100
    saldo = total_a_financiar
    tabla = []

    if tasa_mensual > 0:
        pago_fijo_mensual = total_a_financiar * (tasa_mensual * (1 + tasa_mensual) ** plazo_meses) / ((1 + tasa_mensual) ** plazo_meses - 1)
    else:
        pago_fijo_mensual = total_a_financiar / plazo_meses

    for mes in range(1, plazo_meses + 1):
        interes_ordinario = saldo * tasa_mensual
        iva_intereses = interes_ordinario * (iva_general_pct / 100)
        pago_capital = pago_fijo_mensual - interes_ordinario
        pago_mensual_total = pago_fijo_mensual + iva_intereses
        
        saldo_anterior = saldo
        saldo -= pago_capital

        tabla.append({
            "Mes": mes,
            "Saldo de Capital": saldo_anterior,
            "Pago a Capital": pago_capital,
            "Pago de Interés Ordinarios": interes_ordinario,
            "Pago Fijo Mensual": pago_fijo_mensual,
            "Pago IVA Intereses*": iva_intereses,
            "Pago Mensual Total**": pago_mensual_total,
            "Prepagos": ""
        })

    return tabla, comision_con_iva


def resumen(tabla: list[dict], comision_con_iva: float) -> dict:
    total_capital = sum(r["Pago a Capital"] for r in tabla)
    total_interes = sum(r["Pago de Interés Ordinarios"] for r in tabla)
    total_iva = sum(r["Pago IVA Intereses*"] for r in tabla)
    total_pagado = sum(r["Pago Mensual Total**"] for r in tabla)
    
    return {
        "Monto Autorizado": total_capital - comision_con_iva,
        "Comisión Apertura (c/IVA)": comision_con_iva,
        "Total a Financiar": total_capital,
        "Total Intereses": total_interes,
        "Total IVA Intereses": total_iva,
        "Total Pagado": total_pagado,
    }


def calcular_cat(monto_recibido: float, tabla: list[dict], plazo_meses: int) -> float:
    pagos = [r["Pago Mensual Total**"] for r in tabla]
    tasa_id = 0.02

    for _ in range(100):
        f = sum(pagos[t] / (1 + tasa_id) ** (t + 1) for t in range(plazo_meses)) - monto_recibido
        df = sum(-(t + 1) * pagos[t] / (1 + tasa_id) ** (t + 2) for t in range(plazo_meses))
        if df == 0:
            break
        tasa_id_nueva = tasa_id - f / df
        if abs(tasa_id_nueva - tasa_id) < 1e-7:
            tasa_id = tasa_id_nueva
            break
        tasa_id = tasa_id_nueva

    return ((1 + tasa_id) ** 12 - 1) * 100