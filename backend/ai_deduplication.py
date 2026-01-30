"""
AI-Driven Encrypted Duplicate Detection
Uses CNN for binary file similarity analysis without decryption
"""

import numpy as np
import hashlib
from typing import List, Tuple, Optional
from pathlib import Path
import pickle
import json


class BinaryFileEncoder:
    """Convert binary files to fixed-size feature vectors"""
    
    def __init__(self, chunk_size: int = 256, vector_size: int = 2048):
        self.chunk_size = chunk_size
        self.vector_size = vector_size
    
    def encode_file(self, file_content: bytes) -> np.ndarray:
        """
        Convert binary file to feature vector
        Uses statistical properties of encrypted data
        """
        # Ensure minimum length
        if len(file_content) < self.chunk_size:
            file_content = file_content + b'\x00' * (self.chunk_size - len(file_content))
        
        # Extract features
        features = []
        
        # 1. Byte frequency distribution (256 bins)
        byte_counts = np.bincount(np.frombuffer(file_content, dtype=np.uint8), minlength=256)
        byte_freq = byte_counts / len(file_content)
        features.extend(byte_freq)
        
        # 2. Byte pair frequencies (sample 256 most common pairs)
        pairs = []
        for i in range(0, len(file_content) - 1, 2):
            pair_val = (file_content[i] << 8) | file_content[i + 1]
            pairs.append(pair_val)
        pair_counts = np.bincount(pairs, minlength=65536)
        top_pairs = np.argsort(pair_counts)[-256:]
        pair_features = pair_counts[top_pairs] / len(pairs)
        features.extend(pair_features)
        
        # 3. Entropy measures (per chunk)
        chunk_entropies = []
        for i in range(0, len(file_content), self.chunk_size):
            chunk = file_content[i:i + self.chunk_size]
            if len(chunk) < self.chunk_size:
                chunk = chunk + b'\x00' * (self.chunk_size - len(chunk))
            entropy = self._calculate_entropy(chunk)
            chunk_entropies.append(entropy)
        
        # Pad to fixed size (256 chunks)
        if len(chunk_entropies) < 256:
            chunk_entropies.extend([0.0] * (256 - len(chunk_entropies)))
        else:
            chunk_entropies = chunk_entropies[:256]
        features.extend(chunk_entropies)
        
        # 4. Statistical moments (mean, std, skewness, kurtosis)
        byte_array = np.frombuffer(file_content, dtype=np.uint8)
        stats = [
            np.mean(byte_array),
            np.std(byte_array),
            self._skewness(byte_array),
            self._kurtosis(byte_array)
        ]
        features.extend(stats)
        
        # Convert to fixed-size vector
        feature_vector = np.array(features[:self.vector_size])
        
        # Pad if necessary
        if len(feature_vector) < self.vector_size:
            padding = np.zeros(self.vector_size - len(feature_vector))
            feature_vector = np.concatenate([feature_vector, padding])
        
        return feature_vector.astype(np.float32)
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy"""
        if len(data) == 0:
            return 0.0
        
        counts = np.bincount(np.frombuffer(data, dtype=np.uint8))
        probabilities = counts[counts > 0] / len(data)
        entropy = -np.sum(probabilities * np.log2(probabilities))
        return entropy
    
    def _skewness(self, data: np.ndarray) -> float:
        """Calculate skewness (3rd moment)"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 3)
    
    def _kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis (4th moment)"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return 0.0
        return np.mean(((data - mean) / std) ** 4)


class SimpleCNN:
    """
    Lightweight CNN for binary similarity detection
    Uses cosine similarity on learned embeddings
    """
    
    def __init__(self, input_size: int = 2048, embedding_size: int = 128):
        self.input_size = input_size
        self.embedding_size = embedding_size
        
        # Simple projection layer (W * x + b)
        self.W = np.random.randn(embedding_size, input_size).astype(np.float32) * 0.01
        self.b = np.zeros(embedding_size, dtype=np.float32)
        
        # Trained flag
        self.is_trained = False
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass: project to embedding space
        Uses ReLU activation
        """
        # Linear projection
        z = np.dot(self.W, x) + self.b
        
        # ReLU activation
        embedding = np.maximum(0, z)
        
        # L2 normalization for cosine similarity
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def train(self, X_train: List[np.ndarray], y_train: List[int], epochs: int = 10):
        """
        Simple contrastive learning
        Brings similar files closer, pushes dissimilar files apart
        """
        print(f"Training CNN on {len(X_train)} samples for {epochs} epochs...")
        
        learning_rate = 0.01
        
        for epoch in range(epochs):
            total_loss = 0
            
            # Mini-batch training
            for i in range(len(X_train) - 1):
                x1 = X_train[i]
                y1 = y_train[i]
                
                # Find pair
                for j in range(i + 1, len(X_train)):
                    x2 = X_train[j]
                    y2 = y_train[j]
                    
                    # Forward pass
                    emb1 = self.forward(x1)
                    emb2 = self.forward(x2)
                    
                    # Cosine similarity
                    similarity = np.dot(emb1, emb2)
                    
                    # Contrastive loss
                    if y1 == y2:
                        # Same class: minimize distance
                        loss = 1 - similarity
                    else:
                        # Different class: maximize distance
                        loss = max(0, similarity - 0.2)  # margin = 0.2
                    
                    total_loss += loss
                    
                    # Simple gradient update (approximation)
                    if loss > 0:
                        grad = (emb2 - emb1) if y1 == y2 else (emb1 - emb2)
                        self.W += learning_rate * np.outer(grad, x1)
            
            avg_loss = total_loss / (len(X_train) * (len(X_train) - 1) / 2)
            print(f"Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}")
        
        self.is_trained = True
        print("Training complete!")
    
    def similarity(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Calculate similarity between two files (0 to 1)"""
        emb1 = self.forward(x1)
        emb2 = self.forward(x2)
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2)
        return float(similarity)
    
    def save_model(self, path: Path):
        """Save model weights"""
        model_data = {
            'W': self.W,
            'b': self.b,
            'input_size': self.input_size,
            'embedding_size': self.embedding_size,
            'is_trained': self.is_trained
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Model saved to {path}")
    
    def load_model(self, path: Path):
        """Load model weights"""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)
        
        self.W = model_data['W']
        self.b = model_data['b']
        self.input_size = model_data['input_size']
        self.embedding_size = model_data['embedding_size']
        self.is_trained = model_data['is_trained']
        print(f"Model loaded from {path}")


