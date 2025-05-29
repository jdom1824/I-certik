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

    // Mapping de cedula/tokenId a struct Certificado
    mapping(uint256 => Certificado) private _detalles;

    constructor() ERC721("CertificadosOnChainConexalab", "CERT") Ownable(msg.sender) {}
    
    function mintCertificado(
        string memory nombre,
        uint256 cedula,
        string memory descripcion,
        string memory fecha
    ) public onlyOwner returns (uint256) {
        require(!_tokenExists(cedula), "Certificado ya existe para esta cedula");
        _safeMint(msg.sender, cedula);
        _detalles[cedula] = Certificado({
            nombre: nombre,
            descripcion: descripcion,
            fecha: fecha
        });
        return cedula;
    }
    function _tokenExists(uint256 tokenId) internal view returns (bool) {
        try this.ownerOf(tokenId) returns (address owner) {
            return owner != address(0);
        } catch {
            return false;
        }
    }
    function tokenURI(uint256 tokenId) public view override returns (string memory) {
        require(ownerOf(tokenId) != address(0), "El token no existe");

        Certificado memory cert = _detalles[tokenId];
        bytes memory data = abi.encodePacked(
            '{',
                '"name": "', cert.nombre, '", ',
                '"cedula": "', tokenId.toString(), '", ',
                '"description": "', cert.descripcion, '", ',
                '"fecha": "', cert.fecha, '"',
            '}'
        );
        string memory jsonBase64 = Base64.encode(data);
        return string(abi.encodePacked("data:application/json;base64,", jsonBase64));
    }
}
