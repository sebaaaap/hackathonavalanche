"use client"

import { useState, useEffect } from "react"
import type { Player, Hex, Building, ResourceCount } from "../types/catan"

// --- CONFIGURACIÓN DE LA BLOCKCHAIN/API ---
// URL de tu API de Flask para la consulta de saldos
const API_BALANCE_URL = "http://127.0.0.1:5001/consultar-saldos"

// Mapeo de nombres de modelos en la API a IDs de jugadores locales
const MODEL_TO_PLAYER_MAP: Record<string, number> = {
  "MODELO_A": 0, // Jugador 1 -> ID 0
  "MODELO_B": 1, // Jugador 2 -> ID 1
}

// Mapeo de nombres de recursos de la API (MADERA, ARCILLA) a claves locales (wood, brick)
const RESOURCE_API_TO_LOCAL: Record<string, keyof ResourceCount> = {
  "MADERA": "wood",
  "ARCILLA": "brick",
  "OVEJA": "sheep",
  "TRIGO": "wheat",
  "MINERAL": "ore",
}
// ------------------------------------------

// ... (RESOURCE_TYPES, RESOURCE_MAPPING, initializeBoard, initializePlayers se mantienen)

const RESOURCE_TYPES = ["forest", "hill", "field", "pasture", "mountain", "desert"]
const RESOURCE_MAPPING: Record<string, keyof ResourceCount> = {
  forest: "wood",
  hill: "brick",
  field: "wheat",
  pasture: "sheep",
  mountain: "ore",
}

function initializeBoard(): Hex[] {
  // ... (El código de initializeBoard es muy largo, se omite aquí por brevedad, pero se mantiene en el archivo)
  const hexagons: Hex[] = []
  const numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]
  // ...
  return hexagons
}

function initializePlayers(): Player[] {
  const players: Player[] = []
  for (let i = 0; i < 2; i++) {
    players.push({
      id: i,
      name: `Jugador ${i + 1}`,
      // Los recursos se inicializan a 0, pero serán SOBREESCRITOS por el fetch
      resources: { wood: 0, brick: 0, sheep: 0, wheat: 0, ore: 0 },
      buildings: { roads: 15, settlements: 5, cities: 4 },
      victoryPoints: 0,
    })
  }
  return players
}