class AIDeduplicationEngine:
    """
    Main engine combining encoder + CNN
    Detects encrypted duplicates using learned similarity
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        self.encoder = BinaryFileEncoder()
        self.cnn = SimpleCNN()
        
        if model_path and model_path.exists():
            self.cnn.load_model(model_path)
        
        # Cache of encoded files
        self.file_cache: dict = {}
    
    def check_similarity(
        self, 
        file1: bytes, 
        file2: bytes, 
        threshold: float = 0.85
    ) -> Tuple[bool, float]:
        """
        Check if two encrypted files are likely duplicates
        
        Args:
            file1: First file content (encrypted)
            file2: Second file content (encrypted)
            threshold: Similarity threshold (0.85 = 85% similar)
        
        Returns:
            (is_duplicate, similarity_score)
        """
        # Encode files
        vec1 = self.encoder.encode_file(file1)
        vec2 = self.encoder.encode_file(file2)
        
        # Calculate similarity
        similarity = self.cnn.similarity(vec1, vec2)
        
        is_duplicate = similarity >= threshold
        return is_duplicate, similarity
    
    def train_on_dataset(
        self, 
        file_pairs: List[Tuple[bytes, bytes, bool]], 
        epochs: int = 10
    ):
        """
        Train model on labeled file pairs
        
        Args:
            file_pairs: List of (file1, file2, is_duplicate) tuples
            epochs: Number of training epochs
        """
        print(f"Preparing training data from {len(file_pairs)} pairs...")
        
        X_train = []
        y_train = []
        
        for file1, file2, is_duplicate in file_pairs:
            vec1 = self.encoder.encode_file(file1)
            vec2 = self.encoder.encode_file(file2)
            
            X_train.extend([vec1, vec2])
            label = 1 if is_duplicate else 0
            y_train.extend([label, label])
        
        self.cnn.train(X_train, y_train, epochs=epochs)
    
    def save_model(self, path: Path):
        """Save trained model"""
        self.cnn.save_model(path)
    
    def load_model(self, path: Path):
        """Load trained model"""
        self.cnn.load_model(path)


# Example usage and testing
if __name__ == "__main__":
    print("=== AI-Driven Deduplication Demo ===\n")
    
    # Create engine
    engine = AIDeduplicationEngine()
    
    # Test files (simulating encrypted data)
    file1 = b"This is a test file content" * 100
    file2 = b"This is a test file content" * 100  # Duplicate
    file3 = b"Different file with other content" * 100
    
    # Add some noise to simulate encryption variations
    file2_noisy = file2 + b"\x00\x01\x02"
    
    # Create training dataset
    training_pairs = [
        (file1, file2, True),   # Duplicates
        (file1, file2_noisy, True),  # Similar with noise
        (file1, file3, False),  # Different
        (file2, file3, False),  # Different
    ]
    
    # Train model
    engine.train_on_dataset(training_pairs, epochs=20)
    
    # Test similarity detection
    print("\n=== Testing Similarity Detection ===")
    
    test_cases = [
        (file1, file2, "Exact duplicate"),
        (file1, file2_noisy, "Duplicate with noise"),
        (file1, file3, "Different files"),
    ]
    
    for f1, f2, description in test_cases:
        is_dup, score = engine.check_similarity(f1, f2, threshold=0.85)
        print(f"{description}: {score:.3f} -> {'DUPLICATE' if is_dup else 'UNIQUE'}")
    
    # Save model
    model_path = Path("data/ai_model.pkl")
    model_path.parent.mkdir(exist_ok=True)
    engine.save_model(model_path)
    
    print("\n✅ AI deduplication module ready!")