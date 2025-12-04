# Catan - Blockchain Integration Guide

## 📋 Overview

Este documento describe cómo integrar el juego de Catan con la blockchain de Avalanche para crear un juego completamente descentralizado y transparente.

## 🎮 Game State Management

### Current Implementation
- **Hook**: `useGameStore.ts` - Maneja el estado del juego en cliente
- **API Routes**: 
  - `/api/blockchain/place-building.ts` - Registra edificios en blockchain
  - `/api/blockchain/roll-dice.ts` - Registra tiradas de dados

### Next Steps

1. **Conectar con Web3**
   \`\`\`typescript
   // client/src/hooks/useWeb3.ts
   import { useAccount, useConnect } from 'wagmi'
   
   export function useWeb3() {
     const { address } = useAccount()
     // Implementar wallet connection
   }
   \`\`\`

2. **Implementar Smart Contract Calls**
   \`\`\`typescript
   // Usar ethers.js o viem para llamar al contrato
   const tx = await catan.placeBuilding(buildingType, xPos, yPos)
   const receipt = await tx.wait()
   \`\`\`

3. **Sincronizar estado local con blockchain**
   - Escuchar eventos del contrato
   - Actualizar estado en tiempo real
   - Validar todas las acciones en el contrato

## 🔗 Smart Contract Functions

### Core Functions

**placeBuilding(buildingType, xPos, yPos)**
- Valida que el jugador tiene recursos
- Deduce recursos
- Registra el edificio
- Actualiza puntos de victoria

**rollDice()**
- Genera un número aleatorio verificable
- Registra la tirada
- Permite que otros jugadores verifiquen

**grantResources(player, resource, amount)**
- Solo admins pueden llamar
- Distribuye recursos según números de dados

## 🎯 Integration Checklist

- [ ] Configurar Web3 provider (Avalanche Mainnet o Testnet)
- [ ] Desplegar smart contract
- [ ] Actualizar `useGameStore.ts` para llamar al contrato
- [ ] Implementar wallet connection
- [ ] Agregar verificación de transacciones
- [ ] Agregar eventos blockchain a UI
- [ ] Implementar game state sincronización
- [ ] Agregar validación en tiempo real
- [ ] Testing en testnet
- [ ] Audit de seguridad

## 📦 Required Dependencies

\`\`\`json
{
  "wagmi": "^2.0.0",
  "viem": "^2.0.0",
  "ethers": "^6.0.0",
  "@web3modal/wagmi": "^3.0.0"
}
\`\`\`

## 🚀 Deployment

1. Deploy a Avalanche C-Chain
2. Update contract address en `.env`
3. Configurar RPC endpoints
4. Publicar en Vercel

## 📝 Notes

- Todas las acciones deben ser verificables en blockchain
- Los datos críticos (recursos, edificios) deben estar en el contrato
- Considerar costos de gas y UX
- Implementar mecanismos anti-cheat
