
# rules/robber_rules.py
def mover_ladron(mapa, hex_index, jugador_roba=None):
    mapa.ladron = hex_index
    if jugador_roba:
        # robar 1 recurso al azar del jugador
        from random import choice
        recursos_posibles = [r for r,c in jugador_roba.recursos.items() if c>0]
        if recursos_posibles:
            r = choice(recursos_posibles)
            jugador_roba.recursos[r] -= 1
            jugador_roba.recursos[r] += 1
def mover_ladron(mapa, hex_index, jugador_roba=None, jugador_que_mueve=None):
    """
    Mueve al ladrón a un hex específico.
    Si hay un jugador para robar (jugador_roba), se roba 1 recurso al azar.
    """
    from random import choice
    
    mapa.ladron = hex_index  # actualizar posición del ladrón
    
    if jugador_roba:  # si hay jugador que robar
        # obtener lista de recursos disponibles
        recursos_posibles = [r for r, c in jugador_roba.recursos.items() if c > 0]
        if recursos_posibles:
            r = choice(recursos_posibles)
            jugador_roba.recursos[r] -= 1  # se lo quitas al jugador víctima
            if jugador_que_mueve:
                jugador_que_mueve.recursos[r] += 1  # se lo das al jugador que mueve

