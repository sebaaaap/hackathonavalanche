# models/carta.py
class Carta:
    def __init__(self, tipo):
        self.tipo = tipo  # "caballero", "progreso", "punto_victoria"
        self.jugada = False