export function useGameStore() {
  const [players, setPlayers] = useState<Player[]>(initializePlayers())
  const [board, setBoard] = useState({ hexagons: [] as Hex[] })

  useEffect(() => {
    setBoard({ hexagons: initializeBoard() })
  }, [])
  const [buildings, setBuildings] = useState<Building[]>([])
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0)
  const [gamePhase, setGamePhase] = useState<"setup" | "rolling" | "building" | "trading" | "finished">("rolling")
  const [selectedHex, setSelectedHex] = useState<number | null>(null)
  const [selectedBuildingType, setSelectedBuildingType] = useState<string | null>(null)

  // --------------------------------------------------------------------------
  // --- FUNCIÓN CENTRAL PARA CONSULTAR Y ACTUALIZAR SALDOS ---
  // --------------------------------------------------------------------------
  const fetchBalances = async () => {
    try {
      const response = await fetch(API_BALANCE_URL)

      if (!response.ok) {
        throw new Error(`Error al conectar con la API: ${response.status}`)
      }

      const data = await response.json()

      if (data.status !== "success" || !data.saldos) {
        throw new Error("Respuesta de API inválida o error en el servidor.")
      }

      const blockchainBalances = data.saldos // { MODELO_A: {...}, MODELO_B: {...} }

      // Crear un nuevo estado de jugadores basado en el estado actual
      const newPlayers = players.map((player) => {
        let updatedResources = { ...player.resources };
        let hasUpdated = false;

        // Iterar sobre los modelos definidos en la API (MODELO_A, MODELO_B)
        for (const [modelName, balances] of Object.entries(blockchainBalances)) {
          const playerId = MODEL_TO_PLAYER_MAP[modelName];

          // Si el ID del jugador actual coincide con el modelo de la API
          if (playerId === player.id) {
            // Actualizar los recursos con los valores de la blockchain
            const resourcesFromAPI = (balances as any).recursos;

            for (const [apiResourceName, amount] of Object.entries(resourcesFromAPI)) {
              const localKey = RESOURCE_API_TO_LOCAL[apiResourceName];

              if (localKey) {
                // Sobreescribir el saldo local con el saldo de la blockchain
                updatedResources[localKey] = amount as number;
                hasUpdated = true;
              }
            }
          }
        }

        // Si se encontraron actualizaciones, devolver el nuevo objeto Player
        if (hasUpdated) {
          return { ...player, resources: updatedResources };
        }
        return player;
      });

      setPlayers(newPlayers);
      console.log("✅ Saldos actualizados desde la blockchain.");

    } catch (error) {
      console.error("❌ Error durante el fetch de balances:", error)
    }
  }

  // --------------------------------------------------------------------------
  // --- EFECTO PARA EL POLLING CONSTANTE ---
  // --------------------------------------------------------------------------
  useEffect(() => {
    // 1. Ejecutar la consulta inmediatamente al montar el componente
    fetchBalances()

    // 2. Configurar el intervalo para la consulta periódica (ej: cada 5 segundos)
    const intervalId = setInterval(fetchBalances, 5000)

    // 3. Limpiar el intervalo al desmontar el componente (limpieza esencial de React)
    return () => clearInterval(intervalId)
  }, []) // El array de dependencias vacío asegura que se ejecute solo una vez al inicio.

  // --------------------------------------------------------------------------
  // --- FUNCIONES DE ACCIÓN (Ajustes para usar los saldos de la blockchain) ---
  // --------------------------------------------------------------------------

  const rollDice = (total: number) => {
    // Nota: Si la asignación de recursos se maneja en el servidor/blockchain, 
    // solo se necesita llamar a fetchBalances después de un pequeño delay
    // para dar tiempo a que la transacción se complete.

    // Aquí se mantiene la vieja lógica local de asignación (que DEBE ser reemplazada 
    // por una llamada POST de acuñación en un sistema real de blockchain).
    const newPlayers = [...players]

    board.hexagons.forEach((hex) => {
      // ... (Lógica de asignación local de recursos original)
    })

    // setPlayers(newPlayers) // Ya no es necesario si la asignación es en la blockchain

    setGamePhase("building")
    // Forzar una actualización de saldos desde la blockchain después del tiro de dado
    setTimeout(fetchBalances, 2000);
  }

  const buildRoad = (hexId: number, edgeId: number) => {
    const currentPlayer = players[currentPlayerIndex]

    // La verificación de saldo (if...) usa el saldo YA actualizado por el fetch.
    if (currentPlayer.resources.wood < 1 || currentPlayer.resources.brick < 1) {
      alert("No tienes suficientes recursos (necesitas 1 madera y 1 ladrillo)")
      return
    }

    if (currentPlayer.buildings.roads <= 0) {
      alert("No tienes más caminos disponibles")
      return
    }

    // *** Aquí debería ir la llamada POST a la API /enviar-recursos ***
    // Si la llamada POST es exitosa:
    // 1. Añade la construcción localmente (como abajo)
    const buildingId = `${currentPlayerIndex}-road-${hexId}-${edgeId}`
    const newBuilding: Building = { id: buildingId, hexId, vertexId: edgeId, type: "road", playerId: currentPlayerIndex }

    const newPlayers = [...players]
    // 2. Comenta estas líneas ya que el gasto lo hará la blockchain:
    // newPlayers[currentPlayerIndex].resources.wood -= 1
    // newPlayers[currentPlayerIndex].resources.brick -= 1
    newPlayers[currentPlayerIndex].buildings.roads -= 1

    setBuildings([...buildings, newBuilding])
    setPlayers(newPlayers)

    // 3. Forzar fetch para reflejar el gasto de la blockchain inmediatamente
    setTimeout(fetchBalances, 500);
  }

  // Las demás funciones (buildSettlement, upgradeCity, tradeWithBank) seguirían el mismo patrón:
  // 1. Verificar saldo local (ya actualizado por el fetch).
  // 2. Llamar a la API POST para realizar la TX de gasto.
  // 3. Si la TX es exitosa, actualizar el estado de buildings/VP localmente.
  // 4. Llamar a fetchBalances para confirmar el nuevo saldo.

  // ... (El resto de las funciones buildSettlement, upgradeCity, tradeWithBank, endTurn, selectHex se mantienen con la lógica original)

  // Omitiendo el resto del código por brevedad, asumiendo que se mantiene inalterado
  const buildSettlement = (hexId: number, vertexId: number) => { /* ... */ }
  const upgradeCity = (hexId: number, vertexId: number) => { /* ... */ }
  const tradeWithBank = (give: Record<string, number>, receive: Record<string, number>) => { /* ... */ }
  const endTurn = () => { /* ... */ }
  const selectHex = (hexId: number) => { /* ... */ }


  return {
    players,
    board,
    buildings,
    currentPlayerIndex,
    gamePhase,
    selectedHex,
    selectedBuildingType,
    setSelectedBuildingType,
    rollDice,
    buildRoad,
    buildSettlement,
    upgradeCity,
    tradeWithBank,
    endTurn,
    selectHex,
    fetchBalances, // Exportamos la función por si se necesita una actualización manual
  }
}