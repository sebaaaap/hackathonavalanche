import random

import random

def tirar_dados():
    d1 = random.randint(1,6)
    d2 = random.randint(1,6)
    return d1,d2,d1+d2



def producir_recursos(mapa, jugadores, total):
    """Asigna recursos según el número del hexágono."""
    for hexagon in mapa.hexagonos:
        if hexagon["numero"] == total and not hexagon["tiene_ladron"]:
            recurso = hexagon["recurso"]
            # versión simple: todos los jugadores reciben 1
            for j in jugadores:
                j.recursos[recurso] += 1
