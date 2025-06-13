// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Strings.sol";
import "@openzeppelin/contracts/utils/Base64.sol";

contract CertificadosOnChainConexalab is ERC721, Ownable {
    using Strings for uint256;

    struct Certificado {
        string nombre;
        string descripcion;
        string fecha;
    }

    mapping(uint256 => Certificado) private _detalles;
    uint256  private _totalMinted; 

    constructor() ERC721("CertificadosOnChainConexalab", "CERT") Ownable(_msgSender()) {}

    function mintCertificado(
        string memory nombre,
        uint256 cedula,
        string memory descripcion,
        string memory fecha
    ) public onlyOwner returns (uint256) {
        // Ajustado para OZ v5
        require(_ownerOf(cedula) == address(0), "Certificado ya existe para esta cedula");
        _totalMinted += 1; 
        _safeMint(msg.sender, cedula);
        _detalles[cedula] = Certificado(nombre, descripcion, fecha);
        return cedula;
    }

    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(_ownerOf(tokenId) != address(0), "El token no existe");

        Certificado memory cert = _detalles[tokenId];
        bytes memory data = abi.encodePacked(
            "{",
                '"name":"', cert.nombre, '",',
                '"cedula":"', tokenId.toString(), '",',
                '"description":"', cert.descripcion, '",',
                '"fecha":"', cert.fecha, '"',
            "}"
        );
        return string(abi.encodePacked("data:application/json;base64,", Base64.encode(data)));
    }
    function totalSupply() external view returns (uint256) {
        return _totalMinted;
    }
}
