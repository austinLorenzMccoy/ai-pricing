"""
Core pricing engine for RWA AI Pricing.
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

import aiohttp
import asyncio
import groq
import faiss
import numpy as np

from ai_pricing.core.embedding_model import LightEmbeddingModel

from ai_pricing.models.schemas import PriceSignal, DataSourceUpdate
from ai_pricing.services.blockchain import BlockchainHelper

# Initialize logging
logger = logging.getLogger(__name__)

class AIPricingEngine:
    """AI-powered pricing engine for tokenized real-world assets."""
    
    def __init__(self):
        """Initialize the pricing engine with Groq API, blockchain helper, and embeddings."""
        # Initialize blockchain helper
        self.blockchain = BlockchainHelper()
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize Groq API client
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        # Initialize Groq client
        try:
            # Initialize with just the API key, no additional parameters
            self.client = groq.Client(api_key=self.api_key)
            self.model = "llama3-70b-8192"  # Use llama3-70b-8192 model which is currently supported
            self.temperature = 0.1
            self.logger.info("Successfully initialized Groq client")
        except Exception as e:
            self.logger.error(f"Error initializing Groq client: {e}")
            # Create a mock client for testing
            self.logger.warning("Using mock Groq client for testing")
            self.client = None
        
        # Initialize embeddings model
        try:
            self.embedding_model = LightEmbeddingModel("universal-sentence-encoder-lite")
            self.vector_dimension = self.embedding_model.vector_dimension  # Update dimension to match the model
        except Exception as e:
            self.logger.error(f"Error initializing embedding model: {e}")
            self.embedding_model = None
        
        self.last_model_update = datetime.now()
        
        # Parse REFRESH_INTERVAL, handling possible comments in the value
        refresh_interval_str = os.getenv("REFRESH_INTERVAL", "300")
        try:
            # Extract just the number if there are comments
            if '#' in refresh_interval_str:
                refresh_interval_str = refresh_interval_str.split('#')[0].strip()
            self.refresh_interval = int(refresh_interval_str)
        except (ValueError, TypeError):
            self.logger.warning(f"Invalid REFRESH_INTERVAL value: {refresh_interval_str}, using default 300")
            self.refresh_interval = 300
        
        self.pricing_template = """
        You are an AI pricing specialist for tokenized real-world assets (RWAs).
        
        ASSET INFORMATION:
        {asset_info}
        
        BLOCKCHAIN DATA:
        {blockchain_data}
        
        RECENT MARKET DATA:
        {market_data}
        
        SENTIMENT ANALYSIS:
        {sentiment_data}
        
        ECONOMIC INDICATORS:
        {economic_data}
        
        Based on all the information above, determine a fair market price for this asset.
        Consider trends, comparable assets, sentiment, economic conditions, and blockchain data.
        
        Provide your response as a JSON object with the following fields:
        - price: The recommended price in USD (numeric value only)
        - confidence_score: Your confidence in this price (0.0-1.0)
        - factors: A dictionary of factors and their influence weights (sum to 1.0)
        - explanation: Brief explanation of your pricing rationale
        - trend: Expected short-term price direction ("up", "down", or "stable")
        
        JSON RESPONSE:
        """
        
        # Initialize FAISS vector store
        self.index = None
        self.documents = []
        # Vector dimension is set when initializing the embedding model
        self.init_vector_store()
    
    def init_vector_store(self):
        """Initialize the vector store for asset knowledge."""
        try:
            if os.path.exists("faiss_index"):
                # Load the index
                self.index = faiss.read_index("faiss_index/index.faiss")
                # Load the documents
                with open("faiss_index/documents.json", "r") as f:
                    self.documents = json.load(f)
                self.logger.info("Loaded existing vector store from faiss_index")
            else:
                self.logger.info("No existing vector store found, initializing empty store")
                # Initialize an empty index
                self.index = faiss.IndexFlatL2(self.vector_dimension)
                self.documents = []
        except Exception as e:
            self.logger.error(f"Error initializing vector store: {e}")
            # Initialize an empty index as fallback
            self.index = faiss.IndexFlatL2(self.vector_dimension)
            self.documents = []
    
    async def get_asset_price(self, asset_id: str, asset_metadata: Dict = None) -> PriceSignal:
        """Generate pricing signal for an asset using multiple data sources including blockchain."""
        try:
            if not asset_metadata:
                asset_metadata = {"id": asset_id, "category": "art", "initial_price": 10000}
                
            category = asset_metadata.get("category", "art")
            
            # Import here to avoid circular imports
            from ai_pricing.services.data_sources import DataSourceAdapter
            
            # Fetch data from all sources in parallel
            auction_task = asyncio.create_task(DataSourceAdapter.fetch_auction_data(category))
            sentiment_task = asyncio.create_task(DataSourceAdapter.fetch_sentiment_analysis(asset_id))
            economic_task = asyncio.create_task(DataSourceAdapter.fetch_economic_indicators())
            nft_task = asyncio.create_task(DataSourceAdapter.fetch_nft_data(asset_id))
            
            auction_data = await auction_task
            sentiment_data = await sentiment_task
            economic_data = await economic_task
            nft_data = await nft_task
            
            # Get blockchain data if contract address is available
            blockchain_data = {"available": False}
            if "contract_address" in nft_data and nft_data["contract_address"]:
                contract_address = nft_data["contract_address"]
                token_id = int(nft_data.get("token_id", "1"))
                
                # Get ownership information
                owner = self.blockchain.get_asset_ownership(contract_address, token_id)
                contract_info = self.blockchain.get_contract_info(contract_address)
                token_uri = self.blockchain.get_token_uri(contract_address, token_id)
                
                blockchain_data = {
                    "available": True,
                    "owner": owner,
                    "contract_info": contract_info,
                    "token_uri": token_uri
                }
            
            # Format the prompt with all data sources
            prompt_content = self.pricing_template.format(
                asset_info=json.dumps(asset_metadata, indent=2),
                blockchain_data=json.dumps(blockchain_data, indent=2),
                market_data=json.dumps(auction_data, indent=2),
                sentiment_data=json.dumps(sentiment_data, indent=2),
                economic_data=json.dumps(economic_data, indent=2)
            )
            
            # Call the Groq API directly
            try:
                # Use the Groq client if available
                if self.client:
                    chat_completion = await self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "You are an AI pricing specialist for tokenized real-world assets."},
                            {"role": "user", "content": prompt_content}
                        ],
                        temperature=self.temperature,
                        max_tokens=1000
                    )
                    result_text = chat_completion.choices[0].message.content
                else:
                    # Fallback to direct API call if client initialization failed
                    headers = {
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    payload = {
                        "model": "llama3-70b-8192",
                        "messages": [
                            {"role": "system", "content": "You are an AI pricing specialist for tokenized real-world assets."},
                            {"role": "user", "content": prompt_content}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 1000
                    }
                    
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                            "https://api.groq.com/openai/v1/chat/completions",
                            headers=headers,
                            json=payload
                        ) as response:
                            if response.status != 200:
                                error_text = await response.text()
                                self.logger.error(f"API Error: {response.status} {response.reason}")
                                self.logger.error(f"Response content: {error_text}")
                                raise Exception(f"API Error: {response.status} {response.reason}")
                            
                            result_json = await response.json()
                            result_text = result_json["choices"][0]["message"]["content"]
            except Exception as e:
                self.logger.error(f"Error calling Groq API: {e}")
                raise
            
            try:
                # Extract JSON from the response if it's wrapped in markdown code blocks
                if "```" in result_text:
                    json_text = result_text.split("```")[1]
                    if json_text.startswith("json"):
                        json_text = json_text[4:].strip()
                    parsed_result = json.loads(json_text.strip())
                else:
                    parsed_result = json.loads(result_text.strip())
            except json.JSONDecodeError:
                self.logger.warning(f"Invalid JSON from LLM: {result_text}")
                parsed_result = {
                    "price": asset_metadata.get("initial_price", 10000),
                    "confidence_score": 0.5,
                    "factors": {"fallback": 1.0},
                    "explanation": "Error parsing LLM response",
                    "trend": "stable"
                }
            
            signal = PriceSignal(
                asset_id=asset_id,
                price=float(parsed_result["price"]),
                confidence_score=float(parsed_result["confidence_score"]),
                timestamp=datetime.now().isoformat(),
                factors=parsed_result["factors"]
            )
            
            self.log_pricing_decision(asset_id, signal, parsed_result)
            return signal
                
        except Exception as e:
            self.logger.error(f"Error generating price signal: {e}")
            return PriceSignal(
                asset_id=asset_id,
                price=asset_metadata.get("initial_price", 10000) if asset_metadata else 10000,
                confidence_score=0.5,
                timestamp=datetime.now().isoformat(),
                factors={"error": 1.0}
            )
    
    def log_pricing_decision(self, asset_id: str, signal: PriceSignal, full_result: Dict):
        """Log pricing decisions for audit and improvement."""
        try:
            self.logger.info(f"Price signal for {asset_id}: {full_result}")
        except Exception as e:
            self.logger.error(f"Error logging pricing decision: {e}")

    async def update_knowledge_base(self, data: Dict) -> Dict:
        """Update the knowledge base with new data."""
        try:
            source_name = data.get("source", "unknown")
            timestamp = datetime.now().isoformat()
            
            # Convert data to text for embedding
            if isinstance(data.get("content"), dict):
                data_text = json.dumps(data["content"])
            elif isinstance(data.get("content"), str):
                data_text = data["content"]
            else:
                data_text = str(data)
            
            # Create document metadata
            document = {
                "text": data_text,
                "metadata": {
                    "source": source_name,
                    "timestamp": timestamp
                }
            }
            
            # Generate embedding
            embedding = self.embedding_model.encode([data_text])[0]
            embedding = embedding.reshape(1, -1)  # Reshape for FAISS
            
            # Create or update vector store
            if not hasattr(self, 'index') or self.index is None:
                # Create a new index
                self.index = faiss.IndexFlatL2(self.vector_dimension)
                self.documents = [document]
                self.index.add(embedding)
                
                # Save the index and documents
                os.makedirs("faiss_index", exist_ok=True)
                faiss.write_index(self.index, "faiss_index/index.faiss")
                with open("faiss_index/documents.json", "w") as f:
                    json.dump(self.documents, f)
                    
                self.logger.info("Created new vector store")
            else:
                # Update existing index
                self.documents.append(document)
                self.index.add(embedding)
                
                # Save the updated index and documents
                faiss.write_index(self.index, "faiss_index/index.faiss")
                with open("faiss_index/documents.json", "w") as f:
                    json.dump(self.documents, f)
                    
                self.logger.info(f"Updated vector store with new {source_name} data")
            
            return {
                "status": "success",
                "message": f"Updated knowledge base with {source_name} data"
            }
            
        except Exception as e:
            self.logger.error(f"Error updating knowledge base: {e}")
            return {"error": str(e)}

# Import for type hints
import asyncio
