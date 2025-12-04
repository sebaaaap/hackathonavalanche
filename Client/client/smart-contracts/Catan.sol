pragma solidity ^0.8.19;

contract CatanGame {
    enum BuildingType { ROAD, SETTLEMENT, CITY }
    enum ResourceType { WOOD, BRICK, SHEEP, WHEAT, ORE }

    struct Player {
        address wallet;
        uint256 victoryPoints;
        uint256 settlements;
        uint256 cities;
        uint256 roads;
        mapping(ResourceType => uint256) resources;
        bool active;
    }

    struct Building {
        uint256 playerId;
        BuildingType buildingType;
        uint256 xPos;
        uint256 yPos;
        uint256 timestamp;
    }

    struct DiceRoll {
        address player;
        uint256 result;
        uint256 timestamp;
    }

    mapping(address => Player) public players;
    Building[] public buildings;
    DiceRoll[] public diceRolls;

    address[] public activePlayers;
    uint256 public currentPlayerIndex;
    bool public gameActive;

    event PlayerJoined(address indexed player);
    event BuildingPlaced(address indexed player, BuildingType building, uint256 xPos, uint256 yPos);
    event DiceRolled(address indexed player, uint256 result);
    event ResourcesGranted(address indexed player, ResourceType resource, uint256 amount);

    modifier onlyActivePlayers() {
        require(players[msg.sender].active, "Player not active");
        _;
    }

    modifier onlyCurrentPlayer() {
        require(activePlayers[currentPlayerIndex] == msg.sender, "Not current player");
        _;
    }

    // Funciones para conectar con el juego React

    function joinGame() external {
        require(!players[msg.sender].active, "Already in game");
        require(activePlayers.length < 4, "Game full");

        players[msg.sender].active = true;
        activePlayers.push(msg.sender);

        // Inicializar recursos
        for (uint i = 0; i < 5; i++) {
            players[msg.sender].resources[ResourceType(i)] = 0;
        }

        emit PlayerJoined(msg.sender);
    }

    function placeBuilding(
        BuildingType buildingType,
        uint256 xPos,
        uint256 yPos
    ) external onlyActivePlayers onlyCurrentPlayer {
        // Validar que el jugador tiene recursos
        require(validateResources(msg.sender, buildingType), "Insufficient resources");

        // Deducir recursos
        deductResources(msg.sender, buildingType);

        // Registrar edificio
        buildings.push(Building({
            playerId: getPlayerId(msg.sender),
            buildingType: buildingType,
            xPos: xPos,
            yPos: yPos,
            timestamp: block.timestamp
        }));

        // Actualizar contador de edificios
        if (buildingType == BuildingType.SETTLEMENT) {
            players[msg.sender].settlements += 1;
            players[msg.sender].victoryPoints += 1;
        } else if (buildingType == BuildingType.CITY) {
            players[msg.sender].cities += 1;
            players[msg.sender].victoryPoints += 2;
        } else {
            players[msg.sender].roads += 1;
        }

        emit BuildingPlaced(msg.sender, buildingType, xPos, yPos);
    }

    function rollDice() external onlyActivePlayers onlyCurrentPlayer returns (uint256) {
        uint256 roll = (uint256(keccak256(abi.encodePacked(block.timestamp, msg.sender))) % 11) + 2;

        diceRolls.push(DiceRoll({
            player: msg.sender,
            result: roll,
            timestamp: block.timestamp
        }));

        emit DiceRolled(msg.sender, roll);

        return roll;
    }

    function grantResources(address player, ResourceType resource, uint256 amount) external {
        players[player].resources[resource] += amount;
        emit ResourcesGranted(player, resource, amount);
    }

    // Funciones auxiliares

    function validateResources(address player, BuildingType buildingType) internal view returns (bool) {
        if (buildingType == BuildingType.ROAD) {
            return players[player].resources[ResourceType.WOOD] >= 1 &&
                   players[player].resources[ResourceType.BRICK] >= 1;
        } else if (buildingType == BuildingType.SETTLEMENT) {
            return players[player].resources[ResourceType.WOOD] >= 1 &&
                   players[player].resources[ResourceType.BRICK] >= 1 &&
                   players[player].resources[ResourceType.SHEEP] >= 1 &&
                   players[player].resources[ResourceType.WHEAT] >= 1;
        } else { // CITY
            return players[player].resources[ResourceType.WHEAT] >= 2 &&
                   players[player].resources[ResourceType.ORE] >= 3;
        }
    }

    function deductResources(address player, BuildingType buildingType) internal {
        if (buildingType == BuildingType.ROAD) {
            players[player].resources[ResourceType.WOOD] -= 1;
            players[player].resources[ResourceType.BRICK] -= 1;
        } else if (buildingType == BuildingType.SETTLEMENT) {
            players[player].resources[ResourceType.WOOD] -= 1;
            players[player].resources[ResourceType.BRICK] -= 1;
            players[player].resources[ResourceType.SHEEP] -= 1;
            players[player].resources[ResourceType.WHEAT] -= 1;
        } else { // CITY
            players[player].resources[ResourceType.WHEAT] -= 2;
            players[player].resources[ResourceType.ORE] -= 3;
        }
    }

    function getPlayerId(address playerWallet) internal view returns (uint256) {
        for (uint i = 0; i < activePlayers.length; i++) {
            if (activePlayers[i] == playerWallet) {
                return i;
            }
        }
        revert("Player not found");
    }

    // Getters

    function getPlayerResources(address player) external view returns (uint256[5] memory) {
        uint256[5] memory resources;
        for (uint i = 0; i < 5; i++) {
            resources[i] = players[player].resources[ResourceType(i)];
        }
        return resources;
    }

    function getBuildingCount(address player) external view returns (uint256, uint256, uint256) {
        return (players[player].settlements, players[player].cities, players[player].roads);
    }

    function getVictoryPoints(address player) external view returns (uint256) {
        return players[player].victoryPoints;
    }
}
