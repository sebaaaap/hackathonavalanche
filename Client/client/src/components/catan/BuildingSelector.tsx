"use client"
import type { Player } from "../../types/catan"

interface BuildingSelectorProps {
  onBuildRoad: () => void
  onBuildSettlement: () => void
  onUpgradeCity: () => void
  selectedType: string | null
  player: Player | undefined
}

const BUILDING_COSTS = {
  road: { wood: 1, brick: 1 },
  settlement: { wood: 1, brick: 1, sheep: 1, wheat: 1 },
  city: { ore: 3, wheat: 2 },
}

export default function BuildingSelector({
  onBuildRoad,
  onBuildSettlement,
  onUpgradeCity,
  selectedType,
  player,
}: BuildingSelectorProps) {
  if (!player) return null

  const canBuildRoad =
    player.resources.wood >= BUILDING_COSTS.road.wood &&
    player.resources.brick >= BUILDING_COSTS.road.brick &&
    player.buildings.roads > 0

  const canBuildSettlement =
    player.resources.wood >= BUILDING_COSTS.settlement.wood &&
    player.resources.brick >= BUILDING_COSTS.settlement.brick &&
    player.resources.sheep >= BUILDING_COSTS.settlement.sheep &&
    player.resources.wheat >= BUILDING_COSTS.settlement.wheat &&
    player.buildings.settlements > 0

  const canBuildCity =
    player.resources.ore >= BUILDING_COSTS.city.ore &&
    player.resources.wheat >= BUILDING_COSTS.city.wheat &&
    player.buildings.cities > 0

  return (
    <div className="building-selector">
      <h3>Construir</h3>

      <button
        className={`btn-build ${selectedType === "road" ? "selected" : ""} ${!canBuildRoad ? "disabled" : ""}`}
        onClick={onBuildRoad}
        disabled={!canBuildRoad}
        title={`Requiere: 1 Madera, 1 Ladrillo`}
      >
        🛣️ Camino
      </button>

      <button
        className={`btn-build ${selectedType === "settlement" ? "selected" : ""} ${!canBuildSettlement ? "disabled" : ""}`}
        onClick={onBuildSettlement}
        disabled={!canBuildSettlement}
        title={`Requiere: 1 Madera, 1 Ladrillo, 1 Oveja, 1 Trigo`}
      >
        🏘️ Poblado
      </button>

      <button
        className={`btn-build ${selectedType === "city" ? "selected" : ""} ${!canBuildCity ? "disabled" : ""}`}
        onClick={onUpgradeCity}
        disabled={!canBuildCity}
        title={`Requiere: 3 Minerales, 2 Trigo`}
      >
        🏰 Ciudad
      </button>
    </div>
  )
}
