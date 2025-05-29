const hre = require("hardhat");
require('dotenv').config();

async function main() {
    const contractAddress = process.env.CONTRACT_ADDRESS;
    // Permite pasar la cédula/tokenId como argumento
    const tokenId = process.argv[2] ? parseInt(process.argv[2]) : 0;

    if (!contractAddress) {
        console.error("Falta la variable CONTRACT_ADDRESS en tu .env");
        process.exit(1);
    }

    // Carga el contrato
    const CertificadosOnChain = await hre.ethers.getContractFactory("CertificadosOnChainConexalab");
    const certificados = CertificadosOnChain.attach(contractAddress);

    // 1. Obtiene el owner del token
    let owner;
    try {
        owner = await certificados.ownerOf(tokenId);
        console.log("Owner:", owner);
    } catch (e) {
        console.error(`El tokenId ${tokenId} no existe.`);
        process.exit(1);
    }

    // 2. Obtiene el tokenURI y decodifica la data base64
    const tokenURI = await certificados.tokenURI(tokenId);
    console.log("tokenURI:", tokenURI);

    // Extrae y decodifica la parte base64 (el JSON)
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
