import time

class Partida:
    def __init__(self, jugadores, mapa, duracion_segundos=15):
        self.jugadores = jugadores
        self.mapa = mapa
        self.turno = None
        self.eventos = []
        self.inicio = time.time()
        self.duracion_max = duracion_segundos

    def registrar_evento(self, tipo, data):
        self.eventos.append({"tipo": tipo, "data": data})

    def ha_terminado_por_tiempo(self):
        return (time.time() - self.inicio) >= self.duracion_max
