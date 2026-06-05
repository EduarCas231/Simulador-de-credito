def calcular_tabla(monto: float, tasa_anual: float, plazo_meses: int, iva_pct: float) -> list[dict]:
    tasa_mensual = tasa_anual / 12 / 100
    pago_capital = monto / plazo_meses
    saldo = monto
    tabla = []

    for mes in range(1, plazo_meses + 1):
        interes = saldo * tasa_mensual
        iva = interes * (iva_pct / 100)
        pago_total = pago_capital + interes + iva
        saldo -= pago_capital

        tabla.append({
            "Mes": mes,
            "Saldo Inicial": saldo + pago_capital,
            "Pago Capital": pago_capital,
            "Interés": interes,
            f"IVA ({iva_pct:.0f}%)": iva,
            "Pago Total": pago_total,
            "Saldo Final": max(saldo, 0.0),
        })

    return tabla


def resumen(tabla: list[dict], iva_pct: float) -> dict:
    total_capital = sum(r["Pago Capital"] for r in tabla)
    total_interes = sum(r["Interés"] for r in tabla)
    total_iva = sum(r[f"IVA ({iva_pct:.0f}%)"] for r in tabla)
    total_pagado = sum(r["Pago Total"] for r in tabla)
    return {
        "Total Capital": total_capital,
        "Total Intereses": total_interes,
        f"Total IVA ({iva_pct:.0f}%)": total_iva,
        "Total Pagado": total_pagado,
        "Costo Financiero": total_pagado - total_capital,
    }


def calcular_tcl(monto: float, tabla: list[dict], plazo_meses: int) -> float:
    """
    Calcula el TCL (Tasa de Costo Total) mensual usando Newton-Raphson,
    luego lo convierte a tasa anual efectiva.
    Resuelve: monto = Σ pago_total_t / (1 + tcl_mensual)^t
    """
    pagos = [r["Pago Total"] for r in tabla]
    tcl = 0.03  # estimado inicial mensual

    for _ in range(1000):
        f = sum(pagos[t] / (1 + tcl) ** (t + 1) for t in range(plazo_meses)) - monto
        df = sum(-(t + 1) * pagos[t] / (1 + tcl) ** (t + 2) for t in range(plazo_meses))
        if df == 0:
            break
        tcl_nuevo = tcl - f / df
        if abs(tcl_nuevo - tcl) < 1e-10:
            tcl = tcl_nuevo
            break
        tcl = tcl_nuevo

    return ((1 + tcl) ** 12 - 1) * 100  # TEA %
