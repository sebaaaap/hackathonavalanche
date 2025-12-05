from rules.trade_rules import comercio_banco, comercio_jugador


# actions/trade.py
def comerciar_banco(jugador, recurso_ofrece, recurso_recibe, tasa=4):
    if jugador.recursos[recurso_ofrece] >= tasa:
        jugador.recursos[recurso_ofrece] -= tasa
        jugador.recursos[recurso_recibe] += 1
        return True
    return False

def comerciar_jugador(jugador1, jugador2, oferta, demanda):
    # oferta y demanda son dicts de recursos
    if all(jugador1.recursos[r] >= c for r,c in oferta.items()) and \
       all(jugador2.recursos[r] >= c for r,c in demanda.items()):
        for r,c in oferta.items(): jugador1.recursos[r] -= c; jugador2.recursos[r] += c
        for r,c in demanda.items(): jugador2.recursos[r] -= c; jugador1.recursos[r] += c
        return True
    return False
