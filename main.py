"""Simulación de la plataforma distribuida inteligente y sostenible (ciudad colombiana).

Compara el escenario A (todas las lecturas van directo a la nube) con el escenario B
(procesamiento en el borde) y calcula los indicadores de la propuesta de sostenibilidad.
Uso: python main.py
"""
import json
import random
from config import SEMILLA, MINUTOS, SENSORES, VENTANA_EDGE_MIN, FACTOR_EMISION, LITROS_POR_KM, KG_CO2_POR_LITRO
from sensores import Sensor
from broker import Broker
from edge import NodoEdge
from servicios import Almacen, ServicioEnergia, ServicioMovilidad, ServicioResiduos
import sostenibilidad as sos


def simular():
    rng = random.Random(SEMILLA)
    sensores = [Sensor(t, i, rng) for t, n in SENSORES.items() for i in range(1, n + 1)]
    nube, borde = Broker("A: todo a la nube"), Broker("B: con edge")
    edge, almacen = NodoEdge(borde), Almacen()
    energia, movilidad = ServicioEnergia(), ServicioMovilidad()
    residuos = ServicioResiduos({s.id: s.xy for s in sensores if s.tipo == "residuos"})
    for tipo, servicio in (("energia", energia), ("movilidad", movilidad), ("residuos", residuos)):
        borde.suscribir(tipo, servicio.procesar)
        borde.suscribir(tipo, almacen.guardar)

    kwh_real = 0.0
    for minuto in range(MINUTOS):
        for s in sensores:
            v = s.leer(minuto)
            if s.tipo == "energia":
                kwh_real += v / 60
            nube.publicar(f"ciudad/{s.zona}/{s.tipo}/{s.id}",
                          {"id": s.id, "z": s.zona, "t": minuto, "v": round(v, 2), "u": s.unidad, "a": 0})
            edge.recibir(s, minuto, v)
        if (minuto + 1) % VENTANA_EDGE_MIN == 0:
            energia.cerrar_ventana(minuto)

    auto, lotes, ruta = sos.autoescalado(), sos.planificacion_consciente_del_carbono(), residuos.planificar()
    lecturas = nube.mensajes
    red_a, red_b = sos.energia_red_wh(nube.bytes), sos.energia_red_wh(borde.bytes)
    km_ahorro = ruta["km_ruta_fija"] - ruta["km_ruta_dinamica"]
    return {
        "datos": {"sensores": len(sensores), "lecturas_generadas": lecturas,
                  "mensajes_sin_edge": nube.mensajes, "mensajes_con_edge": borde.mensajes,
                  "reduccion_mensajes_pct": 100 * (1 - borde.mensajes / nube.mensajes),
                  "mb_sin_edge": nube.bytes / 1e6, "mb_con_edge": borde.bytes / 1e6,
                  "reduccion_bytes_pct": 100 * (1 - borde.bytes / nube.bytes),
                  "wh_red_sin_edge": red_a, "wh_red_con_edge": red_b,
                  "registros_almacenados": almacen.contar(),
                  "error_energia_reconstruida_pct": 100 * abs(sum(energia.kwh_hora) - kwh_real) / kwh_real},
        "analitica": {"kwh_dia_medidos": sum(energia.kwh_hora), "mape_pronostico_pct": energia.pronostico(),
                      "hora_pico_movilidad": movilidad.hora_pico(), "alertas_llenado": residuos.alertas},
        "autoescalado": {**auto, "ahorro_pct": 100 * (1 - auto["kwh_auto"] / auto["kwh_fijo"]),
                         "kg_co2e_evitados_dia": (auto["kwh_fijo"] - auto["kwh_auto"]) * FACTOR_EMISION},
        "carbono_lotes": {**lotes, "ahorro_pct": 100 * (1 - lotes["kg_optimo"] / lotes["kg_habitual"])},
        "residuos": {**ruta, "ahorro_km_pct": 100 * km_ahorro / ruta["km_ruta_fija"],
                     "litros_evitados": km_ahorro * LITROS_POR_KM,
                     "kg_co2_evitados": km_ahorro * LITROS_POR_KM * KG_CO2_POR_LITRO},
        "sci_g_co2e_por_1000_lecturas": {
            "linea_base": sos.sci(auto["kwh_fijo"] + red_a / 1000, lecturas / 1000),
            "propuesta": sos.sci(auto["kwh_auto"] + red_b / 1000, lecturas / 1000)},
    }


if __name__ == "__main__":
    reporte = simular()
    for seccion, valores in reporte.items():
        print(f"\n[{seccion}]")
        for clave, valor in valores.items():
            print(f"  {clave:<34} {valor:>12,.2f}" if isinstance(valor, float) else f"  {clave:<34} {valor:>12}")
    with open("reporte.json", "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    print("\nReporte guardado en reporte.json")
