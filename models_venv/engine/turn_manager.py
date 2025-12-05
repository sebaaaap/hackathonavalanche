
from rules.dice_rules import tirar_dados

def ejecutar_turno(jugador, mapa, partida):
    d1,d2,total = tirar_dados()
    if total == 7:
        # activamos ladrón
        pass
    else:
        for hex in mapa.hexagonos:
            if hex["numero"] == total:
                for p in hex["pueblos"]:
                    p.recursos[hex["recurso"]] += 1
