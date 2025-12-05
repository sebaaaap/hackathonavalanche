"use client"
import Hexagon from "./Hexagon"
import type { Hex, Building } from "../../types/catan"

interface GameBoardProps {
  hexagons: Hex[]
  buildings: Building[]
  selectedHex: number | null
  onHexSelect: (hexId: number) => void
}

export default function GameBoard({ hexagons, buildings, selectedHex, onHexSelect }: GameBoardProps) {
  const HEX_SIZE = 80
  const HEX_WIDTH = HEX_SIZE * 2
  const HEX_HEIGHT = HEX_SIZE * Math.sqrt(3)

  const getHexPosition = (index: number) => {
    const rings = [
      { start: 0, count: 1, radius: 0 },
      { start: 1, count: 6, radius: 1 },
      { start: 7, count: 12, radius: 2 },
    ]

    let ring = 0
    let posInRing = index
    let offset = 0

    for (const r of rings) {
      if (index < r.start + r.count) {
        ring = r.radius
        posInRing = index - r.start
        offset = r.start
        break
      }
    }

    const angle = (posInRing / (ring === 0 ? 1 : ring * 6)) * Math.PI * 2
    const x = Math.cos(angle) * ring * HEX_WIDTH * 0.86
    const y = Math.sin(angle) * ring * HEX_HEIGHT * 0.86

    return { x: x + 500, y: y + 400 }
  }

  return (
    <div className="game-board">
      <svg width="1000" height="800" className="hex-grid">
        {hexagons.map((hex, index) => {
          const pos = getHexPosition(index)
          const buildingsOnHex = buildings.filter((b) => b.hexId === index)
          const isSelected = selectedHex === index

          return (
            <g
              key={hex.id}
              transform={`translate(${pos.x}, ${pos.y})`}
              onClick={() => onHexSelect(index)}
              className={`hex-group ${isSelected ? "selected" : ""}`}
            >
              <Hexagon hex={hex} size={HEX_SIZE} buildings={buildingsOnHex} isSelected={isSelected} />
            </g>
          )
        })}
      </svg>
    </div>
  )
}
