"""
Disk image analyzer using Sleuth Kit integration.
"""

from pathlib import Path
from typing import Dict, Optional, List
from core.logger import setup_logger

logger = setup_logger("disk_analyzer")


class DiskAnalyzer:
    """
    Analyze disk images using Sleuth Kit.
    
    This is a wrapper that prepares disk images for analysis.
    Actual Sleuth Kit integration is in integrations/sleuthkit.py
    """
    
    SUPPORTED_FORMATS = [
        '.e01', '.e02', '.001', '.dd', '.raw', '.img', '.aff', '.afd'
    ]
    
    @staticmethod
    def is_disk_image(file_path: Path) -> bool:
        """
        Check if file is a supported disk image.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if supported disk image format
        """
        return file_path.suffix.lower() in DiskAnalyzer.SUPPORTED_FORMATS
    
    @staticmethod
    def get_image_info(file_path: Path) -> Dict:
        """
        Get basic information about a disk image.
        
        Args:
            file_path: Path to disk image
            
        Returns:
            Dictionary with image information
        """
        if not file_path.exists():
            logger.error(f"Disk image not found: {file_path}")
            return {}
        
        try:
            stat = file_path.stat()
            
            info = {
                'filename': file_path.name,
                'path': str(file_path.absolute()),
                'size': stat.st_size,
                'size_human': DiskAnalyzer._format_size(stat.st_size),
                'format': file_path.suffix.lower(),
                'is_supported': DiskAnalyzer.is_disk_image(file_path)
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting image info: {str(e)}")
            return {}
    
    @staticmethod
    def _format_size(size: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"