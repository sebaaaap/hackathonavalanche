from rules.construction_rules import validar_costos, pagar_costos


# =========================
# CONSTRUIR PUEBLO
# =========================
def construir_pueblo(partida, jugador):
    costo = {
        "madera": 1,
        "arcilla": 1,
        "trigo": 1,
        "oveja": 1
    }

    if not validar_costos(jugador, costo):
        return False

    pagar_costos(jugador, costo)

    # Registrar estructura
    jugador.estructuras["pueblos"] += 1
    jugador.puntos_victoria += 1

    partida.registrar_evento("construir_pueblo", jugador.nombre)
    return True


# =========================
# CONSTRUIR CARRETERA
# =========================
def construir_carretera(partida, jugador):
    costo = {
        "madera": 1,
        "arcilla": 1
    }

    if not validar_costos(jugador, costo):
        return False

    pagar_costos(jugador, costo)

    jugador.estructuras["carreteras"] += 1

    partida.registrar_evento("construir_carretera", jugador.nombre)
    return True


# =========================
# CONSTRUIR CASTILLO (CIUDAD)
# =========================
def construir_castillo(partida, jugador):
    costo = {
        "piedra": 3,
        "trigo": 2
    }

    if not validar_costos(jugador, costo):
        return False

    pagar_costos(jugador, costo)

    jugador.estructuras["castillos"] += 1
    jugador.puntos_victoria += 1  # ciudad = +1 adicional (ya tenía un pueblo)

    partida.registrar_evento("construir_castillo", jugador.nombre)
    return True
