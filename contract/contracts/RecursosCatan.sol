// SPDX-License-Identifier: MIT
// Compatible with OpenZeppelin Contracts ^5.0.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC1155/ERC1155.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

// 1. CAMBIO DE NOMBRE: Ahora representa todo el juego, no solo madera
contract RecursosCatan is ERC1155, Ownable {
    // Constructor simple (sin initializers complejos)
    constructor(
        address initialOwner
    ) ERC1155("https://example.com/metadata/{id}.json") Ownable(initialOwner) {}

    // Función para cambiar la URI si mueves tu servidor de metadatos
    function setURI(string memory newuri) public onlyOwner {
        _setURI(newuri);
    }

    // Función para crear recursos (Uno por uno)
    function mint(
        address account,
        uint256 id,
        uint256 amount,
        bytes memory data
    ) public onlyOwner {
        _mint(account, id, amount, data);
    }

    // Función para crear lotes (Ej: Dar madera, trigo y oveja de golpe)
    function mintBatch(
        address to,
        uint256[] memory ids,
        uint256[] memory amounts,
        bytes memory data
    ) public onlyOwner {
        _mintBatch(to, ids, amounts, data);
    }
}
