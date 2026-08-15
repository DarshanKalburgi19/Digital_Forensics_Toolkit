"""
Tests for hashing module.
"""

import unittest
import tempfile
from pathlib import Path
from core.hashing import HashCalculator


class TestHashCalculator(unittest.TestCase):
    """Test cases for HashCalculator."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary test file
        self.test_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
        self.test_data = b"This is test data for forensic hashing."
        self.test_file.write(self.test_data)
        self.test_file.close()
        self.test_path = Path(self.test_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_path.exists():
            self.test_path.unlink()
    
    def test_md5_hash(self):
        """Test MD5 hash calculation."""
        hash_value = HashCalculator.hash_file(self.test_path, 'md5')
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 32)  # MD5 is 32 hex chars
    
    def test_sha1_hash(self):
        """Test SHA-1 hash calculation."""
        hash_value = HashCalculator.hash_file(self.test_path, 'sha1')
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 40)  # SHA-1 is 40 hex chars
    
    def test_sha256_hash(self):
        """Test SHA-256 hash calculation."""
        hash_value = HashCalculator.hash_file(self.test_path, 'sha256')
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 64)  # SHA-256 is 64 hex chars
    
    def test_sha512_hash(self):
        """Test SHA-512 hash calculation."""
        hash_value = HashCalculator.hash_file(self.test_path, 'sha512')
        self.assertIsNotNone(hash_value)
        self.assertEqual(len(hash_value), 128)  # SHA-512 is 128 hex chars
    
    def test_multiple_hashes(self):
        """Test calculating multiple hashes at once."""
        hashes = HashCalculator.hash_file_multiple(self.test_path)
        
        self.assertIn('md5', hashes)
        self.assertIn('sha1', hashes)
        self.assertIn('sha256', hashes)
        self.assertIn('sha512', hashes)
        
        for hash_value in hashes.values():
            self.assertIsNotNone(hash_value)
    
    def test_hash_consistency(self):
        """Test that hashing same file produces same result."""
        hash1 = HashCalculator.hash_file(self.test_path, 'sha256')
        hash2 = HashCalculator.hash_file(self.test_path, 'sha256')
        
        self.assertEqual(hash1, hash2)
    
    def test_verify_hash_success(self):
        """Test hash verification with correct hash."""
        original_hash = HashCalculator.hash_file(self.test_path, 'sha256')
        result = HashCalculator.verify_hash(self.test_path, original_hash, 'sha256')
        
        self.assertTrue(result)
    
    def test_verify_hash_failure(self):
        """Test hash verification with incorrect hash."""
        wrong_hash = "0" * 64
        result = HashCalculator.verify_hash(self.test_path, wrong_hash, 'sha256')
        
        self.assertFalse(result)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent file."""
        fake_path = Path("nonexistent_file.txt")
        hash_value = HashCalculator.hash_file(fake_path, 'sha256')
        
        self.assertIsNone(hash_value)
    
    def test_large_file_handling(self):
        """Test hashing of larger file using chunks."""
        # Create 1MB file
        large_file = tempfile.NamedTemporaryFile(delete=False, mode='wb')
        large_data = b"X" * (1024 * 1024)  # 1MB
        large_file.write(large_data)
        large_file.close()
        large_path = Path(large_file.name)
        
        try:
            hash_value = HashCalculator.hash_file(large_path, 'sha256')
            self.assertIsNotNone(hash_value)
            self.assertEqual(len(hash_value), 64)
        finally:
            large_path.unlink()
    
    def test_get_file_info(self):
        """Test getting complete file information."""
        info = HashCalculator.get_file_info(self.test_path)
        
        self.assertIn('filename', info)
        self.assertIn('size', info)
        self.assertIn('hashes', info)
        self.assertIn('md5', info['hashes'])
        self.assertIn('sha256', info['hashes'])


if __name__ == '__main__':
    unittest.main()