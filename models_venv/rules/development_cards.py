# rules/development_cards.py
def comprar_carta(jugador, mazo):
    if jugador.tiene_recursos({"trigo":1, "oveja":1, "piedra":1}):
        jugador.pagar_recursos({"trigo":1, "oveja":1, "piedra":1})
        carta = mazo.pop()
        jugador.cartas_desarrollo.append(carta)
        return carta
    return None

def jugar_carta(jugador, carta):
    if carta in jugador.cartas_desarrollo and not carta.jugada:
        carta.jugada = True
        # efectos según tipo
        return True
    return False
