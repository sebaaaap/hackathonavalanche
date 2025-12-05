class Mapa:
    def __init__(self):
        self.hexagonos = []

    def inicializar_mapa_basico(self):
        # Hexágonos simplificados: recurso + número + pueblos adyacentes
        self.hexagonos = [
            {"recurso":"madera", "numero":8, "pueblos":[]},
            {"recurso":"trigo", "numero":6, "pueblos":[]},
            {"recurso":"arcilla", "numero":5, "pueblos":[]},
            {"recurso":"oveja", "numero":9, "pueblos":[]},
            {"recurso":"piedra", "numero":4, "pueblos":[]},
        ]

#class Mapa:
#    def __init__(self):
#        self.hexagonos = []  # [{id, recurso, numero, tiene_ladron}]
#        self.intersecciones = []  # [{id, jugador_id, tipo}]
#        self.caminos = []  # [{id, jugador_id, nodoA, nodoB}]
#
#    def inicializar_mapa_basico(self):
#        """Mapa simple para pruebas: 3 hexagonos."""
#        self.hexagonos = [
#            {"id": 1, "recurso": "madera", "numero": 6, "tiene_ladron": False},
#            {"id": 2, "recurso": "arcilla", "numero": 8, "tiene_ladron": False},
#            {"id": 3, "recurso": "trigo", "numero": 5, "tiene_ladron": False}
#        ]
