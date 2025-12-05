"use client"
import type { Hex } from "../../types/catan"

interface HexagonProps {
  hex: Hex
  size: number
  buildings: any[]
  isSelected: boolean
  // Opcional: Prop para controlar la orientación desde fuera
  orientation?: "flat" | "pointy"
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

export default function Hexagon({ hex, size, isSelected, orientation = "flat" }: HexagonProps) {
  const angle = (Math.PI * 2) / 6
  const centerX = 0
  const centerY = 0

  // CALCULO DEL ÁNGULO:
  // Si queremos "Flat-topped" (Lado plano arriba): offset = 0
  // Si queremos "Pointy-topped" (Punta arriba): offset = Math.PI / 6 (30 grados) o -Math.PI/2 (-90 grados para empezar arriba)

  // Tu código original tenía offset de 30° (Punta arriba). 
  // Aquí lo ajusto a 0° para Lado Plano Arriba, o -90° para Punta Arriba estricta.
  const angleOffset = orientation === "flat"
    ? 0
    : -Math.PI / 2; // -90 grados asegura que el primer punto sea la punta superior exacta

  const points = Array.from({ length: 6 })
    .map((_, i) => {
      // Aplicamos el offset según la orientación deseada
      const a = (angle * i) + angleOffset;
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
          <circle cx={centerX} cy={centerY} r={size * 0.4} fill="#fff" stroke="#333" strokeWidth={2} />
          <text
            x={centerX}
            y={centerY}
            textAnchor="middle"
            dy="0.3em"
            className="font-bold text-lg select-none pointer-events-none"
            fill="#000"
          >
            {hex.number}
          </text>
        </>
      )}

      {/* Selection highlight */}
      {isSelected && (
        <polygon
          points={points}
          fill="none"
          stroke="#ff6b6b"
          strokeWidth={2}
          strokeDasharray="5,5"
        />
      )}
    </g>
  )
}