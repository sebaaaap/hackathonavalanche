def comercio_banco(jugador, entregar, recibir):
    """Versión simple: banco 4:1."""
    if jugador.recursos[entregar] < 4:
        return False

    jugador.recursos[entregar] -= 4
    jugador.recursos[recibir] += 1
    return True


def comercio_jugador(a, b, ofertaA, ofertaB):
    """Intercambio directo entre jugadores."""
    # validar
    for r, c in ofertaA.items():
        if a.recursos[r] < c:
            return False

    for r, c in ofertaB.items():
        if b.recursos[r] < c:
            return False

    # aplicar
    for r, c in ofertaA.items():
        a.recursos[r] -= c
        b.recursos[r] += c

    for r, c in ofertaB.items():
        b.recursos[r] -= c
        a.recursos[r] += c

    return True
