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
        
        # Force using the lite model for deployment to reduce memory usage
        if os.getenv("ENVIRONMENT") == "production":
            self.logger.info("Production environment detected, forcing use of lite model")
            model_name = "universal-sentence-encoder-lite"
            
        # Set TensorFlow to grow GPU memory usage
        gpus = tf.config.experimental.list_physical_devices('GPU')
        if gpus:
            try:
                for gpu in gpus:
                    tf.config.experimental.set_memory_growth(gpu, True)
            except RuntimeError as e:
                self.logger.warning(f"Error setting GPU memory growth: {e}")
        
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
                # The lite model requires special handling but uses much less memory
                self.logger.info("Initializing lite model components")
                
                # Actually use the lite model to save memory
                self.logger.info("Loading universal-sentence-encoder-lite model")
                self.model = hub.load("https://tfhub.dev/google/universal-sentence-encoder-lite/2")
                self.model_name = "universal-sentence-encoder-lite"
            
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
            # Handle lite model differently
            if self.model_name == "universal-sentence-encoder-lite":
                # For lite model, we need to use a different approach
                # The lite model is more memory efficient but requires more steps
                return self._encode_with_lite_model(sentences, batch_size)
            
            # Process in batches to avoid memory issues for standard models
            all_embeddings = []
            
            # Regular and large models can be called directly
            for i in range(0, len(sentences), batch_size):
                batch = sentences[i:i+batch_size]
                embeddings = self.model(batch).numpy()
                all_embeddings.append(embeddings)
            
            # Concatenate all embeddings
            return np.array(all_embeddings)
        except Exception as e:
            self.logger.error(f"Error encoding sentences: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(sentences), self.vector_dimension))

    def _encode_with_lite_model(self, sentences, batch_size=32):
        """Encode sentences using the lite model which requires special handling.
        
        The lite model is more memory efficient but requires more steps to use.
        
        Args:
            sentences: List of strings to encode
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings with shape (len(sentences), vector_dimension)
        """
        try:
            # The lite model has separate modules for preprocessing and encoding
            # This approach uses much less memory
            self.logger.info(f"Encoding {len(sentences)} sentences with lite model")
            
            # Process in smaller batches to minimize memory usage
            all_embeddings = []
            for i in range(0, len(sentences), batch_size):
                batch = sentences[i:i+batch_size]
                # For the lite model, we need to call the model directly
                # This is more memory efficient than the standard model
                batch_embeddings = self.model(batch)
                all_embeddings.extend(batch_embeddings.numpy())
                
                # Force garbage collection to free memory
                if i % (batch_size * 5) == 0 and i > 0:
                    import gc
                    gc.collect()
                    
            return np.array(all_embeddings)
        except Exception as e:
            self.logger.error(f"Error encoding with lite model: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(sentences), self.vector_dimension))
