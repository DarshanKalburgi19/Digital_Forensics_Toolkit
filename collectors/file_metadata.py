"""
File metadata collector for forensic analysis.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import mimetypes
from core.hashing import HashCalculator
from core.logger import setup_logger

logger = setup_logger("file_metadata")


class FileMetadataCollector:
    """
    Collect metadata from files without modification.
    """
    
    @staticmethod
    def collect(file_path: Path) -> Optional[Dict]:
        """
        Collect metadata from a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with file metadata or None if error
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        if not file_path.is_file():
            logger.error(f"Not a file: {file_path}")
            return None
        
        try:
            logger.info(f"Collecting metadata for {file_path.name}")
            
            # File statistics
            stat = file_path.stat()
            
            # MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            
            # Hash values
            hashes = HashCalculator.hash_file_multiple(file_path)
            
            metadata = {
                'filename': file_path.name,
                'full_path': str(file_path.absolute()),
                'extension': file_path.suffix,
                'size': stat.st_size,
                'size_human': FileMetadataCollector._format_size(stat.st_size),
                'mime_type': mime_type or 'Unknown',
                'created': stat.st_ctime,
                'created_str': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'modified': stat.st_mtime,
                'modified_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'accessed': stat.st_atime,
                'accessed_str': datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
                'hashes': hashes,
                'collection_timestamp': datetime.now().isoformat()
            }
            
            # Windows-specific attributes
            if hasattr(stat, 'st_file_attributes'):
                metadata['windows_attributes'] = stat.st_file_attributes
            
            logger.info(f"Metadata collected for {file_path.name}")
            return metadata
            
        except PermissionError:
            logger.error(f"Permission denied: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error collecting metadata: {str(e)}")
            return None
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"