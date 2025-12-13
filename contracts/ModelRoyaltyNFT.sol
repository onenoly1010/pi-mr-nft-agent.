// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721Royalty.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

/**
 * @title ModelRoyaltyNFT
 * @dev ERC-721 NFT for GGUF models with built-in royalty enforcement
 * 
 * Each MR-NFT represents a model + its creator's right to earn 10-30% on every inference
 * Royalties are automatically enforced on-chain and routed to creator address
 */
contract ModelRoyaltyNFT is ERC721, ERC721Royalty, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;

    Counters.Counter private _tokenIdCounter;
    
    struct ModelMetadata {
        string modelId;
        string ipfsHash;
        uint256 baseRoyaltyBps; // 1000 = 10%, 2000 = 20%, 3000 = 30%
        address creatorAddress;
        uint256 mintTimestamp;
    }

    mapping(uint256 => ModelMetadata) public modelMetadata;

    event ModelMinted(
        uint256 indexed tokenId,
        string modelId,
        address indexed creator,
        uint256 royaltyBps
    );

    event RoyaltyPaid(
        uint256 indexed tokenId,
        address indexed to,
        uint256 amount,
        uint256 catalyst_multiplier
    );

    constructor() ERC721("Pi Model Royalty NFT", "MR-NFT") {}

    /**
     * @dev Mint new MR-NFT for a model
     * @param modelId Unique model identifier
     * @param ipfsHash GGUF file hash on IPFS
     * @param royaltyBps Royalty percentage in basis points (1000-3000)
     * @param creatorAddress Creator wallet address
     * @param uri Token metadata URI
     */
    function mintModelNFT(
        string memory modelId,
        string memory ipfsHash,
        uint256 royaltyBps,
        address creatorAddress,
        string memory uri
    ) public returns (uint256) {
        require(royaltyBps >= 1000 && royaltyBps <= 3000, "Invalid royalty (10-30%)");
        require(creatorAddress != address(0), "Invalid creator address");

        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();

        _safeMint(msg.sender, tokenId);
        _setTokenURI(tokenId, uri);

        // Set royalty info
        _setDefaultRoyalty(creatorAddress, royaltyBps);

        // Store metadata
        modelMetadata[tokenId] = ModelMetadata({
            modelId: modelId,
            ipfsHash: ipfsHash,
            baseRoyaltyBps: royaltyBps,
            creatorAddress: creatorAddress,
            mintTimestamp: block.timestamp
        });

        emit ModelMinted(tokenId, modelId, creatorAddress, royaltyBps);
        return tokenId;
    }

    /**
     * @dev Calculate and enforce royalty for inference
     * @param tokenId MR-NFT token ID
     * @param inferenceValue Inference compute value in PI
     * @param catalystMultiplier Current catalyst pool multiplier (8.0-1.0)
     */
    function executeRoyalty(
        uint256 tokenId,
        uint256 inferenceValue,
        uint256 catalystMultiplier
    ) external payable returns (uint256) {
        require(_exists(tokenId), "Token does not exist");
        
        ModelMetadata memory metadata = modelMetadata[tokenId];
        
        // Calculate base royalty
        uint256 baseRoyalty = (inferenceValue * metadata.baseRoyaltyBps) / 10000;
        
        // Apply catalyst multiplier
        uint256 totalRoyalty = (baseRoyalty * catalystMultiplier) / 100;

        // Route to creator
        (bool success, ) = metadata.creatorAddress.call{value: totalRoyalty}("");
        require(success, "Royalty transfer failed");

        emit RoyaltyPaid(tokenId, metadata.creatorAddress, totalRoyalty, catalystMultiplier);
        return totalRoyalty;
    }

    /**
     * @dev Get metadata for token
     */
    function getModelMetadata(uint256 tokenId) 
        external 
        view 
        returns (ModelMetadata memory) 
    {
        require(_exists(tokenId), "Token does not exist");
        return modelMetadata[tokenId];
    }

    // Required overrides
    function _burn(uint256 tokenId) 
        internal 
        override(ERC721, ERC721Royalty, ERC721URIStorage) 
    {
        super._burn(tokenId);
    }

    function tokenURI(uint256 tokenId)
        public
        view
        override(ERC721, ERC721URIStorage)
        returns (string memory)
    {
        return super.tokenURI(tokenId);
    }

    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721, ERC721Royalty, ERC721URIStorage)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}
