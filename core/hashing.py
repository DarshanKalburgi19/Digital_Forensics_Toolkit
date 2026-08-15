"""
Cryptographic hashing module for evidence integrity verification.
"""

import hashlib
from pathlib import Path
from typing import Dict, Optional
from .logger import setup_logger

logger = setup_logger("hashing")


class HashCalculator:
    """
    Calculate and verify cryptographic hashes for forensic evidence.
    """
    
    # Supported hash algorithms
    ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512
    }
    
    # Default chunk size for reading large files (8 KB)
    CHUNK_SIZE = 8192
    
    @classmethod
    def hash_file(
        cls,
        file_path: Path,
        algorithm: str = 'sha256',
        chunk_size: int = CHUNK_SIZE
    ) -> Optional[str]:
        """
        Calculate hash of a file using specified algorithm.
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm to use
            chunk_size: Bytes to read per iteration
            
        Returns:
            Hexadecimal hash string or None if error
        """
        algorithm = algorithm.lower()
        
        if algorithm not in cls.ALGORITHMS:
            logger.error(f"Unsupported hash algorithm: {algorithm}")
            return None
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        try:
            hash_obj = cls.ALGORITHMS[algorithm]()
            
            with open(file_path, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hash_obj.update(chunk)
            
            hash_value = hash_obj.hexdigest()
            logger.info(f"Calculated {algorithm.upper()} for {file_path.name}: {hash_value}")
            return hash_value
            
        except PermissionError:
            logger.error(f"Permission denied reading file: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error hashing file {file_path}: {str(e)}")
            return None
    
    @classmethod
    def hash_file_multiple(
        cls,
        file_path: Path,
        algorithms: list = None
    ) -> Dict[str, Optional[str]]:
        """
        Calculate multiple hashes for a file.
        
        Args:
            file_path: Path to file
            algorithms: List of algorithms (default: all supported)
            
        Returns:
            Dictionary mapping algorithm names to hash values
        """
        if algorithms is None:
            algorithms = list(cls.ALGORITHMS.keys())
        
        results = {}
        for algorithm in algorithms:
            results[algorithm] = cls.hash_file(file_path, algorithm)
        
        return results
    
    @classmethod
    def verify_hash(
        cls,
        file_path: Path,
        expected_hash: str,
        algorithm: str = 'sha256'
    ) -> bool:
        """
        Verify file integrity against expected hash.
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            
        Returns:
            True if hashes match, False otherwise
        """
        current_hash = cls.hash_file(file_path, algorithm)
        
        if current_hash is None:
            return False
        
        match = current_hash.lower() == expected_hash.lower()
        
        if match:
            logger.info(f"Hash verification PASSED for {file_path.name}")
        else:
            logger.warning(
                f"Hash verification FAILED for {file_path.name}: "
                f"expected {expected_hash}, got {current_hash}"
            )
        
        return match
    
    @classmethod
    def get_file_info(cls, file_path: Path) -> Dict[str, any]:
        """
        Get file information including size and all hashes.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file information
        """
        if not file_path.exists():
            return {}
        
        try:
            stat = file_path.stat()
            hashes = cls.hash_file_multiple(file_path)
            
            return {
                'filename': file_path.name,
                'path': str(file_path.absolute()),
                'size': stat.st_size,
                'size_human': cls._format_size(stat.st_size),
                'modified': stat.st_mtime,
                'created': stat.st_ctime,
                'hashes': hashes
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return {}
    
    @staticmethod
    def _format_size(size: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size: Size in bytes
            
        Returns:
            Formatted size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"