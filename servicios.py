"""Capa de servicios distribuidos: microservicios de dominio, analítica (IA) y almacenamiento."""
import math
import sqlite3
from collections import defaultdict
from config import VENTANA_EDGE_MIN, UMBRAL_RUTA


class Almacen:
    """Base de datos de series de tiempo (SQLite como sustituto local de TimescaleDB)."""
    def __init__(self, ruta=":memory:"):
        self.db = sqlite3.connect(ruta)
        self.db.execute("CREATE TABLE IF NOT EXISTS lecturas(id TEXT, zona TEXT, minuto INT, valor REAL, alerta INT)")

    def guardar(self, m):
        self.db.execute("INSERT INTO lecturas VALUES (?,?,?,?,?)", (m["id"], m["z"], m["t"], m["v"], m["a"]))

    def contar(self):
        return self.db.execute("SELECT COUNT(*) FROM lecturas").fetchone()[0]


class ServicioEnergia:
    def __init__(self):
        self.ultimo, self.kwh_hora = {}, [0.0] * 24

    def procesar(self, m):
        self.ultimo[m["id"]] = m["v"]

    def cerrar_ventana(self, minuto):                      # reconstrucción por retención del último valor
        self.kwh_hora[minuto // 60] += sum(self.ultimo.values()) * VENTANA_EDGE_MIN / 60

    def pronostico(self, alfa=0.9, beta=0.7):
        """Suavizado exponencial doble (Holt), un paso adelante. Devuelve el MAPE en %."""
        nivel, tend, errores = self.kwh_hora[0], 0.0, []
        for real in self.kwh_hora[1:]:
            pred = nivel + tend
            errores.append(abs(real - pred) / real)
            nuevo = alfa * real + (1 - alfa) * (nivel + tend)
            tend, nivel = beta * (nuevo - nivel) + (1 - beta) * tend, nuevo
        return 100 * sum(errores) / len(errores)


class ServicioMovilidad:
    def __init__(self):
        self.flujo = defaultdict(lambda: [0.0] * 24)       # zona -> veh/min acumulado por hora
        self.n = defaultdict(lambda: [0] * 24)

    def procesar(self, m):
        h = m["t"] // 60
        self.flujo[m["z"]][h] += m["v"]
        self.n[m["z"]][h] += 1

    def hora_pico(self):
        total = [sum(self.flujo[z][h] / max(self.n[z][h], 1) for z in self.flujo) for h in range(24)]
        return max(range(24), key=total.__getitem__)


class ServicioResiduos:
    def __init__(self, coordenadas):
        self.xy, self.nivel, self.alertas = coordenadas, {}, 0

    def procesar(self, m):
        self.nivel[m["id"]] = m["v"]
        self.alertas += m["a"]

    @staticmethod
    def _ruta_km(puntos):                                  # heurística del vecino más cercano
        actual, km, pendientes = (0.0, 0.0), 0.0, list(puntos)
        while pendientes:
            sig = min(pendientes, key=lambda p: math.dist(actual, p))
            km += math.dist(actual, sig)
            actual = sig
            pendientes.remove(sig)
        return km + math.dist(actual, (0.0, 0.0))

    def planificar(self):
        llenos = [i for i, v in self.nivel.items() if v >= UMBRAL_RUTA]
        return {"contenedores_ruta_fija": len(self.xy), "contenedores_ruta_dinamica": len(llenos),
                "km_ruta_fija": self._ruta_km(self.xy.values()),
                "km_ruta_dinamica": self._ruta_km([self.xy[i] for i in llenos])}
