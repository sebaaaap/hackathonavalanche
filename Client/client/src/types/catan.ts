export interface ResourceCount {
  wood: number
  brick: number
  sheep: number
  wheat: number
  ore: number
}

export interface BuildingCount {
  roads: number
  settlements: number
  cities: number
}

export interface Player {
  id: number
  name: string
  resources: ResourceCount
  buildings: BuildingCount
  victoryPoints: number
}

export interface Hex {
  id: number
  resourceType: string
  number: number | null
}

export interface Building {
  id: string
  hexId: number
  vertexId: number
  type: "road" | "settlement" | "city"
  playerId: number
}

export interface Board {
  hexagons: Hex[]
}

export interface GameStoreState {
  players: Player[]
  board: Board
  buildings: Building[]
  currentPlayerIndex: number
  gamePhase: "setup" | "rolling" | "building" | "trading" | "finished"
  selectedHex: number | null
  selectedBuildingType: string | null
}

export interface HexTile {
  x: number
  y: number
  pixelX: number
  pixelY: number
  type: "forest" | "hill" | "field" | "pasture" | "mountain" | "desert"
  number?: number
  resource?: "wood" | "brick" | "sheep" | "wheat" | "ore"
}
