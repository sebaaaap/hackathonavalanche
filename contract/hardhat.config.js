require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
    solidity: "0.8.20",
    networks: {
        // La red pública que usábamos antes
        fuji: {
            url: "https://api.avax-test.network/ext/bc/C/rpc",
            chainId: 43113,
            accounts: [process.env.PRIVATE_KEY_MODELO_A]
        },
        mi_l1: {
            url: "https://api.avax-test.network/ext/bc/C/rpc", // ¡PON TU RPC AQUÍ!
            chainId: 43113, // ¡PON TU CHAIN ID AQUÍ! (Sin comillas si es número)

            // OJO: En tu L1, la cuenta que tiene dinero NO es la del faucet público.
            // Es la cuenta que definiste en el "Genesis" o la cuenta por defecto de pruebas (EWOQ).
            accounts: [process.env.PRIVATE_KEY_ADMIN_L1]
        }
    }
};