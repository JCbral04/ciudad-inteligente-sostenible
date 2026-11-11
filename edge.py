"""Capa Edge Computing: agregación por ventana, banda muerta, latido y alertas locales."""
from collections import defaultdict
from statistics import fmean
from config import VENTANA_EDGE_MIN, BANDA_MUERTA, LATIDO_MIN, UMBRAL_LLENADO


class NodoEdge:
    def __init__(self, broker):
        self.broker = broker
        self.buffer = defaultdict(list)
        self.ultimo = {}                 # id -> (valor enviado, minuto)
        self.alertados = set()

    def _enviar(self, s, minuto, valor, alerta=False):
        self.broker.publicar(f"ciudad/{s.zona}/{s.tipo}/{s.id}",
                             {"id": s.id, "z": s.zona, "t": minuto, "v": round(valor, 2),
                              "u": s.unidad, "a": int(alerta)})
        self.ultimo[s.id] = (valor, minuto)

    def _cambio_significativo(self, s, valor, minuto):
        if s.id not in self.ultimo:
            return True
        previo, t_previo = self.ultimo[s.id]
        modo, banda = BANDA_MUERTA[s.tipo]
        delta = abs(valor - previo) / max(abs(previo), 1e-9) if modo == "rel" else abs(valor - previo)
        return delta > banda or minuto - t_previo >= LATIDO_MIN

    def recibir(self, s, minuto, valor):
        if s.tipo == "residuos" and valor >= UMBRAL_LLENADO and s.id not in self.alertados:
            self.alertados.add(s.id)                       # decisión local, sin esperar a la nube
            self._enviar(s, minuto, valor, alerta=True)
        self.buffer[s.id].append(valor)
        if (minuto + 1) % VENTANA_EDGE_MIN == 0:
            promedio = fmean(self.buffer.pop(s.id))
            if self._cambio_significativo(s, promedio, minuto):
                self._enviar(s, minuto, promedio)
