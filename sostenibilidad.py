"""Propuesta de sostenibilidad: métricas de energía y carbono de la plataforma."""
import math
from config import (KWH_POR_GB, FACTOR_EMISION, PUE, CAPACIDAD_REPLICA, REPLICAS_MIN,
                    POTENCIA_REPLICA_W, TRABAJO_LOTES)
from sensores import perfil_movilidad


def energia_red_wh(n_bytes):
    return n_bytes / 1e9 * KWH_POR_GB * 1000


def autoescalado():
    """Compara aprovisionamiento fijo para el pico frente a escalado horizontal por demanda."""
    pico = max(perfil_movilidad(h) for h in range(24))
    demanda = [15_000 + 185_000 * perfil_movilidad(h) / pico for h in range(24)]
    reposo, maximo = POTENCIA_REPLICA_W
    fijas = math.ceil(max(demanda) / CAPACIDAD_REPLICA) + 1            # N+1
    kwh_fijo = kwh_auto = 0.0
    horas_replica = 0
    for d in demanda:
        r = max(REPLICAS_MIN, math.ceil(d / CAPACIDAD_REPLICA))
        horas_replica += r
        for n, acum in ((fijas, "fijo"), (r, "auto")):
            uso = d / (n * CAPACIDAD_REPLICA)
            kwh = n * (reposo + (maximo - reposo) * uso) / 1000 * PUE
            if acum == "fijo":
                kwh_fijo += kwh
            else:
                kwh_auto += kwh
    return {"replicas_fijas": fijas, "horas_replica_fijo": fijas * 24, "horas_replica_auto": horas_replica,
            "kwh_fijo": kwh_fijo, "kwh_auto": kwh_auto}


def intensidad_horaria():
    """Perfil ilustrativo de intensidad de carbono (g CO2e/kWh) con media igual al factor del SIN."""
    forma = [1 + 0.35 * math.exp(-((h - 19.5) ** 2) / 6) - 0.25 * math.exp(-((h - 12) ** 2) / 10)
             - 0.10 * math.exp(-((h - 3) ** 2) / 8) for h in range(24)]
    escala = FACTOR_EMISION * 1000 / (sum(forma) / 24)
    return [f * escala for f in forma]


def planificacion_consciente_del_carbono():
    """Mueve el trabajo por lotes a la ventana de menor intensidad de carbono."""
    g, n, kw = intensidad_horaria(), TRABAJO_LOTES["horas"], TRABAJO_LOTES["kw"] * PUE
    emision = lambda inicio: sum(g[(inicio + i) % 24] for i in range(n)) * kw / 1000    # kg CO2e
    mejor = min(range(24), key=emision)
    return {"inicio_habitual": TRABAJO_LOTES["inicio_habitual"], "inicio_optimo": mejor,
            "kg_habitual": emision(TRABAJO_LOTES["inicio_habitual"]), "kg_optimo": emision(mejor)}


def sci(kwh, unidades_funcionales):
    """Software Carbon Intensity simplificado: (E x I) / R, sin carbono incorporado (M = 0)."""
    return kwh * FACTOR_EMISION * 1000 / unidades_funcionales            # g CO2e por unidad funcional
