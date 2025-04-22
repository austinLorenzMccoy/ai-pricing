"""
Blockchain integration services for the RWA AI Pricing Engine.
"""
import os
import logging
from typing import Dict, Any, Optional

from web3 import Web3

# Initialize logging
logger = logging.getLogger(__name__)

# ERC721 ABI for NFT contract interactions
ERC721_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "ownerOf",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "uint256", "name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"internalType": "string", "name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class BlockchainHelper:
    """Helper class for blockchain interactions."""
    
    def __init__(self):
        """Initialize blockchain connection using Infura."""
        self.infura_endpoint = os.getenv("INFURA_ENDPOINT")
        if not self.infura_endpoint:
            logger.warning("INFURA_ENDPOINT not set, blockchain features will be limited")
            self.w3 = None
        else:
            try:
                self.w3 = Web3(Web3.HTTPProvider(self.infura_endpoint))
                logger.info(f"Connected to Ethereum: {self.w3.is_connected()}")
            except Exception as e:
                logger.error(f"Failed to connect to Ethereum: {e}")
                self.w3 = None
    
    def get_asset_ownership(self, contract_address: str, token_id: int = 1) -> Optional[str]:
        """
        Get the owner of an NFT asset.
        
        Args:
            contract_address: The NFT contract address
            token_id: The token ID to check ownership for
            
        Returns:
            The owner address or None if error
        """
        if not self.w3 or not self.w3.is_connected():
            logger.error("Not connected to Ethereum network")
            return None
            
        try:
            if not Web3.is_address(contract_address):
                logger.error(f"Invalid contract address: {contract_address}")
                return None
                
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=ERC721_ABI
            )
            
            owner = contract.functions.ownerOf(token_id).call()
            return owner
        except Exception as e:
            logger.error(f"Error getting asset ownership: {e}")
            return None
    
    def get_contract_info(self, contract_address: str) -> Dict[str, Any]:
        """
        Get basic information about an NFT contract.
        
        Args:
            contract_address: The NFT contract address
            
        Returns:
            Dictionary with contract information
        """
        if not self.w3 or not self.w3.is_connected():
            logger.error("Not connected to Ethereum network")
            return {"error": "Not connected to Ethereum network"}
            
        try:
            if not Web3.is_address(contract_address):
                logger.error(f"Invalid contract address: {contract_address}")
                return {"error": "Invalid contract address"}
            
            # Convert to checksum address
            checksum_address = Web3.to_checksum_address(contract_address)
                
            contract = self.w3.eth.contract(
                address=checksum_address,
                abi=ERC721_ABI
            )
            
            try:
                name = contract.functions.name().call()
            except Exception:
                name = "Unknown"
                
            try:
                symbol = contract.functions.symbol().call()
            except Exception:
                symbol = "Unknown"
            
            return {
                "name": name,
                "symbol": symbol,
                "address": contract_address,
                "chain_id": self.w3.eth.chain_id
            }
        except Exception as e:
            logger.error(f"Error getting contract info: {e}")
            return {"error": str(e)}
    
    def get_token_uri(self, contract_address: str, token_id: int = 1) -> Optional[str]:
        """
        Get the token URI for an NFT.
        
        Args:
            contract_address: The NFT contract address
            token_id: The token ID
            
        Returns:
            The token URI or None if error
        """
        if not self.w3 or not self.w3.is_connected():
            logger.error("Not connected to Ethereum network")
            return None
            
        try:
            if not Web3.is_address(contract_address):
                logger.error(f"Invalid contract address: {contract_address}")
                return None
                
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=ERC721_ABI
            )
            
            uri = contract.functions.tokenURI(token_id).call()
            return uri
        except Exception as e:
            logger.error(f"Error getting token URI: {e}")
            return None
