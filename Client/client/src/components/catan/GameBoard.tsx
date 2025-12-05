"use client"

// 1. TIPOS DE DATOS DEFINIDOS EN ESTE ARCHIVO (Para hacerlo autocontenido)
// Se asume que Hex tiene 'q' y 'r' para el posicionamiento hexagonal axial.
type Hex = {
  id: number;
  type: string; // Tipo de recurso (ej: 'forest', 'brick', 'desert')
  number: number; // Número de token (2-12)
  q: number; // Coordenada Axial Q
  r: number; // Coordenada Axial R
}

type Building = {
  hexId: number;
  type: 'settlement' | 'city';
  ownerId: number;
  position: number; // Posición en el hexágono (ej: 0-5 para los vértices)
}

// 2. COMPONENTE HEXAGON (Integrado para resolver el error de importación)
// Este es un placeholder funcional que dibuja un hexágono SVG básico y su número.
const Hexagon = ({ hex, size, buildings, isSelected }: { hex: Hex, size: number, buildings: Building[], isSelected: boolean }) => {
  const SQRT3 = Math.sqrt(3);
  const width = size * 2;
  const height = size * SQRT3;
  const points = [
    `${size}, 0`,
    `${size / 2}, ${height / 2}`,
    `${-size / 2}, ${height / 2}`,
    `${-size}, 0`,
    `${-size / 2}, ${-height / 2}`,
    `${size / 2}, ${-height / 2}`,
  ].join(' ');

  const getFillColor = (type: string) => {
    switch (type) {
      case 'forest': return '#22c55e'; // Verde para madera
      case 'brick': return '#b91c1c'; // Rojo para arcilla
      case 'sheep': return '#fcd34d'; // Amarillo para oveja
      case 'wheat': return '#fde047'; // Dorado para trigo
      case 'ore': return '#9ca3af';   // Gris para mineral
      case 'desert': return '#f59e0b'; // Naranja para desierto
      default: return '#e5e7eb';
    }
  };

  const buildingColorMap = ['#3b82f6', '#ef4444', '#10b981', '#f97316']; // Colores de ejemplo para jugadores

  return (
    <g className="transition-transform duration-300">
      {/* Hexágono de Terreno */}
      <polygon
        points={points}
        fill={getFillColor(hex.type)}
        stroke={isSelected ? '#3b82f6' : '#6b7280'}
        strokeWidth={isSelected ? 4 : 2}
        className="cursor-pointer transition-all duration-150 hover:opacity-90"
        style={{ transform: `scale(${isSelected ? 1.05 : 1})` }}
      />
      {/* Círculo de Número */}
      {hex.number > 0 && (
        <g className="pointer-events-none">
          <circle r={size * 0.3} fill={hex.number === 6 || hex.number === 8 ? '#fef2f2' : '#fef08a'} />
          <text
            x="0"
            y="4"
            textAnchor="middle"
            fontSize={size * 0.3}
            fontWeight="bold"
            fill={hex.number === 6 || hex.number === 8 ? '#dc2626' : '#1f2937'}
            className="select-none"
          >
            {hex.number}
          </text>
        </g>
      )}

      {/* Renderizado de Edificios (Placerholders en los vértices) */}
      {buildings.map((building, idx) => {
        // Posición de los vértices (0-5, donde 0 es la esquina superior-derecha)
        const angle = (building.position * 60 - 30) * (Math.PI / 180);
        const r = size - 10; // Distancia del centro
        const vx = r * Math.cos(angle);
        const vy = r * Math.sin(angle);

        const buildingSize = building.type === 'city' ? 14 : 10;
        const shape = building.type === 'city' ? 'rect' : 'circle';

        return (
          <g key={idx} transform={`translate(${vx}, ${vy})`} className="drop-shadow-sm">
            {shape === 'circle' ? (
              <circle
                r={buildingSize}
                fill={buildingColorMap[building.ownerId % buildingColorMap.length]}
                stroke="#1f2937"
                strokeWidth="2"
              />
            ) : (
              <rect
                width={buildingSize * 1.5}
                height={buildingSize * 1.5}
                x={-buildingSize * 0.75}
                y={-buildingSize * 0.75}
                fill={buildingColorMap[building.ownerId % buildingColorMap.length]}
                stroke="#1f2937"
                strokeWidth="2"
                rx="3"
              />
            )}
          </g>
        );
      })}
    </g>
  );
}

// 3. COMPONENTE GAMEBOARD (Lógica de posicionamiento axial)
interface GameBoardProps {
  hexagons: Hex[]
  buildings: Building[]
  selectedHex: number | null
  onHexSelect: (hexId: number) => void
}

/**
 * Componente principal para renderizar el tablero de Catan.
 * Utiliza coordenadas axiales para el posicionamiento preciso de los hexágonos.
 */
export default function GameBoard({ hexagons, buildings, selectedHex, onHexSelect }: GameBoardProps) {
  const HEX_SIZE = 80
  const SQRT3 = Math.sqrt(3)

  /**
   * @description Converts axial coordinates (q, r) to screen pixel coordinates (x, y).
   * Uses the 'Pointy Top' system (points facing up).
   * @param q Axial coordinate Q (column)
   * @param r Axial coordinate R (row)
   * @param size The size of the hexagon edge
   */
  const axialToPixel = (q: number, r: number, size: number) => {
    // Calculation based on hexagonal geometry (Pointy Top)
    // X Coordinate: (Q + R/2) * Size * SQRT(3)
    const x = size * SQRT3 * (q + r / 2)
    // Y Coordinate: R * Size * 1.5
    const y = size * (r * 1.5)

    // Offset to center the board in the SVG (500, 400 is the center of the SVG)
    return {
      x: x + 500,
      y: y + 400
    }
  }

  return (
    <div className="game-board flex justify-center items-center h-full w-full">
      {/* El tamaño del SVG debe ser suficiente para contener el tablero centrado */}
      <svg width="1000" height="800" className="hex-grid shadow-2xl rounded-xl bg-gray-50/50">
        {hexagons.map((hex) => {
          // Utilizamos las coordenadas axiales (hex.q, hex.r) para obtener la posición precisa.
          const pos = axialToPixel(hex.q, hex.r, HEX_SIZE)

          const buildingsOnHex = buildings.filter((b) => b.hexId === hex.id) // Usar hex.id es más seguro que index
          const isSelected = selectedHex === hex.id

          return (
            <g
              key={hex.id}
              transform={`translate(${pos.x}, ${pos.y})`}
              onClick={() => onHexSelect(hex.id)} // Usar hex.id es más seguro que index
              className={`hex-group ${isSelected ? "selected" : ""}`}
            >
              <Hexagon
                hex={hex}
                size={HEX_SIZE}
                buildings={buildingsOnHex}
                isSelected={isSelected}
              />
            </g>
          )
        })}
      </svg>
    </div>
  )
}