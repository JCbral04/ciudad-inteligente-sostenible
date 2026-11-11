"""Parámetros de la simulación. Todos los supuestos son configurables."""
SEMILLA = 42
MINUTOS = 24 * 60                      # un día, una lectura por sensor cada minuto
SENSORES = {"energia": 100, "movilidad": 60, "residuos": 80}
ZONAS = 6

# --- Capa edge ---
VENTANA_EDGE_MIN = 5                   # agregación local (promedio) cada 5 min
BANDA_MUERTA = {"energia": ("rel", 0.03), "movilidad": ("rel", 0.10), "residuos": ("abs", 2.0)}
LATIDO_MIN = 30                        # envío obligatorio aunque no haya cambios
UMBRAL_LLENADO = 80.0                  # % de llenado que dispara alerta local
SOBRECARGA_BYTES = 60                  # cabeceras MQTT/TLS/TCP/IP aproximadas por mensaje

# --- Sostenibilidad ---
KWH_POR_GB = 0.06                      # intensidad eléctrica de la red fija (Aslan et al., 2018)
FACTOR_EMISION = 0.220                 # kg CO2e/kWh, SIN Colombia 2024 (UPME, Res. 085 de 2026)
PUE = 1.56                             # promedio global de centros de datos (Uptime Institute, 2024)
CAPACIDAD_REPLICA = 50_000             # peticiones/hora que atiende una réplica (supuesto)
REPLICAS_MIN = 2                       # alta disponibilidad
POTENCIA_REPLICA_W = (60, 150)         # consumo en reposo y a plena carga (supuesto)
TRABAJO_LOTES = {"horas": 3, "kw": 2.0, "inicio_habitual": 18}   # reentrenamiento del modelo de IA
UMBRAL_RUTA = 75.0                     # se recogen solo contenedores con llenado >= 75 %
LITROS_POR_KM = 0.5                    # camión recolector (supuesto)
KG_CO2_POR_LITRO = 2.68                # diésel (supuesto de referencia)
