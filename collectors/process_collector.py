"""
Process information collector for live forensics.
"""

import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path
import json
from core.logger import setup_logger

logger = setup_logger("process_collector")


class ProcessInfo:
    """
    Represents information about a running process.
    """
    
    def __init__(self, process: psutil.Process):
        """
        Initialize from psutil.Process object.
        
        Args:
            process: psutil.Process instance
        """
        try:
            self.pid = process.pid
            self.name = process.name()
            
            # Try to get additional info (may fail for some processes)
            try:
                self.exe = process.exe()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.exe = None
            
            try:
                self.username = process.username()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.username = None
            
            try:
                self.status = process.status()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.status = "Unknown"
            
            try:
                self.create_time = process.create_time()
                self.create_time_str = datetime.fromtimestamp(
                    self.create_time
                ).strftime('%Y-%m-%d %H:%M:%S')
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.create_time = None
                self.create_time_str = None
            
            try:
                self.cpu_percent = process.cpu_percent(interval=0.1)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.cpu_percent = 0.0
            
            try:
                mem_info = process.memory_info()
                self.memory_rss = mem_info.rss
                self.memory_percent = process.memory_percent()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.memory_rss = 0
                self.memory_percent = 0.0
            
            try:
                self.cmdline = ' '.join(process.cmdline())
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                self.cmdline = None
            
            # Check if potentially suspicious
            self.suspicious_indicators = self._check_suspicious()
            
        except psutil.NoSuchProcess:
            raise
    
    def _check_suspicious(self) -> List[str]:
        """
        Check for potentially interesting process characteristics.
        
        NOTE: This is NOT malware detection. These are simple heuristics
        that may indicate a process worthy of manual investigation.
        
        Returns:
            List of indicator descriptions
        """
        indicators = []
        
        # Missing executable path
        if not self.exe:
            indicators.append("No executable path")
        
        # Running from temporary directories
        if self.exe:
            exe_lower = self.exe.lower()
            temp_dirs = ['temp', 'tmp', 'appdata\\local\\temp', '/tmp/']
            
            for temp_dir in temp_dirs:
                if temp_dir in exe_lower:
                    indicators.append(f"Running from temporary directory: {temp_dir}")
                    break
        
        # Suspicious process names (common test indicators)
        suspicious_names = [
            'nc.exe', 'netcat', 'ncat',
            'mimikatz', 'psexec',
            'procdump', 'pwdump'
        ]
        
        if self.name.lower() in suspicious_names:
            indicators.append(f"Known tool name: {self.name}")
        
        # High CPU or memory (potential DoS or crypto mining)
        if self.cpu_percent > 80:
            indicators.append(f"High CPU usage: {self.cpu_percent:.1f}%")
        
        if self.memory_percent > 50:
            indicators.append(f"High memory usage: {self.memory_percent:.1f}%")
        
        return indicators
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'pid': self.pid,
            'name': self.name,
            'exe': self.exe,
            'username': self.username,
            'status': self.status,
            'create_time': self.create_time,
            'create_time_str': self.create_time_str,
            'cpu_percent': round(self.cpu_percent, 2),
            'memory_rss': self.memory_rss,
            'memory_percent': round(self.memory_percent, 2),
            'cmdline': self.cmdline,
            'suspicious_indicators': self.suspicious_indicators,
            'is_interesting': len(self.suspicious_indicators) > 0
        }


class ProcessCollector:
    """
    Collect running process information from live system.
    """
    
    @staticmethod
    def collect_all() -> List[ProcessInfo]:
        """
        Collect information about all running processes.
        
        Returns:
            List of ProcessInfo objects
        """
        logger.info("Collecting process information...")
        
        processes = []
        
        for proc in psutil.process_iter():
            try:
                proc_info = ProcessInfo(proc)
                processes.append(proc_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
            except Exception as e:
                logger.warning(f"Error processing PID {proc.pid}: {str(e)}")
                continue
        
        logger.info(f"Collected information for {len(processes)} processes")
        return processes
    
    @staticmethod
    def get_suspicious_processes() -> List[ProcessInfo]:
        """
        Get processes with suspicious indicators.
        
        Returns:
            List of ProcessInfo objects with indicators
        """
        all_processes = ProcessCollector.collect_all()
        return [p for p in all_processes if p.suspicious_indicators]
    
    @staticmethod
    def get_process_by_pid(pid: int) -> Optional[ProcessInfo]:
        """
        Get information for specific process.
        
        Args:
            pid: Process ID
            
        Returns:
            ProcessInfo object or None
        """
        try:
            proc = psutil.Process(pid)
            return ProcessInfo(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
        except Exception as e:
            logger.error(f"Error getting process {pid}: {str(e)}")
            return None
    
    @staticmethod
    def save_to_file(processes: List[ProcessInfo], output_path: Path) -> bool:
        """
        Save process information to JSON file.
        
        Args:
            processes: List of ProcessInfo objects
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            data = {
                'collection_timestamp': datetime.now().isoformat(),
                'total_processes': len(processes),
                'processes': [p.to_dict() for p in processes]
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Process information saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving process information: {str(e)}")
            return False