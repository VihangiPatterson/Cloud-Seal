"""
Bloom Filter Module - Fast probabilistic duplicate detection
"""
import math
import mmh3  # MurmurHash3 for fast hashing

class BloomFilter:
    """
    Probabilistic data structure for set membership testing
    Trade-off: Fast O(1) lookups with small false positive rate
    """
    
    def __init__(self, expected_items: int = 10000, false_positive_rate: float = 0.01):
        """
        Initialize Bloom filter
        
        Args:
            expected_items: Number of files expected to store
            false_positive_rate: Target error rate (e.g., 0.01 = 1%)
        """
        self.expected_items = expected_items
        self.fp_rate = false_positive_rate
        
        # Calculate optimal size
        self.size = self._calculate_size(expected_items, false_positive_rate)
        
        # Calculate optimal number of hash functions
        self.hash_count = self._calculate_hash_count(self.size, expected_items)
        
        # Initialize bit array (all zeros)
        self.bit_array = [0] * self.size
        
        # Track actual items added (for monitoring)
        self.items_added = 0
        
    def _calculate_size(self, n: int, p: float) -> int:
        """
        Calculate optimal bit array size
        Formula: m = -(n * ln(p)) / (ln(2)^2)
        
        Args:
            n: Expected number of items
            p: Desired false positive rate
            
        Returns:
            Optimal size in bits
        """
        m = -(n * math.log(p)) / (math.log(2) ** 2)
        return int(m)
    
    def _calculate_hash_count(self, m: int, n: int) -> int:
        """
        Calculate optimal number of hash functions
        Formula: k = (m/n) * ln(2)
        
        Args:
            m: Size of bit array
            n: Expected number of items
            
        Returns:
            Optimal number of hash functions
        """
        k = (m / n) * math.log(2)
        return max(1, int(k))
    
    def add(self, item: str) -> None:
        """
        Add item to Bloom filter
        
        Args:
            item: String to add (usually file hash)
        """
        for i in range(self.hash_count):
            # Generate hash using seed i
            hash_value = mmh3.hash(item, i) % self.size
            self.bit_array[hash_value] = 1
        
        self.items_added += 1
    
    def check(self, item: str) -> bool:
        """
        Check if item might be in set
        
        Args:
            item: String to check
            
        Returns:
            False = definitely NOT in set
            True = MAYBE in set (need to verify)
        """
        for i in range(self.hash_count):
            hash_value = mmh3.hash(item, i) % self.size
            if self.bit_array[hash_value] == 0:
                return False  # Definitely not present
        
        return True  # Maybe present (check database)
    
    def get_stats(self) -> dict:
        """
        Get Bloom filter statistics
        
        Returns:
            Dictionary with size, hash count, fill rate
        """
        fill_rate = sum(self.bit_array) / self.size
        return {
            'size_bits': self.size,
            'size_kb': self.size / 8192,
            'hash_functions': self.hash_count,
            'items_added': self.items_added,
            'fill_rate': f"{fill_rate:.2%}",
            'expected_fp_rate': f"{self.fp_rate:.2%}"
        }


# Example Usage
if __name__ == "__main__":
    # Create Bloom filter
    bloom = BloomFilter(expected_items=1000, false_positive_rate=0.01)
    
    # Add items
    test_hashes = [f"hash_{i}" for i in range(100)]
    for h in test_hashes:
        bloom.add(h)
    
    # Test true positives
    true_positives = sum(1 for h in test_hashes if bloom.check(h))
    print(f"True positives: {true_positives}/100 (should be 100)")
    
    # Test false positives
    false_positives = sum(1 for i in range(100, 200) if bloom.check(f"hash_{i}"))
    fp_rate = false_positives / 100
    print(f"False positive rate: {fp_rate:.2%} (target: 1%)")
    
    # Print stats
    print("\nBloom Filter Stats:")
    for key, value in bloom.get_stats().items():
        print(f"  {key}: {value}")
    
    print("\n✅ Bloom filter test passed!")