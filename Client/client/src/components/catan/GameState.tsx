import type { Player } from "../../types/catan"
import PlayerPanel from "./PlayerPanel"

interface GameStateProps {
  currentPlayer: Player | undefined
  currentPlayerIndex: number
  players: Player[]
  gamePhase: string
}

export default function GameState({ currentPlayer, currentPlayerIndex, players, gamePhase }: GameStateProps) {
  if (!players || players.length === 0) {
    return <div className="game-state">Cargando...</div>
  }

  const phaseTexts: Record<string, string> = {
    setup: "Configuración",
    rolling: "Lanzar dados",
    building: "Construir",
    trading: "Comerciar",
    finished: "Partida terminada",
  }

  const totalPoints = players.reduce((sum, p) => sum + p.victoryPoints, 0)

  return (
    <div className="game-state">
      <div className="game-info">
        <h2>Estado del Juego</h2>
        <p className="game-phase">Fase: {phaseTexts[gamePhase] || gamePhase}</p>
        <p className="current-player">Turno: Jugador {currentPlayerIndex + 1}</p>
      </div>

      <div className="players-list">
        {players.map((player, idx) => (
          <PlayerPanel key={player.id} player={player} isCurrentPlayer={idx === currentPlayerIndex} />
        ))}
      </div>

      <div className="game-stats">
        <p>Puntos Totales: {totalPoints}</p>
      </div>
    </div>
  )
}
