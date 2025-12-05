"use client"
import type { Hex } from "../../types/catan"

interface HexagonProps {
  hex: Hex
  size: number
  buildings: any[]
  isSelected: boolean
}

const TILE_COLORS: Record<string, string> = {
  forest: "#2d5016",
  hill: "#a67c52",
  field: "#f4d03f",
  pasture: "#7cb342",
  mountain: "#8b8b8b",
  desert: "#e8d7b8",
  water: "#4a90e2",
}

export default function Hexagon({ hex, size, isSelected }: HexagonProps) {
  const angle = (Math.PI * 2) / 6
  const centerX = 0
  const centerY = 0

  const points = Array.from({ length: 6 })
    .map((_, i) => {
      const a = (angle * i) - (Math.PI / 6);
      const x = Math.round((centerX + size * Math.cos(a)) * 100) / 100
      const y = Math.round((centerY + size * Math.sin(a)) * 100) / 100
      return `${x},${y}`
    })
    .join(" ")

  const fill = TILE_COLORS[hex.resourceType] || "#cccccc"

  return (
    <g style={{ cursor: "pointer" }}>
      {/* Main hexagon */}
      <polygon
        points={points}
        fill={fill}
        stroke={isSelected ? "#ff6b6b" : "#333"}
        strokeWidth={isSelected ? 3 : 1}
        opacity={0.8}
      />

      {/* Resource number circle */}
      {hex.number && (
        <>
          <circle cx={centerX} cy={centerY} r={20} fill="#fff" stroke="#333" strokeWidth={2} />
          <text x={centerX} y={centerY} textAnchor="middle" dy="0.3em" className="font-bold text-lg" fill="#000">
            {hex.number}
          </text>
        </>
      )}

      {/* Selection highlight */}
      {isSelected && <polygon points={points} fill="none" stroke="#ff6b6b" strokeWidth={2} strokeDasharray="5,5" />}
    </g>
  )
}
