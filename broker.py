"""Capa de comunicación: broker publicación/suscripción en memoria que emula MQTT."""
import json
from collections import defaultdict
from config import SOBRECARGA_BYTES


class Broker:
    def __init__(self, nombre):
        self.nombre, self.subs = nombre, defaultdict(list)
        self.mensajes = self.bytes = 0

    def suscribir(self, tipo, funcion):
        self.subs[tipo].append(funcion)

    def publicar(self, tema, carga):
        self.mensajes += 1
        self.bytes += len(json.dumps(carga, separators=(",", ":"))) + len(tema) + SOBRECARGA_BYTES
        for funcion in self.subs[tema.split("/")[2]]:
            funcion(carga)
