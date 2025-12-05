from models.player import Player
from models.mapa import Mapa
from models.partida import Partida
from models.turno import Turno
from actions.build import construir_pueblo
from rules.dice_rules import tirar_dados
from rules.construction_rules import validar_costos, pagar_costos
import json, time, random, requests, re

# --- Configuración de modelos Ollama disponibles ---
MODELOS_OLLAMA = {
    "alice": "mistral-catan",
    "bob": "qwen-32b-catan",
}

OLLAMA_BASE_URL = "http://localhost:11434"

# --- Función para generar JSON del estado ---
def generar_contexto(partida, archivo="estado.json"):
    estado = {
        "turno_actual": partida.turno.jugador_actual_nombre() if hasattr(partida.turno, 'jugador_actual_nombre') else "Jugador",
        "dados": getattr(partida.turno, 'dados', {"d1": 0, "d2": 0, "total": 0}),
        "jugadores": [],
        "mapa": [],
        "ladron": getattr(partida.mapa, "ladron", None),
        "eventos_recientes": partida.eventos[-5:] if hasattr(partida, 'eventos') else []
    }

    for j in partida.jugadores:
        estado["jugadores"].append({
            "nombre": j.nombre,
            "recursos": j.recursos,
            "puntos_victoria": j.puntos_victoria,
            "pueblos": getattr(j, 'pueblos', []),
            "castillos": getattr(j, 'castillos', []),
            "carreteras": getattr(j, 'carreteras', []),
            "cartas_desarrollo": [c.tipo if hasattr(c, 'tipo') else str(c) for c in getattr(j, 'cartas_desarrollo', []) if not getattr(c, 'jugada', False)]
        })

    for h in getattr(partida.mapa, 'hexagonos', []):
        estado["mapa"].append({
            "recurso": getattr(h, 'recurso', "unknown"),
            "numero": getattr(h, 'numero', 0),
            "pueblos": [p.nombre if hasattr(p, 'nombre') else str(p) for p in getattr(h, 'pueblos', [])],
            "castillos": [c.jugador.nombre if hasattr(c, 'jugador') and hasattr(c.jugador, 'nombre') else str(c) for c in getattr(h, 'castillos', [])]
        })

    with open(archivo, "w") as f:
        json.dump(estado, f, indent=4)


def total_recursos(jugador):
    return sum(jugador.recursos.values())


def descartar_mitad(jugador):
    """Descarta la mitad (floor) de los recursos del jugador de forma aleatoria."""
    total = total_recursos(jugador)
    if total <= 7:
        return {}
    to_discard = total // 2
    recursos = [r for r, c in jugador.recursos.items() for _ in range(c)]
    random.shuffle(recursos)
    discarded = {}
    for _ in range(to_discard):
        if not recursos:
            break
        r = recursos.pop()
        jugador.recursos[r] -= 1
        discarded[r] = discarded.get(r, 0) + 1
    return discarded


def robar_recurso(desde_jugador, hacia_jugador):
    """El jugador 'hacia_jugador' roba 1 recurso aleatorio a 'desde_jugador' si tiene alguno."""
    tipos = [r for r, c in desde_jugador.recursos.items() if c > 0]
    if not tipos:
        return None
    elegido = random.choice(tipos)
    desde_jugador.recursos[elegido] -= 1
    hacia_jugador.recursos[elegido] += 1
    return elegido


# --- Función para consultar modelos LLM vía Ollama ---
def consultar_llm_ollama(modelo, prompt, temperatura=0.7):
    """
    Consulta un modelo LLM en Ollama y obtiene respuesta.
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": modelo,
                "prompt": prompt,
                "stream": False,
                "temperature": temperatura,
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response")
    except Exception as e:
        print(f"Error consultando LLM {modelo}: {e}")
        return None


# --- Función para decidir acciones con LLM ---
def llm_decidir_accion(jugador, contexto_json, reglas_txt="", estrategias_txt="", acciones_legales=None):
    """
    Usa Ollama para que el LLM decida la próxima acción del jugador.
    Se envía SOLO la lista de acciones legales y se exige formato EXACTO: ACCION: <accion>
    """
    nombre_lower = jugador.nombre.lower()
    modelo = MODELOS_OLLAMA.get(nombre_lower, "mixtral-8x7b-catan")

    estado_str = json.dumps(contexto_json, indent=2)
    acciones_legales = acciones_legales or ["pasar_turno"]
    acciones_str = ", ".join(acciones_legales)
    prompt = f"""Eres un jugador de Catan. El estado actual del juego es:

{estado_str}

Tus recursos actuales: {json.dumps(jugador.recursos)}
Tu puntuación: {jugador.puntos_victoria}

Eres el jugador {jugador.nombre}. Es tu turno.

Acciones legales disponibles: {acciones_str}

Respondé con EXACTAMENTE este formato (sin texto adicional):
ACCION: <nombre_accion>

