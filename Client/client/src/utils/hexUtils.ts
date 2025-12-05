import type { HexTile } from "../types/catan"

const TILE_TYPES = ["forest", "hill", "field", "pasture", "mountain", "desert"] as const
const NUMBERS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

const FIXED_SEED = 42
function seededRandom(seed: number): number {
  const x = Math.sin(seed) * 10000
  return x - Math.floor(x)
}

export function generateHexGrid(): HexTile[] {
  const hexes: HexTile[] = []
  const SIZE = 60
  const RADIUS = 2

  let numberIndex = 0
  let seedCounter = FIXED_SEED

  for (let x = -RADIUS; x <= RADIUS; x++) {
    for (let y = -RADIUS; y <= RADIUS; y++) {
      if (Math.abs(x + y) <= RADIUS) {
        const pixelX = 450 + x * SIZE * 1.5
        const pixelY = 400 + y * SIZE * Math.sqrt(3)

        const tileType = TILE_TYPES[Math.floor(seededRandom(seedCounter) * TILE_TYPES.length)]
        seedCounter++

        const isDesert = tileType === "desert"
        const number = isDesert ? undefined : NUMBERS[numberIndex++]

        hexes.push({
          x,
          y,
          pixelX,
          pixelY,
          type: tileType,
          number,
          resource: isDesert
            ? undefined
            : tileType === "forest"
              ? "wood"
              : tileType === "hill"
                ? "brick"
                : tileType === "pasture"
                  ? "sheep"
                  : tileType === "field"
                    ? "wheat"
                    : "ore",
        })
      }
    }
  }

  return hexes
}

export function calculateHexDistance(hex1: { x: number; y: number }, hex2: { x: number; y: number }): number {
  return (Math.abs(hex1.x - hex2.x) + Math.abs(hex1.y - hex2.y) + Math.abs(hex1.x + hex1.y - hex2.x - hex2.y)) / 2
}
