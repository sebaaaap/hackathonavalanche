def siguiente_jugador(turno, cantidad):
    turno.jugador_actual = (turno.jugador_actual + 1) % cantidad
    turno.numero += 1
