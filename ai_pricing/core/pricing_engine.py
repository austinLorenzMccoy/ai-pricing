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
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from ai_pricing.models.schemas import PriceSignal, DataSourceUpdate
from ai_pricing.services.blockchain import BlockchainHelper

# Initialize logging
logger = logging.getLogger(__name__)

class AIPricingEngine:
    """AI-powered pricing engine for tokenized real-world assets."""
    
    def __init__(self):
        """Initialize the pricing engine with LLM, blockchain helper, and embeddings."""
        # Initialize blockchain helper
        self.blockchain = BlockchainHelper()
        
        # Initialize LLM
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set")
        
        # Initialize Groq LLM
        try:
            # Use llama3-70b-8192 model which is currently supported
            self.llm = ChatGroq(
                model_name="llama3-70b-8192",
                groq_api_key=self.api_key,
                temperature=0.1
            )
        except Exception as e:
            logger.error(f"Error initializing ChatGroq: {e}")
            # Fallback to direct API calls if needed
            self.llm = None
        
        # Initialize embeddings and memory
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.last_model_update = datetime.now()
        
        # Parse REFRESH_INTERVAL, handling possible comments in the value
        refresh_interval_str = os.getenv("REFRESH_INTERVAL", "300")
        try:
            # Extract just the number if there are comments
            if '#' in refresh_interval_str:
                refresh_interval_str = refresh_interval_str.split('#')[0].strip()
            self.refresh_interval = int(refresh_interval_str)
        except (ValueError, TypeError):
            logger.warning(f"Invalid REFRESH_INTERVAL value: {refresh_interval_str}, using default 300")
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
        
        self.pricing_prompt = PromptTemplate(
            input_variables=["asset_info", "blockchain_data", "market_data", "sentiment_data", "economic_data"],
            template=self.pricing_template
        )
        
        # Initialize vector store
        self.vector_store = None
        self.init_vector_store()
    
    def init_vector_store(self):
        """Initialize the vector store for asset knowledge."""
        try:
            if os.path.exists("faiss_index"):
                self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
                # Set allow_dangerous_deserialization to True since we trust our own files
                self.vector_store = FAISS.load_local(
                    "faiss_index", 
                    self.embeddings, 
                    allow_dangerous_deserialization=True
                )
                logger.info("Loaded existing vector store")
            else:
                logger.info("No existing vector store found, will create on first data update")
        except Exception as e:
            logger.error(f"Error initializing vector store: {e}")
    
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
            
            # Prepare messages for the LLM
            system_message = SystemMessage(content="You are an AI pricing specialist for tokenized real-world assets.")
            
            # Format the prompt with all data sources
            prompt_content = self.pricing_template.format(
                asset_info=json.dumps(asset_metadata, indent=2),
                blockchain_data=json.dumps(blockchain_data, indent=2),
                market_data=json.dumps(auction_data, indent=2),
                sentiment_data=json.dumps(sentiment_data, indent=2),
                economic_data=json.dumps(economic_data, indent=2)
            )
            
            user_message = HumanMessage(content=prompt_content)
            
            # Call the Groq LLM using langchain or direct API if fallback needed
            if self.llm:
                # Use langchain interface
                result = await self.llm.ainvoke([system_message, user_message])
                result_text = result.content
            else:
                # Direct API call as fallback
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": "llama3-70b-8192",  # Use supported model
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
                            logger.error(f"API Error: {response.status} {response.reason}")
                            logger.error(f"Response content: {error_text}")
                            raise Exception(f"API Error: {response.status} {response.reason}")
                        
                        result_json = await response.json()
                        result_text = result_json["choices"][0]["message"]["content"]
            
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
                logger.warning(f"Invalid JSON from LLM: {result_text}")
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
            logger.error(f"Error generating price signal: {e}")
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
            logger.info(f"Price signal for {asset_id}: {full_result}")
        except Exception as e:
            logger.error(f"Error logging pricing decision: {e}")
    
    async def update_knowledge_base(self, data: Dict) -> Dict:
        """Update the knowledge base with new data."""
        try:
            source_name = data.get("source_name")
            source_data = data.get("data")
            timestamp = data.get("timestamp")
            
            if not source_name or not source_data:
                return {"error": "Invalid data source update"}
            
            # Convert data to text for embedding
            data_text = f"Source: {source_name}\nTimestamp: {timestamp}\nData: {json.dumps(source_data)}"
            
            # Create or update vector store
            if not self.vector_store:
                texts = [data_text]
                metadatas = [{"source": source_name, "timestamp": timestamp}]
                self.vector_store = FAISS.from_texts(texts, self.embeddings, metadatas=metadatas)
                self.vector_store.save_local("faiss_index")
                logger.info("Created new vector store")
            else:
                self.vector_store.add_texts([data_text], [{"source": source_name, "timestamp": timestamp}])
                self.vector_store.save_local("faiss_index")
                logger.info(f"Updated vector store with new {source_name} data")
            
            return {
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating knowledge base: {e}")
            return {"error": str(e)}

# Import for type hints
import asyncio
