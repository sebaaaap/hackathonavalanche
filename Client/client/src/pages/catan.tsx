"use client"

import { useState } from "react"
import GameBoard from "../components/catan/GameBoard"
import DiceRoller from "../components/catan/DiceRoller"
import BuildingSelector from "../components/catan/BuildingSelector"
import ResourceTrader from "../components/catan/ResourceTrader"
import GameState from "../components/catan/GameState"
import { useGameStore } from "../hooks/useGameStore"
import "../styles/catan.css"

export default function CatanPage() {
  const gameState = useGameStore()
  const [showTrader, setShowTrader] = useState(false)

  const handleDiceRoll = (total: number) => {
    gameState.rollDice(total)
  }

  const handleBuildRoad = (hexId: number, edgeId: number) => {
    gameState.buildRoad(hexId, edgeId)
  }

  const handleBuildSettlement = (hexId: number, vertexId: number) => {
    gameState.buildSettlement(hexId, vertexId)
  }

  const handleUpgradeCity = (hexId: number, vertexId: number) => {
    gameState.upgradeCity(hexId, vertexId)
  }

  const handleTrade = (give: Record<string, number>, receive: Record<string, number>) => {
    gameState.tradeWithBank(give, receive)
  }

  const handleEndTurn = () => {
    gameState.endTurn()
  }

  const currentPlayer = gameState.players[gameState.currentPlayerIndex]

  return (
    <div className="catan-container">
      <header className="catan-header">
        <h1>Catan</h1>
        <p>Estrategia · Comercio · Expansión</p>
      </header>

      <main className="catan-main">
        <div className="game-area">
          <GameBoard
            hexagons={gameState.board.hexagons}
            buildings={gameState.buildings}
            selectedHex={gameState.selectedHex}
            onHexSelect={gameState.selectHex}
          />
        </div>

        <aside className="game-sidebar">
          <GameState
            currentPlayer={currentPlayer}
            currentPlayerIndex={gameState.currentPlayerIndex}
            players={gameState.players}
            gamePhase={gameState.gamePhase}
          />

          <div className="control-panel">
            <DiceRoller onRoll={handleDiceRoll} disabled={gameState.gamePhase !== "rolling"} />

            {gameState.gamePhase === "building" && (
              <>
                <BuildingSelector
                  onBuildRoad={() => gameState.setSelectedBuildingType("road")}
                  onBuildSettlement={() => gameState.setSelectedBuildingType("settlement")}
                  onUpgradeCity={() => gameState.setSelectedBuildingType("city")}
                  selectedType={gameState.selectedBuildingType}
                  player={currentPlayer}
                />
                <button className="btn-trade" onClick={() => setShowTrader(!showTrader)}>
                  {showTrader ? "Cerrar" : "Comerciar"}
                </button>
              </>
            )}

            {showTrader && <ResourceTrader player={currentPlayer} onTrade={handleTrade} />}

            {gameState.gamePhase === "building" && (
              <button className="btn-end-turn" onClick={handleEndTurn}>
                Terminar Turno
              </button>
            )}
          </div>
        </aside>
      </main>
    </div>
  )
}
