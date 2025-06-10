const { ethers } = require("ethers");
require("dotenv").config();

async function main() {
    const contractAddress = process.env.CONTRACT_ADDRESS;
    const rpcUrl = process.env.RPC_URL;

    // Permite pasar la cédula/tokenId como argumento
    const tokenId = process.argv[2] ? parseInt(process.argv[2]) : 0;

    if (!contractAddress) {
        console.error("Falta la variable CONTRACT_ADDRESS en tu .env");
        process.exit(1);
    }

    if (!rpcUrl) {
        console.error("Falta la variable RPC_URL en tu .env");
        process.exit(1);
    }

    // Cargar el ABI compilado del contrato
    const contractJson = require("../artifacts/contracts/CertificadosOnChainConexalab.sol/CertificadosOnChainConexalab.json");

    // Conectar al proveedor de la testnet (ej: Sepolia)
    const provider = new ethers.JsonRpcProvider(rpcUrl);

    // Instancia del contrato
    const certificados = new ethers.Contract(contractAddress, contractJson.abi, provider);

    // 1. Obtener el owner del token
    let owner;
    try {
        owner = await certificados.ownerOf(tokenId);
        console.log("Owner:", owner);
    } catch (e) {
        console.error(`El tokenId ${tokenId} no existe.`);
        process.exit(1);
    }

    // 2. Obtener el tokenURI y decodificar base64
    const tokenURI = await certificados.tokenURI(tokenId);
    console.log("tokenURI:", tokenURI);

    const base64Data = tokenURI.replace("data:application/json;base64,", "");
    const json = Buffer.from(base64Data, "base64").toString("utf-8");
    const data = JSON.parse(json);

    console.log("\nInformación del Certificado NFT:");
    console.log("Nombre:", data.name);
    console.log("Cédula:", data.cedula);
    console.log("Descripción:", data.description);
    console.log("Fecha:", data.fecha);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
