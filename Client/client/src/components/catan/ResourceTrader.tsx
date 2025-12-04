"use client"

import { useState } from "react"
import type { Player } from "../../types/catan"

interface ResourceTraderProps {
  player: Player | undefined
  onTrade: (give: Record<string, number>, receive: Record<string, number>) => void
}

export default function ResourceTrader({ player, onTrade }: ResourceTraderProps) {
  const [giveResource, setGiveResource] = useState<string | null>(null)
  const [giveAmount, setGiveAmount] = useState(4)
  const [receiveResource, setReceiveResource] = useState<string | null>(null)

  if (!player) return null

  const handleTrade = () => {
    if (!giveResource || !receiveResource || giveAmount < 1) return

    const give: Record<string, number> = { [giveResource]: giveAmount }
    const receive: Record<string, number> = { [receiveResource]: 1 }

    onTrade(give, receive)
    setGiveResource(null)
    setReceiveResource(null)
    setGiveAmount(4)
  }

  const resources = ["wood", "brick", "sheep", "wheat", "ore"]
  const resourceNames: Record<string, string> = {
    wood: "Madera",
    brick: "Ladrillo",
    sheep: "Oveja",
    wheat: "Trigo",
    ore: "Mineral",
  }

  const canTrade =
    giveResource &&
    receiveResource &&
    giveResource !== receiveResource &&
    player.resources[giveResource as keyof typeof player.resources] >= giveAmount

  return (
    <div className="resource-trader">
      <h3>Comerciar con el Banco</h3>

      <div className="trade-setup">
        <div className="trade-section">
          <label>Dar:</label>
          <select value={giveResource || ""} onChange={(e) => setGiveResource(e.target.value || null)}>
            <option value="">Seleccionar...</option>
            {resources.map((r) => (
              <option key={r} value={r}>
                {resourceNames[r]} ({player.resources[r as keyof typeof player.resources]})
              </option>
            ))}
          </select>
          <input
            type="number"
            min="1"
            max="10"
            value={giveAmount}
            onChange={(e) => setGiveAmount(Math.max(1, Number.parseInt(e.target.value) || 1))}
          />
        </div>

        <div className="trade-arrow">⇄</div>

        <div className="trade-section">
          <label>Recibir:</label>
          <select value={receiveResource || ""} onChange={(e) => setReceiveResource(e.target.value || null)}>
            <option value="">Seleccionar...</option>
            {resources.map((r) => (
              <option key={r} value={r}>
                {resourceNames[r]}
              </option>
            ))}
          </select>
          <span className="receive-amount">1</span>
        </div>
      </div>

      <button className="btn-trade-confirm" onClick={handleTrade} disabled={!canTrade}>
        Comerciar
      </button>
    </div>
  )
}
