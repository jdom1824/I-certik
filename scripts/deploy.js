const hre = require("hardhat");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

async function main() {
  // Obtén la cuenta del owner (usada por default)
  const [owner] = await hre.ethers.getSigners();

  // Despliega el contrato "CertificadosOnChain"
  const CertificadosOnChain = await hre.ethers.getContractFactory("CertificadosOnChainConexalab", owner);
  const certificados = await CertificadosOnChain.deploy();

  // Espera a que el contrato se despliegue completamente
  if (typeof certificados.waitForDeployment === "function") {
    await certificados.waitForDeployment();
  } else {
    await certificados.deployed();
  }

  // Obtén la dirección del contrato desplegado
  const contractAddress = certificados.target || certificados.address || await certificados.getAddress();
  console.log("CertificadosOnChain deployed to:", contractAddress);

  // Ruta del archivo .env
  const envPath = path.resolve(__dirname, "../.env");

  // Cargar el contenido actual del .env (si existe)
  let envContent = "";
  if (fs.existsSync(envPath)) {
    envContent = fs.readFileSync(envPath, "utf8");
  }

  // Buscar si ya existe una línea con CONTRACT_ADDRESS y reemplazarla
  const newEnvContent = envContent.includes("CONTRACT_ADDRESS=")
    ? envContent.replace(/CONTRACT_ADDRESS=.*/g, `CONTRACT_ADDRESS=${contractAddress}`)
    : envContent + `\nCONTRACT_ADDRESS=${contractAddress}`;

  // Escribir en el archivo .env
  fs.writeFileSync(envPath, newEnvContent.trim(), "utf8");

  console.log(`Contract address saved to .env file.`);

  // Mostrar la nueva dirección guardada
  process.env.CONTRACT_ADDRESS = contractAddress;
  console.log("Updated process.env.CONTRACT_ADDRESS:", process.env.CONTRACT_ADDRESS);
}

// Manejo de errores
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
