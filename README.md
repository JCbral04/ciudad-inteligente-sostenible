# Ciudad inteligente sostenible — prototipo de sistema distribuido

Propuesta de sostenibilidad tecnológica del taller **Tecnologías emergentes y sostenibles en sistemas distribuidos** (Sistemas Distribuidos, Ingeniería de Software, Universidad Manuela Beltrán).

El programa simula durante 24 horas una plataforma municipal que integra energía, movilidad y residuos, y mide cuánto reducen el consumo de recursos tres estrategias: procesamiento en el borde, autoescalado de microservicios y planificación de cargas según la intensidad de carbono de la red.

## Arquitectura simulada

| Capa | Archivo | Qué hace |
| --- | --- | --- |
| Dispositivos IoT | `sensores.py` | 240 sensores (100 de energía, 60 de movilidad, 80 de residuos), una lectura por minuto |
| Edge Computing | `edge.py` | Promedio por ventana de 5 min, banda muerta, latido cada 30 min y alertas locales |
| Comunicación | `broker.py` | Broker publicación/suscripción que emula MQTT y contabiliza mensajes y bytes |
| Servicios distribuidos | `servicios.py` | Microservicios de energía, movilidad y residuos; pronóstico (Holt) y ruta dinámica |
| Almacenamiento | `servicios.py` (`Almacen`) | Series de tiempo en SQLite |
| Sostenibilidad | `sostenibilidad.py` | Energía de red, autoescalado, planificación por carbono y SCI |

## Ejecución

Requiere Python 3.10 o superior. No usa dependencias externas.

```bash
python main.py
```

Con Docker:

```bash
docker build -t ciudad-sostenible .
docker run --rm ciudad-sostenible
```

El resultado se imprime en consola y se guarda en `reporte.json`.

## Resultados de referencia (semilla 42)

| Indicador | Línea base | Propuesta | Reducción |
| --- | --- | --- | --- |
| Mensajes enviados a la nube por día | 345 600 | 23 285 | 93,3 % |
| Datos transmitidos por día | 52,7 MB | 3,6 MB | 93,2 % |
| Energía de cómputo de los servicios | 16,49 kWh | 10,88 kWh | 34,1 % |
| Emisiones del trabajo por lotes de IA | 2,72 kg CO2e | 1,60 kg CO2e | 41,1 % |
| Recorrido de recolección de residuos | 86,0 km | 58,9 km | 31,5 % |
| SCI (g CO2e por 1 000 lecturas) | 10,50 | 6,92 | 34,1 % |

El consumo de energía reconstruido a partir de los datos filtrados difiere 0,03 % del valor real, de modo que el filtrado no degrada la información útil.

## Supuestos

Todos los parámetros están en `config.py`. Los valores con fuente son el factor de emisión del SIN de Colombia para 2024 (0,220 kg CO2e/kWh; UPME, Resolución 085 de 2026), el PUE promedio global (1,56; Uptime Institute, 2024) y la intensidad eléctrica de la red fija (0,06 kWh/GB; Aslan et al., 2018). La potencia por réplica, la capacidad por réplica, el consumo del camión y el perfil horario de intensidad de carbono son supuestos ilustrativos. El SCI se calcula sin carbono incorporado (M = 0).

## Limitaciones

Es una simulación en un solo proceso: el broker, los nodos edge y los microservicios son clases de Python, no servicios desplegados. En producción se reemplazarían por Mosquitto o EMQX, K3s en los gateways, Kubernetes con HPA/KEDA en la nube y TimescaleDB.
