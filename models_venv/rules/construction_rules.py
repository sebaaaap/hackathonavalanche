COSTOS = {
    "pueblo": {"madera": 1, "arcilla": 1, "oveja": 1, "trigo": 1},
    "carretera": {"madera": 1, "arcilla": 1},
    "ciudad": {"piedra": 3, "trigo": 2}
}


def validar_costos(jugador, tipo):
    """Verifica si el jugador tiene recursos suficientes."""
    costo = COSTOS[tipo]
    for recurso, cant in costo.items():
        if jugador.recursos[recurso] < cant:
            return False
    return True


def pagar_costos(jugador, tipo):
    """Resta los recursos del jugador."""
    costo = COSTOS[tipo]
    for recurso, cant in costo.items():
        jugador.recursos[recurso] -= cant
