import type { Hex, Building } from "../../types/catan"

interface HexagonProps {
  hex: Hex
  size: number
  buildings: Building[]
  isSelected: boolean
}

const RESOURCE_COLORS: Record<string, string> = {
  forest: "#2d5016",
  hill: "#8b4513",
  field: "#daa520",
  pasture: "#90ee90",
  mountain: "#a9a9a9",
  desert: "#f4a460",
}

export default function Hexagon({ hex, size, buildings, isSelected }: HexagonProps) {
  const points = []
  for (let i = 0; i < 6; i++) {
    const angle = (Math.PI / 3) * i
    const x = size * Math.cos(angle)
    const y = size * Math.sin(angle)
    points.push([x, y])
  }

  const pointsStr = points.map((p) => `${p[0]},${p[1]}`).join(" ")
  const backgroundColor = RESOURCE_COLORS[hex.resourceType] || "#ccc"

  const settlementPositions = [
    { x: 0, y: -size * 0.7 },
    { x: size * 0.6, y: -size * 0.35 },
    { x: size * 0.6, y: size * 0.35 },
    { x: 0, y: size * 0.7 },
    { x: -size * 0.6, y: size * 0.35 },
    { x: -size * 0.6, y: -size * 0.35 },
  ]

  return (
    <>
      <polygon
        points={pointsStr}
        fill={backgroundColor}
        stroke={isSelected ? "#ffd700" : "#333"}
        strokeWidth={isSelected ? 3 : 1}
        className="hexagon"
      />
      <text x="0" y="0" textAnchor="middle" dy="0.3em" className="hex-number">
        {hex.number || "-"}
      </text>

      {buildings.map((building, idx) => {
        const pos = settlementPositions[building.vertexId] || { x: 0, y: 0 }
        const PLAYER_COLORS = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#ffa502"]
        const color = PLAYER_COLORS[building.playerId]

        if (building.type === "road") {
          return (
            <line
              key={`road-${idx}`}
              x1={settlementPositions[building.vertexId].x}
              y1={settlementPositions[building.vertexId].y}
              x2={settlementPositions[(building.vertexId + 1) % 6].x}
              y2={settlementPositions[(building.vertexId + 1) % 6].y}
              stroke={color}
              strokeWidth="3"
            />
          )
        }

        if (building.type === "settlement") {
          return (
            <circle key={`settlement-${idx}`} cx={pos.x} cy={pos.y} r="8" fill={color} stroke="#fff" strokeWidth="2" />
          )
        }

        if (building.type === "city") {
          return (
            <rect
              key={`city-${idx}`}
              x={pos.x - 7}
              y={pos.y - 7}
              width="14"
              height="14"
              fill={color}
              stroke="#fff"
              strokeWidth="2"
            />
          )
        }

        return null
      })}
    </>
  )
}
