"use client"

import { useState, useEffect } from "react"
import type { Player, Hex, Building, ResourceCount } from "../types/catan"

const RESOURCE_TYPES = ["forest", "hill", "field", "pasture", "mountain", "desert"]
const RESOURCE_MAPPING: Record<string, keyof ResourceCount> = {
  forest: "wood",
  hill: "brick",
  field: "wheat",
  pasture: "sheep",
  mountain: "ore",
}

function initializeBoard(): Hex[] {
  const hexagons: Hex[] = []
  const numbers = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

  // Centro
  hexagons.push({
    id: 0,
    resourceType: RESOURCE_TYPES[Math.floor(Math.random() * 5)],
    number: numbers[Math.floor(Math.random() * numbers.length)],
  })

  // Primer anillo (6 hexágonos)
  for (let i = 1; i < 7; i++) {
    hexagons.push({
      id: i,
      resourceType: RESOURCE_TYPES[Math.floor(Math.random() * 5)],
      number: numbers[Math.floor(Math.random() * numbers.length)],
    })
  }

  // Segundo anillo (12 hexágonos)
  for (let i = 7; i < 19; i++) {
    hexagons.push({
      id: i,
      resourceType: RESOURCE_TYPES[Math.floor(Math.random() * 6)],
      number: i % 3 === 0 ? null : numbers[Math.floor(Math.random() * numbers.length)],
    })
  }

  return hexagons
}

function initializePlayers(): Player[] {
  const players: Player[] = []
  for (let i = 0; i < 4; i++) {
    players.push({
      id: i,
      name: `Jugador ${i + 1}`,
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

  const rollDice = (total: number) => {
    const newPlayers = [...players]

    board.hexagons.forEach((hex) => {
      if (hex.number === total && hex.resourceType !== "desert") {
        const resource = RESOURCE_MAPPING[hex.resourceType]

        buildings.forEach((building) => {
          if (building.hexId === hex.id) {
            const player = newPlayers[building.playerId]
            if (player) {
              const amount = building.type === "city" ? 2 : 1
              player.resources[resource] += amount
            }
          }
        })
      }
    })

    setPlayers(newPlayers)
    setGamePhase("building")
  }

  const buildRoad = (hexId: number, edgeId: number) => {
    const currentPlayer = players[currentPlayerIndex]
    if (currentPlayer.resources.wood < 1 || currentPlayer.resources.brick < 1) {
      alert("No tienes suficientes recursos (necesitas 1 madera y 1 ladrillo)")
      return
    }

    if (currentPlayer.buildings.roads <= 0) {
      alert("No tienes más caminos disponibles")
      return
    }

    const buildingId = `${currentPlayerIndex}-road-${hexId}-${edgeId}`
    const buildingExists = buildings.some((b) => b.id === buildingId)

    if (buildingExists) {
      alert("Ya hay una construcción aquí")
      return
    }

    const newBuilding: Building = {
      id: buildingId,
      hexId,
      vertexId: edgeId,
      type: "road",
      playerId: currentPlayerIndex,
    }

    const newPlayers = [...players]
    newPlayers[currentPlayerIndex].resources.wood -= 1
    newPlayers[currentPlayerIndex].resources.brick -= 1
    newPlayers[currentPlayerIndex].buildings.roads -= 1

    setBuildings([...buildings, newBuilding])
    setPlayers(newPlayers)
  }

  const buildSettlement = (hexId: number, vertexId: number) => {
    const currentPlayer = players[currentPlayerIndex]
    if (
      currentPlayer.resources.wood < 1 ||
      currentPlayer.resources.brick < 1 ||
      currentPlayer.resources.sheep < 1 ||
      currentPlayer.resources.wheat < 1
    ) {
      alert("No tienes suficientes recursos (necesitas 1 madera, 1 ladrillo, 1 oveja, 1 trigo)")
      return
    }

    if (currentPlayer.buildings.settlements <= 0) {
      alert("No tienes más poblados disponibles")
      return
    }

    const buildingId = `${currentPlayerIndex}-settlement-${hexId}-${vertexId}`
    const buildingExists = buildings.some((b) => b.id === buildingId)

    if (buildingExists) {
      alert("Ya hay una construcción aquí")
      return
    }

    const newBuilding: Building = {
      id: buildingId,
      hexId,
      vertexId,
      type: "settlement",
      playerId: currentPlayerIndex,
    }

    const newPlayers = [...players]
    newPlayers[currentPlayerIndex].resources.wood -= 1
    newPlayers[currentPlayerIndex].resources.brick -= 1
    newPlayers[currentPlayerIndex].resources.sheep -= 1
    newPlayers[currentPlayerIndex].resources.wheat -= 1
    newPlayers[currentPlayerIndex].buildings.settlements -= 1
    newPlayers[currentPlayerIndex].victoryPoints += 1

    setBuildings([...buildings, newBuilding])
    setPlayers(newPlayers)
  }

  const upgradeCity = (hexId: number, vertexId: number) => {
    const currentPlayer = players[currentPlayerIndex]
    if (currentPlayer.resources.ore < 3 || currentPlayer.resources.wheat < 2) {
      alert("No tienes suficientes recursos (necesitas 3 minerales y 2 trigo)")
      return
    }

    const buildingId = `${currentPlayerIndex}-settlement-${hexId}-${vertexId}`
    const settlement = buildings.find((b) => b.id === buildingId && b.type === "settlement")

    if (!settlement) {
      alert("No hay un poblado aquí para actualizar")
      return
    }

    if (currentPlayer.buildings.cities <= 0) {
      alert("No tienes más ciudades disponibles")
      return
    }

    const newBuildings = buildings.filter((b) => b.id !== buildingId)
    const newCity: Building = {
      id: `${currentPlayerIndex}-city-${hexId}-${vertexId}`,
      hexId,
      vertexId,
      type: "city",
      playerId: currentPlayerIndex,
    }

    const newPlayers = [...players]
    newPlayers[currentPlayerIndex].resources.ore -= 3
    newPlayers[currentPlayerIndex].resources.wheat -= 2
    newPlayers[currentPlayerIndex].buildings.cities -= 1
    newPlayers[currentPlayerIndex].buildings.settlements += 1
    newPlayers[currentPlayerIndex].victoryPoints += 1

    setBuildings([...newBuildings, newCity])
    setPlayers(newPlayers)
  }

  const tradeWithBank = (give: Record<string, number>, receive: Record<string, number>) => {
    const currentPlayer = players[currentPlayerIndex]

    for (const [resource, amount] of Object.entries(give)) {
      if (currentPlayer.resources[resource as keyof ResourceCount] < amount) {
        alert(`No tienes suficientes ${resource}`)
        return
      }
    }

    const newPlayers = [...players]

    for (const [resource, amount] of Object.entries(give)) {
      newPlayers[currentPlayerIndex].resources[resource as keyof ResourceCount] -= amount
    }

    for (const [resource, amount] of Object.entries(receive)) {
      newPlayers[currentPlayerIndex].resources[resource as keyof ResourceCount] += amount
    }

    setPlayers(newPlayers)
  }

  const endTurn = () => {
    const nextPlayerIndex = (currentPlayerIndex + 1) % players.length
    setCurrentPlayerIndex(nextPlayerIndex)
    setGamePhase("rolling")
    setSelectedHex(null)
    setSelectedBuildingType(null)
  }

  const selectHex = (hexId: number) => {
    setSelectedHex(selectedHex === hexId ? null : hexId)
  }

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
  }
}
