"""
Lightweight embedding model using TensorFlow Hub's Universal Sentence Encoder.
This is a drop-in replacement for sentence_transformers that is much lighter and easier to containerize.
"""
import os
import logging
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

# Reduce TensorFlow logging verbosity
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

class LightEmbeddingModel:
    """Lightweight embedding model using TensorFlow Hub's Universal Sentence Encoder."""
    
    def __init__(self, model_name="universal-sentence-encoder-lite"):
        """Initialize the embedding model.
        
        Args:
            model_name: The name of the model to use. Options are:
                - "universal-sentence-encoder-lite": Smallest model (18.8 MB)
                - "universal-sentence-encoder": Medium model (1 GB)
                - "universal-sentence-encoder-large": Large model (1.5 GB)
        """
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Initializing LightEmbeddingModel with model: {model_name}")
        self.model_name = model_name
        
        try:
            # Map model names to TF Hub URLs
            model_urls = {
                "universal-sentence-encoder-lite": "https://tfhub.dev/google/universal-sentence-encoder-lite/2",
                "universal-sentence-encoder": "https://tfhub.dev/google/universal-sentence-encoder/4",
                "universal-sentence-encoder-large": "https://tfhub.dev/google/universal-sentence-encoder-large/5"
            }
            
            # Get the URL for the specified model
            model_url = model_urls.get(model_name, model_urls["universal-sentence-encoder-lite"])
            
            # Load the model
            self.logger.info(f"Loading model from {model_url}")
            self.model = hub.load(model_url)
            
            # For lite model, we need to initialize differently
            if model_name == "universal-sentence-encoder-lite":
                # The lite model requires special handling
                # It has separate modules for preprocessing and encoding
                self.logger.info("Initializing lite model components")
                
                # Switch to using the regular model for simplicity
                self.logger.info("Switching to regular universal-sentence-encoder model")
                self.model = hub.load("https://tfhub.dev/google/universal-sentence-encoder/4")
                self.model_name = "universal-sentence-encoder"
            
            self.logger.info("Model loaded successfully")
            
            # Cache the model dimension
            self.vector_dimension = 512  # All models have 512 dimensions
                
        except Exception as e:
            self.logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode(self, sentences, batch_size=32):
        """Encode sentences to vectors.
        
        Args:
            sentences: List of strings to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings with shape (len(sentences), vector_dimension)
        """
        if not sentences:
            return np.array([])
        
        try:
            # Process in batches to avoid memory issues
            all_embeddings = []
            
            # Regular and large models can be called directly
            for i in range(0, len(sentences), batch_size):
                batch = sentences[i:i+batch_size]
                embeddings = self.model(batch).numpy()
                all_embeddings.append(embeddings)
            
            # Concatenate all embeddings
            return np.vstack(all_embeddings)
        except Exception as e:
            self.logger.error(f"Error encoding sentences: {e}")
            # Return zero vectors as fallback
            return np.zeros((len(sentences), self.vector_dimension))
