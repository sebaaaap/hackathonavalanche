"""
🎮 DEMO COMPLETA: Catan con Blockchain
Ejecuta una partida entre Alice y Bob con el BANCO controlando recursos en blockchain

REQUISITOS:
  1. API levantada: uvicorn main:app --reload --port 8000
  2. Instalar requests: pip install requests

USO:
  python demo_game_blockchain.py
"""

import sys
import time
import json
import random
import requests
from pathlib import Path

# Importar trade_client
try:
    from trade_client import enviar_trade, obtener_balance
except ImportError:
    print("❌ Error: No se pudo importar trade_client")
    print("   Asegúrate de estar en /models_venv y que requests esté instalado")
    sys.exit(1)

# Configuración
BANCO = "BANCO"
MODELO_A = "MODELO_A"
MODELO_B = "MODELO_B"

# URL de la API Flask para enviar metadata
FLASK_API_URL = "http://127.0.0.1:5001/game-state"

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_titulo(texto):
    """Imprime un título formateado"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{texto.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.ENDC}\n")

def print_subtitulo(texto):
    """Imprime un subtítulo"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{texto}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-' * 70}{Colors.ENDC}")

def print_ok(texto):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {texto}{Colors.ENDC}")

def print_error(texto):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {texto}{Colors.ENDC}")

def print_info(texto):
    """Imprime mensaje informativo"""
    print(f"{Colors.BLUE}ℹ️  {texto}{Colors.ENDC}")

def print_jugador(nombre, color_prefix=""):
    """Imprime nombre del jugador con color"""
    if nombre == "Alice":
        color = Colors.BLUE
    elif nombre == "Bob":
        color = Colors.YELLOW
    else:
        color = Colors.GREEN
    print(f"{color}{color_prefix}{nombre}{Colors.ENDC}", end="")

def esperar(segundos=1):
    """Pequeña pausa para legibilidad"""
    time.sleep(segundos)

