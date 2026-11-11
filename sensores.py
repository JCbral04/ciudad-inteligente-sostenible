"""Capa de dispositivos IoT: sensores simulados de energía, movilidad y residuos."""
import math
from config import ZONAS


def perfil_energia(h):
    return 0.35 + 0.65 * math.exp(-((h - 19.5) ** 2) / 8) + 0.25 * math.exp(-((h - 7) ** 2) / 6)


def perfil_movilidad(h):
    return 0.08 + math.exp(-((h - 7.5) ** 2) / 3) + 0.9 * math.exp(-((h - 18) ** 2) / 4)


class Sensor:
    def __init__(self, tipo, n, rng):
        self.tipo, self.rng = tipo, rng
        self.id = f"{tipo[:3].upper()}-{n:03d}"
        self.zona = f"zona-{n % ZONAS + 1}"
        if tipo == "energia":
            self.base, self.unidad = rng.uniform(5, 40), "kW"
        elif tipo == "movilidad":
            self.base, self.unidad = rng.uniform(10, 60), "veh/min"
        else:
            self.nivel, self.tasa, self.unidad = rng.uniform(10, 60), rng.uniform(0.01, 0.045), "%"
            self.xy = (rng.uniform(0, 10), rng.uniform(0, 10))      # km

    def leer(self, minuto):
        h = minuto / 60
        if self.tipo == "energia":
            return max(0.0, self.base * perfil_energia(h) + self.rng.gauss(0, 0.01 * self.base))
        if self.tipo == "movilidad":
            return max(0.0, self.base * perfil_movilidad(h) + self.rng.gauss(0, 0.06 * self.base))
        self.nivel = min(100.0, self.nivel + self.tasa * self.rng.uniform(0.5, 1.5))
        return self.nivel
