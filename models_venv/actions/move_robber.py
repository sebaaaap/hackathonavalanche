from rules.robber_rules import mover_ladron

def mover_ladron_action(partida, hexagon_id):
    mover_ladron(partida.mapa, hexagon_id)
    partida.registrar_evento("ladrón_movido", hexagon_id)
