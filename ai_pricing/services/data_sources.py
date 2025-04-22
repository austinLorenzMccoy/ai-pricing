"""
Data source adapters for the RWA AI Pricing Engine.
"""
import os
import logging
from datetime import datetime
from typing import Dict, List, Any
import asyncio
import json

import aiohttp
import numpy as np
from textblob import TextBlob

# Initialize logging
logger = logging.getLogger(__name__)

class DataSourceAdapter:
    """Adapter for various external data sources."""
    
    @staticmethod
    async def fetch_auction_data(asset_category: str) -> Dict:
        """Real Alpha Vantage integration for market data."""
        try:
            url = f"https://www.alphavantage.co/query?function=TOP_GAINERS_LOSERS&apikey={os.getenv('ALPHA_VANTAGE_KEY')}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
            return DataSourceAdapter._parse_alpha_vantage(data)
        except Exception as e:
            logger.error(f"Error fetching market data: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _parse_alpha_vantage(data: Dict) -> Dict:
        """Parse Alpha Vantage API response."""
        try:
            if 'top_gainers' in data:
                recent_sales = []
                total_price = 0
                for item in data['top_gainers'][:5]:  # Use top 5 gainers as recent sales
                    price = float(item.get('price', 0))
                    recent_sales.append({
                        "item": item.get('ticker', 'unknown'),
                        "price": price,
                        "date": datetime.now().isoformat()
                    })
                    total_price += price
                
                avg_price = total_price / len(recent_sales) if recent_sales else 0
                return {
                    "recent_sales": recent_sales,
                    "average_price": avg_price,
                    "price_trend": data.get('last_updated', 'Unknown')
                }
            return {
                "recent_sales": [],
                "average_price": 0,
                "price_trend": "Unknown"
            }
        except Exception as e:
            logger.error(f"Error parsing Alpha Vantage data: {e}")
            return {"error": str(e)}

    @staticmethod
    async def fetch_sentiment_analysis(asset_id: str) -> Dict:
        """NewsAPI integration for sentiment analysis."""
        try:
            url = f"https://newsapi.org/v2/everything?q={asset_id}&apiKey={os.getenv('NEWSAPI_KEY')}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    articles = await response.json()
            return DataSourceAdapter._analyze_sentiment(articles.get("articles", []))
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {"error": str(e)}
    
    @staticmethod
    def _analyze_sentiment(articles: List[Dict]) -> Dict:
        """Analyze sentiment from news articles."""
        try:
            if not articles:
                return {
                    "overall_sentiment": 0,
                    "mention_volume": 0,
                    "trending_keywords": [],
                    "source_breakdown": {}
                }
            
            # Extract titles and descriptions for sentiment analysis
            texts = []
            sources = {}
            keywords = {}
            
            for article in articles:
                title = article.get('title', '')
                description = article.get('description', '')
                source = article.get('source', {}).get('name', 'unknown')
                
                if title and description:
                    texts.append(title + " " + description)
                    
                    # Count sources
                    sources[source] = sources.get(source, 0) + 1
                    
                    # Extract potential keywords (simple implementation)
                    words = (title + " " + description).lower().split()
                    for word in words:
                        if len(word) > 4:  # Only consider words longer than 4 chars
                            keywords[word] = keywords.get(word, 0) + 1
            
            # Calculate sentiment
            sentiments = [TextBlob(text).sentiment.polarity for text in texts]
            overall_sentiment = float(np.mean(sentiments)) if sentiments else 0
            
            # Get top keywords
            sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
            top_keywords = [k for k, v in sorted_keywords[:10]]
            
            # Normalize source breakdown
            total_mentions = sum(sources.values())
            source_breakdown = {s: count/total_mentions for s, count in sources.items()}
            
            return {
                "overall_sentiment": overall_sentiment,
                "mention_volume": len(texts),
                "trending_keywords": top_keywords,
                "source_breakdown": source_breakdown
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "overall_sentiment": 0,
                "mention_volume": 0,
                "trending_keywords": [],
                "source_breakdown": {}
            }

    @staticmethod
    async def fetch_economic_indicators() -> Dict:
        """FRED API integration for economic indicators."""
        try:
            # Clean up API key by removing quotes and comments
            api_key = os.getenv('FRED_API_KEY', '')
            if api_key:
                # Remove quotes and comments if present
                api_key = api_key.strip()
                if api_key.startswith('"') and api_key.endswith('"'):
                    api_key = api_key[1:-1]
                # Remove any comment part
                if '#' in api_key:
                    api_key = api_key.split('#')[0].strip()
            
            url = f"https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key={api_key}&file_type=json"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    data = await response.json()
            
            # Process FRED data
            observations = data.get('observations', [])
            if observations:
                # Get latest values
                latest = observations[-1]
                prev_month = observations[-2] if len(observations) > 1 else None
                prev_year = observations[-13] if len(observations) > 12 else None
                
                # Calculate inflation rate (year-over-year)
                inflation_rate = 0
                if prev_year and 'value' in latest and 'value' in prev_year:
                    try:
                        current = float(latest['value'])
                        year_ago = float(prev_year['value'])
                        inflation_rate = ((current - year_ago) / year_ago) * 100
                    except (ValueError, ZeroDivisionError):
                        pass
                
                return {
                    "inflation_rate": round(inflation_rate, 2),
                    "latest_cpi": latest.get('value'),
                    "cpi_date": latest.get('date'),
                    "data_source": "FRED"
                }
            
            return {
                "inflation_rate": 0,
                "latest_cpi": 0,
                "cpi_date": datetime.now().isoformat(),
                "data_source": "FRED"
            }
        except Exception as e:
            logger.error(f"Error fetching economic data: {e}")
            return {"error": str(e)}
    
    @staticmethod
    async def fetch_nft_data(asset_id: str) -> Dict:
        """OpenSea API integration for NFT data."""
        try:
            headers = {"X-API-KEY": os.getenv("OPENSEA_API_KEY")}
            url = f"https://api.opensea.io/api/v1/asset/{asset_id}/"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    data = await response.json()
            
            if 'detail' in data and 'Request was throttled' in data['detail']:
                logger.warning("OpenSea API rate limit reached")
                return {"error": "Rate limit reached"}
                
            return {
                "name": data.get('name', 'Unknown'),
                "description": data.get('description', ''),
                "image_url": data.get('image_url', ''),
                "permalink": data.get('permalink', ''),
                "contract_address": data.get('asset_contract', {}).get('address', ''),
                "token_id": data.get('token_id', ''),
                "last_sale": data.get('last_sale', {}),
                "traits": data.get('traits', []),
                "collection": {
                    "name": data.get('collection', {}).get('name', ''),
                    "description": data.get('collection', {}).get('description', ''),
                    "stats": data.get('collection', {}).get('stats', {})
                }
            }
        except Exception as e:
            logger.error(f"Error fetching NFT data: {e}")
            return {"error": str(e)}
