"use client"

import { useState, useEffect } from "react"
// Nota: 'Hex' y 'Building' deben incluir 'q' y 'r' para que TypeScript no arroje errores
import type { Player, Hex, Building, ResourceCount } from "../types/catan"

// --- DEFINICIONES DE TIPOS (Re-declaradas aquí por si no se importan correctamente) ---
// ASUMIMOS que Hex ahora incluye q y r, necesario para el posicionamiento
type InternalHex = {
  id: number;
  type: string;
  number: number;
  q: number; // Coordenada Axial Q
  r: number; // Coordenada Axial R
}

// --------------------------------------------------------------------------
// --- CONFIGURACIÓN DE LA BLOCKCHAIN/API ---
// --------------------------------------------------------------------------
const API_BALANCE_URL = "http://127.0.0.1:5001/consultar-saldos"

const MODEL_TO_PLAYER_MAP: Record<string, number> = {
  "MODELO_A": 0,
  "MODELO_B": 1,
}

const RESOURCE_API_TO_LOCAL: Record<string, keyof ResourceCount> = {
  "MADERA": "wood",
  "ARCILLA": "brick",
  "OVEJA": "sheep",
  "TRIGO": "wheat",
  "MINERAL": "ore",
}

const RESOURCE_TYPES = ["forest", "hill", "field", "pasture", "mountain", "desert"]
const RESOURCE_MAPPING: Record<string, keyof ResourceCount> = {
  forest: "wood",
  hill: "brick",
  field: "wheat",
  pasture: "sheep",
  mountain: "ore",
}

/**
 * Función de utilidad para barajar (shuffle) un array.
 */
