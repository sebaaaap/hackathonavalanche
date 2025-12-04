import type { NextApiRequest, NextApiResponse } from "next"

interface DiceRollRequest {
  playerWallet: string
  diceResult: number
  timestamp: number
  signature: string
}

interface DiceRollResponse {
  success: boolean
  transactionHash?: string
  error?: string
}

export default async function handler(req: NextApiRequest, res: NextApiResponse<DiceRollResponse>) {
  if (req.method !== "POST") {
    return res.status(405).json({
      success: false,
      error: "Method not allowed",
    })
  }

  try {
    const { playerWallet, diceResult, timestamp, signature } = req.body as DiceRollRequest

    // TODO: Implementar registro en blockchain
    // Esto permite que todos puedan verificar la tirada

    res.status(200).json({
      success: true,
      transactionHash: "0x" + Math.random().toString(16).slice(2),
    })
  } catch (error) {
    console.error("Error recording dice roll:", error)
    res.status(500).json({
      success: false,
      error: "Failed to record dice roll",
    })
  }
}
