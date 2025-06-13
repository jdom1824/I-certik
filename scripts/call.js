// call.js
require("dotenv").config();               // 1) Carga .env antes de usar process.env
const { ethers } = require("ethers");    // 2) Importa ethers

// 3) Asegúrate de que RPC_URL esté definida
if (!process.env.RPC_URL) {
  console.error("❌ ERROR: falta la variable RPC_URL en .env");
  process.exit(1);
}

// 4) Crea el provider con la clase JsonRpcProvider
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);

// 5) Instancia tu contrato
const ABI = [
  "function totalSupply() view returns (uint256)"
];
const contract = new ethers.Contract(
  process.env.CONTRACT_ADDRESS,
  ABI,
  provider
);

async function main() {
  // 6) Llama totalSupply
  const supply = await contract.totalSupply();
  console.log("🔢 totalSupply:", supply.toString());
}

main().catch(err => {
  console.error("❌ Error en script:", err);
  process.exit(1);
});
