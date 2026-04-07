"""
AI-Driven Encrypted Duplicate Detection
Uses CNN for binary file similarity analysis without decryption
"""

# AI USAGE DECLARATION: Minor usage of AI (Claude) for code refinements and error checks.
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
        
        # Z-score normalize for balanced gradient flow
        mean = np.mean(feature_vector)
        std = np.std(feature_vector)
        if std > 1e-8:
            feature_vector = (feature_vector - mean) / std
        
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
    Lightweight Siamese CNN for binary similarity detection
    Uses two-layer projection with contrastive learning
    Trained on pairs of feature vectors to learn similarity
    """
    
    def __init__(self, input_size: int = 2048, hidden_size: int = 512, embedding_size: int = 128):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.embedding_size = embedding_size
        
        # Xavier initialization for stable gradients
        # Layer 1: input → hidden
        scale1 = np.sqrt(2.0 / (input_size + hidden_size))
        self.W1 = np.random.randn(hidden_size, input_size).astype(np.float32) * scale1
        self.b1 = np.zeros(hidden_size, dtype=np.float32)
        
        # Layer 2: hidden → embedding
        scale2 = np.sqrt(2.0 / (hidden_size + embedding_size))
        self.W2 = np.random.randn(embedding_size, hidden_size).astype(np.float32) * scale2
        self.b2 = np.zeros(embedding_size, dtype=np.float32)
        
        # Trained flag
        self.is_trained = False
    
    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Forward pass: two-layer projection to embedding space
        Returns both the embedding and intermediate values for backprop
        """
        # Layer 1: linear + ReLU
        z1 = np.dot(self.W1, x) + self.b1
        h1 = np.maximum(0, z1)  # ReLU
        
        # Layer 2: linear (no activation before normalization)
        z2 = np.dot(self.W2, h1) + self.b2
        
        # L2 normalization
        norm = np.linalg.norm(z2)
        if norm > 1e-8:
            embedding = z2 / norm
        else:
            embedding = z2
        
        return embedding
    
    def _forward_with_cache(self, x: np.ndarray):
        """Forward pass that also returns intermediate values for gradient computation"""
        # Layer 1
        z1 = np.dot(self.W1, x) + self.b1
        h1 = np.maximum(0, z1)  # ReLU
        relu_mask = (z1 > 0).astype(np.float32)  # Which neurons fired
        
        # Layer 2
        z2 = np.dot(self.W2, h1) + self.b2
        
        # L2 normalization
        norm = np.linalg.norm(z2)
        if norm > 1e-8:
            embedding = z2 / norm
        else:
            embedding = z2
            norm = 1.0
        
        return embedding, h1, relu_mask, z2, norm
    
    def train_on_pairs(
        self,
        pairs: List[Tuple[np.ndarray, np.ndarray, bool]],
        epochs: int = 10,
        learning_rate: float = 0.005,
        margin: float = 0.3
    ):
        """
        Contrastive learning on pairs with proper gradient backpropagation.
        
        For similar pairs: minimize (1 - cosine_similarity)
        For dissimilar pairs: minimize max(0, cosine_similarity - margin)
        
        Gradients are backpropagated through:
          L2 normalization → Layer 2 (linear) → ReLU → Layer 1 (linear)
        """
        print(f"Training CNN on {len(pairs)} pairs for {epochs} epochs...")
        print(f"  Learning rate: {learning_rate}, Margin: {margin}")
        
        for epoch in range(epochs):
            total_loss = 0.0
            num_updates = 0
            
            # Shuffle pairs each epoch
            indices = np.random.permutation(len(pairs))
            
            for idx in indices:
                vec1, vec2, is_similar = pairs[idx]
                
                # Forward pass with cached intermediate values
                emb1, h1_1, mask1, z2_1, norm1 = self._forward_with_cache(vec1)
                emb2, h1_2, mask2, z2_2, norm2 = self._forward_with_cache(vec2)
                
                # Cosine similarity (embeddings are already L2-normalized)
                cos_sim = np.dot(emb1, emb2)
                cos_sim = np.clip(cos_sim, -1.0, 1.0)
                
                # Contrastive loss and gradient of loss w.r.t. cos_sim
                if is_similar:
                    loss = (1.0 - cos_sim) ** 2
                    d_cos = -2.0 * (1.0 - cos_sim)  # d(loss)/d(cos_sim)
                else:
                    if cos_sim > margin:
                        loss = (cos_sim - margin) ** 2
                        d_cos = 2.0 * (cos_sim - margin)
                    else:
                        loss = 0.0
                        d_cos = 0.0
                
                total_loss += loss
                
                if abs(d_cos) < 1e-10:
                    continue
                
                num_updates += 1
                
                # Gradient of cos_sim w.r.t. z2 (pre-normalization)
                # cos_sim = (z2_1/z2_1) · (z2_2/z2_2)
                # d(cos_sim)/d(z2_1) = (emb2 - cos_sim * emb1) / norm1
                d_z2_1 = d_cos * (emb2 - cos_sim * emb1) / max(norm1, 1e-8)
                d_z2_2 = d_cos * (emb1 - cos_sim * emb2) / max(norm2, 1e-8)
                
                # Clip gradients to prevent explosion
                grad_clip = 1.0
                d_z2_1 = np.clip(d_z2_1, -grad_clip, grad_clip)
                d_z2_2 = np.clip(d_z2_2, -grad_clip, grad_clip)
                
                # Backprop through Layer 2: z2 = W2 @ h1 + b2
                dW2_1 = np.outer(d_z2_1, h1_1)
                dW2_2 = np.outer(d_z2_2, h1_2)
                db2 = d_z2_1 + d_z2_2
                
                # Backprop to h1
                d_h1_1 = np.dot(self.W2.T, d_z2_1)
                d_h1_2 = np.dot(self.W2.T, d_z2_2)
                
                # Backprop through ReLU: d_z1 = d_h1 * relu_mask
                d_z1_1 = d_h1_1 * mask1
                d_z1_2 = d_h1_2 * mask2
                
                # Backprop through Layer 1: z1 = W1 @ x + b1
                dW1_1 = np.outer(d_z1_1, vec1)
                dW1_2 = np.outer(d_z1_2, vec2)
                db1 = d_z1_1 + d_z1_2
                
                # Update weights (gradient descent)
                self.W2 -= learning_rate * (dW2_1 + dW2_2)
                self.b2 -= learning_rate * db2
                self.W1 -= learning_rate * (dW1_1 + dW1_2)
                self.b1 -= learning_rate * db1
            
            avg_loss = total_loss / len(pairs) if pairs else 0
            print(f"  Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.6f}, Updates: {num_updates}/{len(pairs)}")
        
        self.is_trained = True
        print("Training complete!")
    
    # Keep backward-compatible train() method
    def train(self, X_train: List[np.ndarray], y_train: List[int], epochs: int = 10):
        """Legacy training interface — converts to pair-based training"""
        # Build pairs from individual samples
        pairs = []
        for i in range(len(X_train)):
            for j in range(i + 1, len(X_train)):
                is_similar = (y_train[i] == y_train[j])
                pairs.append((X_train[i], X_train[j], is_similar))
        self.train_on_pairs(pairs, epochs=epochs)
    
    def similarity(self, x1: np.ndarray, x2: np.ndarray) -> float:
        """Calculate similarity between two files (0 to 1)"""
        emb1 = self.forward(x1)
        emb2 = self.forward(x2)
        
        # Cosine similarity (clamp to [0, 1] for interpretability)
        sim = np.dot(emb1, emb2)
        return float(max(0.0, min(1.0, sim)))
    
    def save_model(self, path: Path):
        """Save model weights"""
        model_data = {
            'W1': self.W1,
            'b1': self.b1,
            'W2': self.W2,
            'b2': self.b2,
            'input_size': self.input_size,
            'hidden_size': self.hidden_size,
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
        
        self.W1 = model_data['W1']
        self.b1 = model_data['b1']
        self.W2 = model_data['W2']
        self.b2 = model_data['b2']
        self.input_size = model_data['input_size']
        self.hidden_size = model_data.get('hidden_size', 512)
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
        epochs: int = 10,
        learning_rate: float = 0.005,
        margin: float = 0.3
    ):
        """
        Train model on labeled file pairs
    """
        print(f"Preparing training data from {len(file_pairs)} pairs...")
        
        # Encode all files and build pair list
        encoded_pairs = []
        for file1, file2, is_duplicate in file_pairs:
            vec1 = self.encoder.encode_file(file1)
            vec2 = self.encoder.encode_file(file2)
            encoded_pairs.append((vec1, vec2, is_duplicate))
        
        self.cnn.train_on_pairs(encoded_pairs, epochs=epochs, learning_rate=learning_rate, margin=margin)
    
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
    
    print("\n AI deduplication module ready!")