import type { Player } from "../../types/catan"

interface PlayerPanelProps {
  player: Player
  isCurrentPlayer: boolean
}

const PLAYER_COLORS = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#ffa502"]

export default function PlayerPanel({ player, isCurrentPlayer }: PlayerPanelProps) {
  const playerColor = PLAYER_COLORS[player.id]

  return (
    <div className={`player-panel ${isCurrentPlayer ? "active" : ""}`} style={{ borderLeftColor: playerColor }}>
      <div className="player-header">
        <h3>Jugador {player.id + 1}</h3>
        <span className="player-points">{player.victoryPoints} puntos</span>
      </div>

      <div className="resources-grid">
        <div className="resource-item">
          <span className="resource-icon">🌲</span>
          <span className="resource-count">{player.resources.wood}</span>
        </div>
        <div className="resource-item">
          <span className="resource-icon">🧱</span>
          <span className="resource-count">{player.resources.brick}</span>
        </div>
        <div className="resource-item">
          <span className="resource-icon">🐑</span>
          <span className="resource-count">{player.resources.sheep}</span>
        </div>
        <div className="resource-item">
          <span className="resource-icon">🌾</span>
          <span className="resource-count">{player.resources.wheat}</span>
        </div>
        <div className="resource-item">
          <span className="resource-icon">⛏️</span>
          <span className="resource-count">{player.resources.ore}</span>
        </div>
      </div>

      <div className="buildings-info">
        <p>Caminos: {player.buildings.roads}</p>
        <p>Poblados: {player.buildings.settlements}</p>
        <p>Ciudades: {player.buildings.cities}</p>
      </div>
    </div>
  )
}
