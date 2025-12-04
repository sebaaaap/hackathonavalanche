import type { NextApiRequest, NextApiResponse } from "next"

interface BuildingPlacementRequest {
  playerWallet: string
  buildingType: "settlement" | "city" | "road"
  position: { x: number; y: number }
  signature: string
}

interface BuildingPlacementResponse {
  success: boolean
  transactionHash?: string
  error?: string
}

export default async function handler(req: NextApiRequest, res: NextApiResponse<BuildingPlacementResponse>) {
  if (req.method !== "POST") {
    return res.status(405).json({
      success: false,
      error: "Method not allowed",
    })
  }

  try {
    const { playerWallet, buildingType, position, signature } = req.body as BuildingPlacementRequest

    // TODO: Implementar llamada a smart contract de Avalanche
    // Ejemplo con ethers.js:
    // const provider = new ethers.providers.JsonRpcProvider(AVALANCHE_RPC_URL)
    // const contract = new ethers.Contract(CONTRACT_ADDRESS, CONTRACT_ABI, provider)
    // const tx = await contract.placeBuilding(buildingType, position.x, position.y, signature)
    // const receipt = await tx.wait()

    res.status(200).json({
      success: true,
      transactionHash: "0x" + Math.random().toString(16).slice(2), // Placeholder
    })
  } catch (error) {
    console.error("Error placing building:", error)
    res.status(500).json({
      success: false,
      error: "Failed to place building",
    })
  }
}
