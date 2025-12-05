# models/estructuras.py
class Castillos:
    def __init__(self, jugador):
        self.jugador = jugador
        self.posiciones = []

class Carreteras:
    def __init__(self, jugador):
        self.jugador = jugador
        self.conexiones = []

# rules/construction_rules.py
def construir_castillo(jugador):
    costo = {"madera":2, "piedra":3, "trigo":2}
    if jugador.tiene_recursos(costo):
        jugador.pagar_recursos(costo)
        jugador.puntos_victoria += 2
        return True
    return False

def construir_carretera(jugador):
    costo = {"madera":1, "arcilla":1}
    if jugador.tiene_recursos(costo):
        jugador.pagar_recursos(costo)
        return True
    return False
