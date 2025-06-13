// totalSupply.js

require("dotenv").config();
const { ethers } = require("ethers");

// ABI mínimo con solo totalSupply()
const ABI = [
  "function totalSupply() view returns (uint256)"
];

// Instancia del provider y del contrato
const provider = new ethers.providers.JsonRpcProvider(process.env.RPC_URL);
const contract = new ethers.Contract(
  process.env.CONTRACT_ADDRESS,
  ABI,
  provider
);

/**
 * Devuelve el número total de tokens mintados.
 * @returns {Promise<string>}
 */
async function fetchTotalSupply() {
  try {
    const supplyBN = await contract.totalSupply();
    const supply = supplyBN.toString();
    console.log("🔢 totalSupply:", supply);
    return supply;
  } catch (err) {
    console.error("❌ Error al obtener totalSupply:", err);
    throw err;
  }
}

module.exports = { fetchTotalSupply };