function shuffleArray<T>(array: T[]): T[] {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

// --------------------------------------------------------------------------
// --- FUNCIÓN initializeBoard CORREGIDA (IMPLEMENTACIÓN COMPLETA) ---
// --------------------------------------------------------------------------
function initializeBoard(): InternalHex[] {
  // 1. Definición de la geometría: 19 hexágonos con coordenadas axiales (q, r)
  // Estas coordenadas generan el patrón hexagonal 3-4-5-4-3 (o 1-6-12)
  const coordinates = [
    { q: 0, r: 0 }, // Centro

    // Primer anillo (6 hexágonos)
    { q: 1, r: 0 }, { q: 1, r: -1 }, { q: 0, r: -1 },
    { q: -1, r: 0 }, { q: -1, r: 1 }, { q: 0, r: 1 },

    // Segundo anillo (12 hexágonos)
    { q: 2, r: 0 }, { q: 2, r: -1 }, { q: 1, r: -2 }, { q: 0, r: -2 },
    { q: -1, r: -1 }, { q: -2, r: 0 }, { q: -2, r: 1 }, { q: -1, r: 2 },
    { q: 0, r: 2 }, { q: 1, r: 1 }, { q: 2, r: -2 }, { q: -2, r: 2 },
  ];

  // 2. Definición del pool de recursos (Standard Catan)
  const resourcePool = shuffleArray([
    // 4 Bosque (Madera)
    "forest", "forest", "forest", "forest",
    // 4 Pasto (Oveja)
    "pasture", "pasture", "pasture", "pasture",
    // 4 Campo (Trigo)
    "field", "field", "field", "field",
    // 3 Colina (Ladrillo/Arcilla)
    "hill", "hill", "hill",
    // 3 Montaña (Mineral)
    "mountain", "mountain", "mountain",
    // 1 Desierto
    "desert",
  ]);

  // 3. Definición del pool de números (excluyendo el 7)
  const numberPool = shuffleArray([
    2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12,
  ]);

  const hexagons: InternalHex[] = [];
  let numberIndex = 0;

  // 4. Mapear coordenadas y asignar tipos/números
  coordinates.forEach((coord, index) => {
    const type = resourcePool[index];
    let number = 0;

    // Asignar número si NO es el desierto
    if (type !== 'desert') {
      number = numberPool[numberIndex];
      numberIndex++;
    }

    hexagons.push({
      id: index,
      type: type,
      number: number,
      q: coord.q, // <-- ASIGNACIÓN CORRECTA DE Q
      r: coord.r, // <-- ASIGNACIÓN CORRECTA DE R
    });
  });

  // Nota: Deberías implementar una colocación más estratégica (ej: no juntar 6 y 8)
  // pero esta implementación aleatoria es suficiente para que el tablero se muestre.
  return hexagons as Hex[];
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
  // Inicializamos el tablero llamando a la función corregida
  const [board, setBoard] = useState({ hexagons: initializeBoard() })

  // Nota: El useEffect para llamar a setBoard({ hexagons: initializeBoard() }) 
  // ya no es necesario si llamamos a initializeBoard en la inicialización de useState, 
  // lo cual es más eficiente. He comentado o quitado el useEffect duplicado.

  const [buildings, setBuildings] = useState<Building[]>([])
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0)
  const [gamePhase, setGamePhase] = useState<"setup" | "rolling" | "building" | "trading" | "finished">("rolling")
  const [selectedHex, setSelectedHex] = useState<number | null>(null)
  const [selectedBuildingType, setSelectedBuildingType] = useState<string | null>(null)

  // --------------------------------------------------------------------------
  // --- FUNCIÓN CENTRAL PARA CONSULTAR Y ACTUALIZAR SALDOS (fetchBalances) ---
  // ... (Esta función se mantiene inalterada)
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

      const blockchainBalances = data.saldos

      const newPlayers = players.map((player) => {
        let updatedResources = { ...player.resources };
        let hasUpdated = false;

        for (const [modelName, balances] of Object.entries(blockchainBalances)) {
          const playerId = MODEL_TO_PLAYER_MAP[modelName];

          if (playerId === player.id) {
            const resourcesFromAPI = (balances as any).recursos;

            for (const [apiResourceName, amount] of Object.entries(resourcesFromAPI)) {
              const localKey = RESOURCE_API_TO_LOCAL[apiResourceName];

              if (localKey) {
                updatedResources[localKey] = amount as number;
                hasUpdated = true;
              }
            }
          }
        }

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
    fetchBalances()

    const intervalId = setInterval(fetchBalances, 5000)

    return () => clearInterval(intervalId)
  }, [])

  // --------------------------------------------------------------------------
  // --- FUNCIONES DE ACCIÓN (Mantenidas) ---
  // --------------------------------------------------------------------------

  const rollDice = (total: number) => {
    const newPlayers = [...players]
    board.hexagons.forEach((hex) => { /* ... */ })
    setGamePhase("building")
    setTimeout(fetchBalances, 2000);
  }

  const buildRoad = (hexId: number, edgeId: number) => {
    const currentPlayer = players[currentPlayerIndex]

    if (currentPlayer.resources.wood < 1 || currentPlayer.resources.brick < 1) {
      // Usamos console.error o un modal en lugar de alert()
      console.error("No tienes suficientes recursos (necesitas 1 madera y 1 ladrillo)")
      return
    }

    if (currentPlayer.buildings.roads <= 0) {
      console.error("No tienes más caminos disponibles")
      return
    }

    // Aquí iría la llamada POST a la API para gastar los recursos en la blockchain
    // ...

    // Si la TX es exitosa, se actualiza el estado local de la construcción
    const buildingId = `${currentPlayerIndex}-road-${hexId}-${edgeId}`
    const newBuilding: Building = { hexId, type: "road", playerId: currentPlayerIndex, id: buildingId, vertexId: edgeId }

    const newPlayers = [...players]
    newPlayers[currentPlayerIndex].buildings.roads -= 1

    setBuildings([...buildings, newBuilding])
    setPlayers(newPlayers)
    setTimeout(fetchBalances, 500);
  }

  const buildSettlement = (hexId: number, vertexId: number) => { /* ... */ }
  const upgradeCity = (hexId: number, vertexId: number) => { /* ... */ }
  const tradeWithBank = (give: Record<string, number>, receive: Record<string, number>) => { /* ... */ }
  const endTurn = () => { /* ... */ }
  const selectHex = (hexId: number) => setSelectedHex(hexId);


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
    fetchBalances,
  }
}