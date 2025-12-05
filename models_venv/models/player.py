
class Player:
    def __init__(self, id, nombre):
        self.id = id
        self.nombre = nombre
        self.recursos = {"madera": 0, "arcilla": 0, "trigo": 0, "oveja": 0, "piedra": 0}
        self.puntos_victoria = 0
        self.cartas_desarrollo = []
        self.acciones = []

    def tiene_recursos(self, costo):
        return all(self.recursos[r] >= c for r, c in costo.items())

    def pagar_recursos(self, costo):
        for r, c in costo.items():
            self.recursos[r] -= c
