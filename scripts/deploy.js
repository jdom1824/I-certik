const { ethers } = require("ethers");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

// Cargamos el ABI y Bytecode del contrato compilado
const contractJson = require("../artifacts/contracts/CertificadosOnChainConexalab.sol/CertificadosOnChainConexalab.json");

async function main() {
  // Crear un provider con la RPC externa
  const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);

  // Crear una wallet desde la clave privada
  const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

  // Crear instancia del contrato factory
  const factory = new ethers.ContractFactory(contractJson.abi, contractJson.bytecode, wallet);

  console.log("Deploying contract...");
  const contract = await factory.deploy();

  await contract.waitForDeployment(); // Esto es ethers v6+
  const contractAddress = await contract.getAddress();

  console.log("Contract deployed at:", contractAddress);

  // Guardar en el archivo .env
  const envPath = path.resolve(__dirname, "../.env");

  let envContent = "";
  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, "utf8");
  }

  const newEnvContent = envContent.includes("CONTRACT_ADDRESS=")
    ? envContent.replace(/CONTRACT_ADDRESS=.*/g, `CONTRACT_ADDRESS=${contractAddress}`)
    : envContent + `\nCONTRACT_ADDRESS=${contractAddress}`;

  fs.writeFileSync(envPath, newEnvContent.trim(), "utf8");

  console.log("Contract address saved to .env.");
}

main().catch((error) => {
  console.error("Error deploying contract:", error);
  process.exit(1);
});