def enviar_metadata_a_flask(data):
    """
    Envía el estado del juego a la API Flask.
    El frontend consultará Flask para mostrar la partida.
    """
    try:
        print_info(f"📡 Enviando metadata a Flask (turno {data.get('turno')})...")
        response = requests.post(
            FLASK_API_URL,
            json=data,
            timeout=5
        )
        
        if response.status_code == 200:
            print_ok("Metadata enviada correctamente")
            return True
        else:
            print_error(f"Error enviando metadata: {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        print_error("Flask API no disponible (puerto 5001)")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

# ============================================
# CLASE JUEGO CATAN CON BLOCKCHAIN
# ============================================

class CatanGameBlockchain:
    """Simulación de Catan con blockchain integrado"""
    
    # Diccionario de recursos: {recurso_id: nombre}
    RECURSOS_MAP = {
        1: "MADERA",
        2: "ARCILLA",
        3: "OVEJA",
        4: "TRIGO",
        5: "MINERAL"
    }
    
    # Costos de construcción: {item: {recurso_id: cantidad}}
    COSTOS = {
        "pueblo": {1: 1, 2: 1, 3: 1, 4: 1},      # 1 madera, 1 arcilla, 1 oveja, 1 trigo
        "castillo": {4: 3, 5: 2},                 # 3 trigo, 2 mineral
        "carretera": {1: 1, 2: 1},                # 1 madera, 1 arcilla
        "carta_desarrollo": {3: 1, 4: 1, 5: 1}   # 1 oveja, 1 trigo, 1 mineral
    }
    
    def __init__(self):
        """Inicializa el juego"""
        self.turno = 0
        self.max_turnos = 1  # ⚠️ LIMITADO A 1 TURNO PARA DEMO
        self.jugadores = {
            MODELO_A: {"nombre": "Alice", "puntos": 0, "turnos": []},
            MODELO_B: {"nombre": "Bob", "puntos": 0, "turnos": []}
        }
        self.historial = []
        self.ultimo_estado = {}  # Para guardar el último estado del turno
    
    def obtener_nombre(self, modelo):
        """Obtiene el nombre del modelo"""
        return self.jugadores[modelo]["nombre"]
    
    def sincronizar_balance(self):
        """Obtiene el balance actual de blockchain"""
        print_info("Obteniendo balance de blockchain...")
        
        balance_a = obtener_balance(MODELO_A)
        balance_b = obtener_balance(MODELO_B)
        
        if balance_a["status"] != "success":
            print_error(f"Error obteniendo balance de {MODELO_A}: {balance_a['mensaje']}")
            return None
        
        if balance_b["status"] != "success":
            print_error(f"Error obteniendo balance de {MODELO_B}: {balance_b['mensaje']}")
            return None
        
        return {
            MODELO_A: balance_a["recursos"],
            MODELO_B: balance_b["recursos"]
        }
    
    def mostrar_balance(self, balance=None):
        """Muestra el balance actual de ambos jugadores"""
        if balance is None:
            balance = self.sincronizar_balance()
            if balance is None:
                return
        
        print_subtitulo("📊 BALANCE ACTUAL (desde Blockchain)")
        
        for modelo in [MODELO_A, MODELO_B]:
            nombre = self.obtener_nombre(modelo)
            recursos = balance[modelo]
            
            print_jugador(nombre, "👤 ")
            print(f":")
            
            total = 0
            for recurso, cantidad in recursos.items():
                print(f"    {recurso:10} : {Colors.BOLD}{cantidad}{Colors.ENDC}")
                # Contar total
                if recurso in self.RECURSOS_MAP.values():
                    total += cantidad
            
            print(f"    {'TOTAL':10} : {Colors.BOLD}{total}{Colors.ENDC}\n")
    
    def tirar_dados(self):
        """Simula tirar dos dados"""
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2
        
        print_info(f"🎲 Dados: {d1} + {d2} = {Colors.BOLD}{total}{Colors.ENDC}")
        esperar(0.5)
        
        return d1, d2, total
    
    def generar_recursos_dados(self, total_dados):
        """
        Genera recursos basado en los dados.
        En Catan real, depende del mapa. Aquí simulamos.
        """
        # Simulación: cada punto de dado puede generar 1-2 recursos aleatorios
        recursos_generados = {}
        
        for _ in range(total_dados):
            recurso_id = random.randint(1, 5)
            recurso_nombre = self.RECURSOS_MAP[recurso_id]
            recursos_generados[recurso_nombre] = recursos_generados.get(recurso_nombre, 0) + 1
        
        return recursos_generados
    
    def ejecutar_turno_construccion(self, modelo_actual):
        """Ejecuta la fase de construcción de un turno"""
        nombre = self.obtener_nombre(modelo_actual)
        
        print_subtitulo(f"🏗️  CONSTRUCCIÓN - Turno de {Colors.BOLD}{nombre}{Colors.ENDC}")
        
        # Obtener balance actual
        balance_actual = self.sincronizar_balance()
        if balance_actual is None:
            return
        
        recursos = balance_actual[modelo_actual]
        
        # Decidir qué construir (simple IA)
        acciones = []
        
        # Si tiene recursos para pueblo: intentar
        if (recursos.get("MADERA", 0) >= 1 and 
            recursos.get("ARCILLA", 0) >= 1 and
            recursos.get("OVEJA", 0) >= 1 and
            recursos.get("TRIGO", 0) >= 1):
            
            acciones.append({
                "tipo": "pueblo",
                "costo": {"MADERA": 1, "ARCILLA": 1, "OVEJA": 1, "TRIGO": 1}
            })
        
        # Si tiene recursos para carretera: intentar
        if (recursos.get("MADERA", 0) >= 1 and 
            recursos.get("ARCILLA", 0) >= 1):
            
            acciones.append({
                "tipo": "carretera",
                "costo": {"MADERA": 1, "ARCILLA": 1}
            })
        
        if not acciones:
            print_info(f"{nombre} no tiene suficientes recursos para construir")
            return None
        
        # Ejecutar acciones
        construccion_realizada = None
        for accion in acciones:
            tipo = accion["tipo"]
            costo = accion["costo"]
            
            # Convertir a formato de recurso ID
            recursos_id = []
            for recurso_nombre, cantidad in costo.items():
                recurso_id = [k for k, v in self.RECURSOS_MAP.items() if v == recurso_nombre][0]
                for _ in range(cantidad):
                    recursos_id.append({"id": recurso_id, "cantidad": 1})
            
            # Enviar al banco (los recursos usados)
            print_info(f"Enviando {tipo} al banco...")
            print(f"   Costo: {costo}")
            
            # En blockchain, envía recursos al BANCO
            resultado = enviar_trade(
                origen=modelo_actual,
                destino=BANCO,
                recursos=recursos_id
            )
            
            if resultado["status"] == "success":
                hash_info = f" Hash: {resultado['hash_tx'][:10]}..." if resultado.get('hash_tx') else ""
                print_ok(f"{tipo.upper()} construido!{hash_info}")
                self.jugadores[modelo_actual]["puntos"] += (1 if tipo == "pueblo" else 2 if tipo == "castillo" else 0)
                
                construccion_realizada = {
                    "tipo": tipo,
                    "costo": costo,
                    "hash_tx": resultado.get('hash_tx')
                }
                
                esperar(0.5)
            else:
                print_error(f"Error construyendo {tipo}: {resultado['mensaje']}")
        
        return construccion_realizada
    
    def ejecutar_comercio(self, modelo_actual):
        """Ejecuta el comercio del jugador con otros o con el banco"""
        nombre = self.obtener_nombre(modelo_actual)
        otro_modelo = MODELO_B if modelo_actual == MODELO_A else MODELO_A
        otro_nombre = self.obtener_nombre(otro_modelo)
        
        print_subtitulo(f"💼 COMERCIO - Turno de {Colors.BOLD}{nombre}{Colors.ENDC}")
        
        # Obtener balance
        balance = self.sincronizar_balance()
        if balance is None:
            return
        
        recursos_actuales = balance[modelo_actual]
        
        # IA simple: si tiene muchos de algo, intenta comerciar
        recurso_exceso = None
        for recurso, cantidad in recursos_actuales.items():
            if cantidad >= 3:
                recurso_exceso = recurso
                break
        
        if not recurso_exceso:
            print_info(f"{nombre} no tiene recursos para comerciar")
            return None
        
        # Comercio: intenta enviar 2 recursos a otro jugador
        recurso_id = [k for k, v in self.RECURSOS_MAP.items() if v == recurso_exceso][0]
        
        print_info(f"{nombre} quiere comerciar 2 {recurso_exceso} con {otro_nombre}")
        print(f"   {nombre} envía: 2 x {recurso_exceso}")
        print(f"   {otro_nombre} envía: 1 x MADERA (simulado)")
        
        esperar(0.5)
        
        # Ejecutar trade
        resultado = enviar_trade(
            origen=modelo_actual,
            destino=otro_modelo,
            recursos=[{"id": recurso_id, "cantidad": 2}]
        )
        
        if resultado["status"] == "success":
            hash_info = f" Hash: {resultado['hash_tx'][:10]}..." if resultado.get('hash_tx') else ""
            print_ok(f"Comercio exitoso!{hash_info}")
            
            comercio_realizado = {
                "de": modelo_actual,
                "para": otro_modelo,
                "recurso": recurso_exceso,
                "cantidad": 2,
                "hash_tx": resultado.get('hash_tx')
            }
            
            esperar(0.5)
            return comercio_realizado
        else:
            print_error(f"Comercio fallido: {resultado['mensaje']}")
            return None
    
    def inicializar_recursos(self):
        """Distribuye recursos iniciales desde el BANCO"""
        print_titulo("💰 INICIALIZANDO BANCO Y DISTRIBUYENDO RECURSOS")
        
        # Recursos iniciales para cada modelo
        recursos_iniciales = [
            {"id": 1, "cantidad": 5},   # 5 Maderas
            {"id": 2, "cantidad": 3},   # 3 Arcillas
            {"id": 3, "cantidad": 4},   # 4 Ovejas
            {"id": 4, "cantidad": 4},   # 4 Trigos
            {"id": 5, "cantidad": 2}    # 2 Minerales
        ]
        
        for modelo in [MODELO_A, MODELO_B]:
            nombre = self.obtener_nombre(modelo)
            
            print_info(f"Distribuyendo recursos iniciales a {nombre}...")
            print(f"   - 5 Maderas")
            print(f"   - 3 Arcillas")
            print(f"   - 4 Ovejas")
            print(f"   - 4 Trigos")
            print(f"   - 2 Minerales")
            
            resultado = enviar_trade(
                origen=BANCO,
                destino=modelo,
                recursos=recursos_iniciales
            )
            
            if resultado["status"] == "success":
                print_ok(f"Recursos distribuidos a {nombre}")
                if resultado.get('hash_tx'):
                    print(f"   TX Hash: {resultado['hash_tx'][:20]}...")
                esperar(1)
            else:
                print_error(f"Error distribuyendo recursos: {resultado['mensaje']}")
                return False
        
        # Mostrar balance inicial
        esperar(1)
        self.mostrar_balance()
        
        return True
    
    def ejecutar_turno(self, modelo_actual):
        """Ejecuta un turno completo para un modelo"""
        nombre = self.obtener_nombre(modelo_actual)
        
        print_titulo(f"🎮 TURNO {self.turno} - {Colors.BOLD}{nombre}{Colors.ENDC}")
        
        # Inicializar metadata del turno
        turno_metadata = {
            "turno": self.turno,
            "jugador_actual": modelo_actual,
            "jugador_nombre": nombre,
            "dados": [],
            "total_dados": 0,
            "recursos_generados": {},
            "construcciones": [],
            "comercios": [],
            "balances": {},
            "hashes_tx": []
        }
        
        # Fase 1: Tirar dados
        print_subtitulo("🎲 FASE 1: TIRAR DADOS")
        d1, d2, total = self.tirar_dados()
        turno_metadata["dados"] = [d1, d2]
        turno_metadata["total_dados"] = total
        
        # Fase 2: Generar recursos
        print_subtitulo("🌾 FASE 2: GENERAR RECURSOS")
        recursos = self.generar_recursos_dados(total)
        
        if recursos:
            print_info("Recursos generados por la tirada:")
            turno_metadata["recursos_generados"][modelo_actual] = []
            
            for recurso, cantidad in recursos.items():
                recurso_id = [k for k, v in self.RECURSOS_MAP.items() if v == recurso][0]
                print(f"   {recurso}: {cantidad}")
                
                turno_metadata["recursos_generados"][modelo_actual].append({
                    "recurso": recurso,
                    "id": recurso_id,
                    "cantidad": cantidad
                })
                
                # El banco envía estos recursos al jugador
                print_info(f"El BANCO envía {cantidad} {recurso}...")
                resultado = enviar_trade(
                    origen=BANCO,
                    destino=modelo_actual,
                    recursos=[{"id": recurso_id, "cantidad": cantidad}]
                )
                
                if resultado["status"] == "success":
                    print_ok(f"Recursos enviados!")
                    if resultado.get('hash_tx'):
                        turno_metadata["hashes_tx"].append(resultado['hash_tx'])
                    esperar(0.3)
                else:
                    print_error(f"Error enviando recursos: {resultado['mensaje']}")
        else:
            print_info("No se generaron recursos en esta tirada")
        
        esperar(0.5)
        
        # Fase 3: Construcción
        construccion = self.ejecutar_turno_construccion(modelo_actual)
        if construccion:
            turno_metadata["construcciones"].append(construccion)
        
        # Fase 4: Comercio
        comercio = self.ejecutar_comercio(modelo_actual)
        if comercio:
            turno_metadata["comercios"].append(comercio)
        
        # Obtener balances finales
        print_info("Obteniendo balances actualizados...")
        balances = self.sincronizar_balance()
        if balances:
            turno_metadata["balances"] = balances
        
        # Guardar y enviar metadata a Flask
        self.ultimo_estado = turno_metadata
        enviar_metadata_a_flask(turno_metadata)
        
        esperar(1)
    
    def ejecutar_juego(self):
        """Ejecuta la partida completa"""
        print_titulo("🎮 CATAN CON BLOCKCHAIN - DEMO COMPLETA 🎮")
        
        print_info("Este programa simula una partida de Catan donde:")
        print(f"  - {Colors.BOLD}Alice{Colors.ENDC} (MODELO_A) y {Colors.BOLD}Bob{Colors.ENDC} (MODELO_B) juegan")
        print(f"  - El {Colors.BOLD}BANCO{Colors.ENDC} distribuye recursos desde blockchain")
        print(f"  - Cada acción se registra en Avalanche")
        print(f"  - Los datos son reales en blockchain, no simulados")
        
        esperar(2)
        
        # Paso 1: Inicializar recursos
        if not self.inicializar_recursos():
            return
        
        esperar(2)
        
        # Paso 2: Ejecutar turnos
        modelos_orden = [MODELO_A, MODELO_B]
        
        for turno in range(1, self.max_turnos + 1):
            self.turno = turno
            
            for modelo in modelos_orden:
                self.ejecutar_turno(modelo)
                
                if turno < self.max_turnos:
                    esperar(2)
            
            esperar(2)
        
        # Paso 3: Mostrar resultados finales
        self.mostrar_resumen_final()
    
    def mostrar_resumen_final(self):
        """Muestra el resumen final del juego"""
        print_titulo("🏁 FIN DE LA PARTIDA - RESUMEN FINAL")
        
        # Balance final
        balance_final = self.sincronizar_balance()
        if balance_final:
            self.mostrar_balance(balance_final)
        
        # Puntos
        print_subtitulo("🏆 PUNTOS FINALES")
        
        for modelo in [MODELO_A, MODELO_B]:
            nombre = self.obtener_nombre(modelo)
            puntos = self.jugadores[modelo]["puntos"]
            
            print_jugador(nombre, "👤 ")
            print(f": {Colors.BOLD}{puntos} puntos{Colors.ENDC}")
        
        # Historial de eventos
        print_subtitulo("📜 EVENTOS REGISTRADOS")
        print_info(f"Total de turnos jugados: {self.max_turnos}")
        print_info(f"Total de jugadores: {len(self.jugadores)}")
        print_info(f"Todos los datos se encuentran en blockchain (Avalanche Testnet)")
        
        print_titulo("✅ DEMO COMPLETADA EXITOSAMENTE")
        print_info("Puedes verificar las transacciones en:")
        print(f"  {Colors.CYAN}https://testnet.snowtrace.io{Colors.ENDC}")


# ============================================
# MAIN
# ============================================

def main():
    """Función principal"""
    try:
        # Crear juego
        juego = CatanGameBlockchain()
        
        # Ejecutar
        juego.ejecutar_juego()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Juego interrumpido por el usuario{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Error inesperado: {str(e)}")
        print(f"Traceback: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
