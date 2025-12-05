class Turno:
    def __init__(self, jugador_actual=0):
        self.numero = 1
        self.jugador_actual = jugador_actual
        self.dados = {"d1":0,"d2":0,"total":0}
