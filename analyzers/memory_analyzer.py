"""
Memory dump analyzer using Volatility integration.
"""

from pathlib import Path
from typing import Dict, Optional
from core.logger import setup_logger

logger = setup_logger("memory_analyzer")


class MemoryAnalyzer:
    """
    Analyze memory dumps using Volatility.
    
    This is a wrapper that prepares memory dumps for analysis.
    Actual Volatility integration is in integrations/volatility.py
    """
    
    SUPPORTED_FORMATS = [
        '.mem', '.dmp', '.raw', '.vmem', '.bin'
    ]
    
    @staticmethod
    def is_memory_dump(file_path: Path) -> bool:
        """
        Check if file is a supported memory dump.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported memory dump format
        """
        return file_path.suffix.lower() in MemoryAnalyzer.SUPPORTED_FORMATS
    
    @staticmethod
    def get_dump_info(file_path: Path) -> Dict:
        """
        Get basic information about a memory dump.
        
        Args:
            file_path: Path to memory dump
            
        Returns:
            Dictionary with dump information
        """
        if not file_path.exists():
            logger.error(f"Memory dump not found: {file_path}")
            return {}
        
        try:
            stat = file_path.stat()
            
            info = {
                'filename': file_path.name,
                'path': str(file_path.absolute()),
                'size': stat.st_size,
                'size_human': MemoryAnalyzer._format_size(stat.st_size),
                'format': file_path.suffix.lower(),
                'is_supported': MemoryAnalyzer.is_memory_dump(file_path)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting dump info: {str(e)}")
            return {}
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"