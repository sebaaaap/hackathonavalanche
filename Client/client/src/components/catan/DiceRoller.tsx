"use client"

import { useState } from "react"

interface DiceRollerProps {
  onRoll: (total: number) => void
  disabled?: boolean
}

export default function DiceRoller({ onRoll, disabled = false }: DiceRollerProps) {
  const [dice, setDice] = useState<[number, number] | null>(null)
  const [rolling, setRolling] = useState(false)

  const handleRoll = () => {
    if (disabled || rolling) return

    setRolling(true)
    const animations = []

    for (let i = 0; i < 20; i++) {
      setTimeout(() => {
        setDice([Math.floor(Math.random() * 6) + 1, Math.floor(Math.random() * 6) + 1])
      }, i * 50)

      animations.push(i)
    }

    setTimeout(() => {
      const die1 = Math.floor(Math.random() * 6) + 1
      const die2 = Math.floor(Math.random() * 6) + 1
      setDice([die1, die2])
      setRolling(false)
      onRoll(die1 + die2)
    }, animations.length * 50)
  }

  return (
    <div className="dice-roller">
      <h3>Lanzar Dados</h3>
      <div className="dice-container">
        {dice ? (
          <>
            <div className="die">{dice[0]}</div>
            <div className="die">{dice[1]}</div>
            <div className="dice-sum">= {dice[0] + dice[1]}</div>
          </>
        ) : (
          <>
            <div className="die">?</div>
            <div className="die">?</div>
          </>
        )}
      </div>
      <button className="btn-roll" onClick={handleRoll} disabled={disabled || rolling}>
        {rolling ? "Lanzando..." : "Lanzar"}
      </button>
    </div>
  )
}
