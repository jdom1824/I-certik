// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Base64.sol";

contract CertificadosOnChainConexalab is ERC721, Ownable {
    using Strings for uint256;
    using Counters for Counters.Counter;

    // Contador de tokens mintados
    Counters.Counter private _tokenSupply;

    struct Certificado {
        string nombre;
        string descripcion;
        string fecha;
    }

    // Mapping de cedula/tokenId a struct Certificado
    mapping(uint256 => Certificado) private _detalles;

    /// @dev Constructor: Ownable asigna owner = msg.sender automáticamente
    constructor() ERC721("CertificadosOnChainConexalab", "CERT") {}

    /// @notice Mint un nuevo certificado con tokenId = cedula
    function mintCertificado(
        string memory nombre,
        uint256 cedula,
        string memory descripcion,
        string memory fecha
    ) public onlyOwner returns (uint256) {
        require(!_exists(cedula), "Certificado ya existe para esta cedula");
        _safeMint(msg.sender, cedula);
        _detalles[cedula] = Certificado(nombre, descripcion, fecha);
        _tokenSupply.increment();
        return cedula;
    }

    /// @notice Número total de certificados mintados
    function totalSupply() public view returns (uint256) {
        return _tokenSupply.current();
    }

    /// @notice Metadata on-chain en Base64 JSON
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_exists(tokenId), "El token no existe");

        Certificado memory cert = _detalles[tokenId];
        bytes memory data = abi.encodePacked(
            "{",
                '"name":"', cert.nombre, '",',
                '"description":"', cert.descripcion, '",',
                '"fecha":"', cert.fecha, '",',
                '"cedula":"', tokenId.toString(), '"',
            "}"
        );
        string memory jsonBase64 = Base64.encode(data);
        return string(abi.encodePacked("data:application/json;base64,", jsonBase64));
    }
}
