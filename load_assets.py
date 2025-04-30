#!/usr/bin/env python
"""
Script to load sample assets into the asset database for the AI Pricing Engine.
This script is used to populate the asset database for Docker deployment.
"""
import json
import os
import logging
import sqlite3
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_asset_db():
    """Create the asset database if it doesn't exist."""
    db_path = "data/assets.db"
    os.makedirs("data", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create assets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assets (
        id TEXT PRIMARY KEY,
        category TEXT,
        collection TEXT,
        initial_price REAL,
        current_price REAL,
        metadata TEXT,
        contract_address TEXT,
        token_id TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    conn.commit()
    return conn, cursor

def load_sample_assets():
    """Load sample assets from the JSON file into the database."""
    try:
        # Create the database and get connection
        conn, cursor = create_asset_db()
        
        # Load sample assets from JSON
        with open('sample_assets.json', 'r') as f:
            assets = json.load(f)
        
        # Insert assets into the database
        for asset_id, asset_data in assets.items():
            # Convert metadata to JSON string
            metadata = json.dumps(asset_data.get('metadata', {}))
            
            # Get current timestamp
            now = datetime.now().isoformat()
            
            # Insert or update the asset
            cursor.execute('''
            INSERT OR REPLACE INTO assets 
            (id, category, collection, initial_price, current_price, metadata, 
             contract_address, token_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                asset_id,
                asset_data.get('category', ''),
                asset_data.get('collection', ''),
                asset_data.get('initial_price', 0),
                asset_data.get('current_price', 0),
                metadata,
                asset_data.get('contract_address', ''),
                asset_data.get('token_id', ''),
                asset_data.get('created_at', now),
                now
            ))
        
        # Commit changes and close connection
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully loaded {len(assets)} assets into the database")
        return True
    
    except Exception as e:
        logger.error(f"Error loading sample assets: {e}")
        return False

def verify_assets():
    """Verify that assets were loaded correctly."""
    try:
        # Connect to the database
        conn = sqlite3.connect("data/assets.db")
        cursor = conn.cursor()
        
        # Count assets
        cursor.execute("SELECT COUNT(*) FROM assets")
        count = cursor.fetchone()[0]
        
        # Get a sample asset
        cursor.execute("SELECT id, category, current_price FROM assets LIMIT 1")
        sample = cursor.fetchone()
        
        conn.close()
        
        logger.info(f"Verified {count} assets in database")
        if sample:
            logger.info(f"Sample asset: {sample}")
        
        return count > 0
    
    except Exception as e:
        logger.error(f"Error verifying assets: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting asset database initialization")
    success = load_sample_assets()
    
    if success:
        verify_assets()
        logger.info("Asset database initialization complete")
    else:
        logger.error("Failed to initialize asset database")