Donde <nombre_accion> debe ser una de las acciones legales listadas arriba.
"""

    print(f"[{jugador.nombre}] Consultando LLM {modelo}...")
    respuesta_llm = consultar_llm_ollama(modelo, prompt, temperatura=0.3)

    if respuesta_llm:
        print(f"[{jugador.nombre}] LLM raw: {str(respuesta_llm)[:200]}...")
        m = re.search(r"ACCION:\s*([a-zA-Z_]+)", str(respuesta_llm), re.IGNORECASE)
        if m:
            accion = m.group(1).lower()
            if accion in acciones_legales:
                return {"accion": accion}
            else:
                print(f"[LLM] Acción '{accion}' no está en la lista legal: {acciones_legales}")

    # Fallback
    return {"accion": "pasar_turno"}


# --- Script principal ---
def main():
    # Crear jugadores con modelos LLM asignados
    jugador1 = Player(0, "Alice")
    jugador2 = Player(1, "Bob")
    jugadores = [jugador1, jugador2]

    # Recursos iniciales
    jugador1.recursos = {"madera": 3, "arcilla": 2, "trigo": 2, "oveja": 2, "piedra": 0}
    jugador2.recursos = {"madera": 2, "arcilla": 2, "trigo": 2, "oveja": 2, "piedra": 1}

    # Crear mapa
    mapa = Mapa()
    mapa.inicializar_mapa_basico()

    # Crear partida
    partida = Partida(jugadores, mapa, duracion_segundos=60)
    partida.turno = Turno(0)

    print("=" * 60)
    print("SIMULACIÓN DE CATAN CON LLMs OLLAMA")
    print("=" * 60)
    print(f"Modelos disponibles:")
    for nombre, modelo in MODELOS_OLLAMA.items():
        print(f"  - {nombre.capitalize()}: {modelo}")
    print("=" * 60 + "\n")

    # Bucle de juego
    turno_count = 0
    while turno_count < 10:  # Máximo 10 turnos de demostración
        for i, jugador in enumerate(jugadores):
            turno_count += 1
            print(f"\n{'='*60}")
            print(f"TURNO {turno_count} - Jugador: {jugador.nombre}")
            print(f"{'='*60}")
            print(f"Recursos: {jugador.recursos}")
            print(f"Puntos Victoria: {jugador.puntos_victoria}\n")

            # Tirar dados
            try:
                d1, d2, total = tirar_dados()
                print(f"🎲 Dados: {d1} + {d2} = {total}")
            except:
                d1, d2, total = 7, 6, 13
                print(f"🎲 Dados: {d1} + {d2} = {total}")

            # Repartir recursos por mapa (existente)
            for hex in mapa.hexagonos:
                if hex["numero"] == total:
                    for p in hex["pueblos"]:
                        p.recursos[hex["recurso"]] += 1
                        print(f"{p.nombre} recibe 1 {hex['recurso']}")

            # --- Fase de producción simplificada para jugador activo ---
            if total != 7:
                if 2 <= total <= 5:
                    recurso_prod = "madera"
                elif 6 <= total <= 8:
                    recurso_prod = "trigo"
                elif 9 <= total <= 12:
                    recurso_prod = "oveja"
                else:
                    recurso_prod = None
                if recurso_prod:
                    jugador.recursos[recurso_prod] += 1 ##aqui va la funcion de math del brancooo

                    print(f"[Producción] {jugador.nombre} recibe 1 {recurso_prod} (fase de producción simplificada)")
            else:
                # Regla del 7: descartar y robar
                print("[LADRÓN] Salió 7: se aplica la regla del 7")
                # Todos los jugadores con más de 7 recursos descartan la mitad
                for pj in jugadores:
                    tot = total_recursos(pj)
                    if tot > 7:
                        discarded = descartar_mitad(pj)
                        print(f"{pj.nombre} descarta {sum(discarded.values())} recursos: {discarded}")
                # Jugador activo roba 1 recurso a otro jugador aleatorio que tenga recursos
                posibles = [p for p in jugadores if p is not jugador and total_recursos(p) > 0]
                if posibles:
                    objetivo = random.choice(posibles)
                    robado = robar_recurso(objetivo, jugador)
                    if robado:
                        print(f"{jugador.nombre} roba 1 {robado} a {objetivo.nombre}")

            # Generar contexto
            generar_contexto(partida)
            with open("estado.json") as f:
                contexto_json = json.load(f)

            # Calcular acciones legales y consultar LLM
            acciones_legales = ["pasar_turno"]
            if validar_costos(jugador, "pueblo"):
                acciones_legales.append("construir_pueblo")
            if validar_costos(jugador, "carretera"):
                acciones_legales.append("construir_carretera")
            if validar_costos(jugador, "ciudad"):
                acciones_legales.append("construir_castillo")

            accion = llm_decidir_accion(jugador, contexto_json, reglas_txt="", estrategias_txt="", acciones_legales=acciones_legales)
            print(f"\n🤖 {jugador.nombre} decidió: {accion['accion'].upper()}")

            # Ejecutar acción
            if accion["accion"] == "construir_pueblo":
                if validar_costos(jugador, "pueblo"):
                    pagar_costos(jugador, "pueblo")
                    jugador.puntos_victoria += 1
                    print(f"✓ {jugador.nombre} construyó un pueblo (+1 PV)")
                else:
                    print(f"✗ {jugador.nombre} no tiene recursos para construir pueblo")

            elif accion["accion"] == "construir_carretera":
                if validar_costos(jugador, "carretera"):
                    pagar_costos(jugador, "carretera")
                    print(f"✓ {jugador.nombre} construyó una carretera")
                else:
                    print(f"✗ {jugador.nombre} no tiene recursos para construir carretera")

            elif accion["accion"] == "construir_castillo":
                if validar_costos(jugador, "ciudad"):
                    pagar_costos(jugador, "ciudad")
                    jugador.puntos_victoria += 1
                    print(f"✓ {jugador.nombre} construyó un castillo (+1 PV)")
                else:
                    print(f"✗ {jugador.nombre} no puede construir castillo")

            time.sleep(2)

    print("\n" + "=" * 60)
    print("⏹ SIMULACIÓN FINALIZADA")
    print("=" * 60)
    print("\nResultados finales:")
    for jugador in jugadores:
        print(f"  {jugador.nombre}: {jugador.puntos_victoria} PV | Recursos: {jugador.recursos}")


if __name__ == "__main__":
    main()
