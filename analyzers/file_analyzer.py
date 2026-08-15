"""
File analysis module for forensic investigations.
"""

import magic
from pathlib import Path
from typing import Dict, Optional, List
import hashlib
from core.logger import setup_logger
from core.hashing import HashCalculator

logger = setup_logger("file_analyzer")


class FileAnalyzer:
    """
    Analyze files for forensic purposes.
    """
    
    @staticmethod
    def analyze_file(file_path: Path) -> Optional[Dict]:
        """
        Perform comprehensive file analysis.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dictionary with analysis results
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        try:
            logger.info(f"Analyzing file: {file_path.name}")
            
            # Basic file info
            stat = file_path.stat()
            
            # Calculate hashes
            hashes = HashCalculator.hash_file_multiple(file_path)
            
            # Get file type
            file_type = FileAnalyzer._get_file_type(file_path)
            
            # Get file signature (magic bytes)
            file_signature = FileAnalyzer._get_file_signature(file_path)
            
            # Check for common file types
            file_category = FileAnalyzer._categorize_file(file_path)
            
            analysis = {
                'filename': file_path.name,
                'path': str(file_path.absolute()),
                'size': stat.st_size,
                'size_human': FileAnalyzer._format_size(stat.st_size),
                'extension': file_path.suffix.lower(),
                'file_type': file_type,
                'file_signature': file_signature,
                'category': file_category,
                'hashes': hashes,
                'timestamps': {
                    'created': stat.st_ctime,
                    'modified': stat.st_mtime,
                    'accessed': stat.st_atime
                }
            }
            
            logger.info(f"File analysis complete: {file_path.name}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing file: {str(e)}")
            return None
    
    @staticmethod
    def _get_file_type(file_path: Path) -> str:
        """
        Determine file type using python-magic if available.
        
        Args:
            file_path: Path to file
            
        Returns:
            File type description
        """
        try:
            # Try using python-magic if available
            import magic
            return magic.from_file(str(file_path))
        except ImportError:
            # Fallback to extension-based detection
            import mimetypes
            mime_type, _ = mimetypes.guess_type(str(file_path))
            return mime_type or 'Unknown'
        except Exception as e:
            logger.warning(f"Error detecting file type: {str(e)}")
            return 'Unknown'
    
    @staticmethod
    def _get_file_signature(file_path: Path, num_bytes: int = 16) -> str:
        """
        Get file signature (magic bytes).
        
        Args:
            file_path: Path to file
            num_bytes: Number of bytes to read
            
        Returns:
            Hex representation of file signature
        """
        try:
            with open(file_path, 'rb') as f:
                signature = f.read(num_bytes)
                return signature.hex().upper()
        except Exception as e:
            logger.warning(f"Error reading file signature: {str(e)}")
            return ''
    
    @staticmethod
    def _categorize_file(file_path: Path) -> str:
        """
        Categorize file based on extension and signature.
        
        Args:
            file_path: Path to file
            
        Returns:
            File category
        """
        ext = file_path.suffix.lower()
        
        # Image files
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.ico']:
            return 'Image'
        
        # Document files
        if ext in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']:
            return 'Document'
        
        # Archive files
        if ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
            return 'Archive'
        
        # Executable files
        if ext in ['.exe', '.dll', '.sys', '.bat', '.cmd', '.ps1', '.sh']:
            return 'Executable'
        
        # Forensic image files
        if ext in ['.e01', '.e02', '.001', '.dd', '.raw', '.img']:
            return 'Forensic Image'
        
        # Memory dump files
        if ext in ['.mem', '.dmp', '.vmem']:
            return 'Memory Dump'
        
        # Database files
        if ext in ['.db', '.sqlite', '.sqlite3', '.mdb']:
            return 'Database'
        
        # Log files
        if ext in ['.log', '.evtx', '.evt']:
            return 'Log File'
        
        return 'Other'
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"
    
    @staticmethod
    def analyze_multiple(file_paths: List[Path]) -> List[Dict]:
        """
        Analyze multiple files.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of analysis results
        """
        results = []
        
        for file_path in file_paths:
            analysis = FileAnalyzer.analyze_file(file_path)
            if analysis:
                results.append(analysis)
        
        return results