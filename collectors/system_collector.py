"""
System information collector for live forensics.
"""

import platform
import socket
import psutil
from datetime import datetime
from typing import Dict, List
from pathlib import Path
import json
from core.logger import setup_logger

logger = setup_logger("system_collector")


class SystemCollector:
    """
    Collect system information from the investigator's machine or test system.
    
    NOTE: This collects information from the LIVE SYSTEM where the toolkit is running.
    This is intended for educational purposes and testing.
    """
    
    @staticmethod
    def collect_all() -> Dict:
        """
        Collect all system information.
        
        Returns:
            Dictionary containing system information
        """
        logger.info("Collecting system information...")
        
        try:
            info = {
                'collection_timestamp': datetime.now().isoformat(),
                'collection_type': 'LIVE SYSTEM COLLECTION',
                'hostname': SystemCollector.get_hostname(),
                'operating_system': SystemCollector.get_os_info(),
                'hardware': SystemCollector.get_hardware_info(),
                'network': SystemCollector.get_network_info(),
                'boot_time': SystemCollector.get_boot_time(),
                'current_user': SystemCollector.get_current_user()
            }
            
            logger.info("System information collected successfully")
            return info
            
        except Exception as e:
            logger.error(f"Error collecting system information: {str(e)}")
            return {'error': str(e)}
    
    @staticmethod
    def get_hostname() -> str:
        """Get system hostname."""
        try:
            return socket.gethostname()
        except Exception as e:
            logger.error(f"Error getting hostname: {str(e)}")
            return "Unknown"
    
    @staticmethod
    def get_os_info() -> Dict:
        """Get operating system information."""
        try:
            return {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture()[0],
                'platform': platform.platform()
            }
        except Exception as e:
            logger.error(f"Error getting OS info: {str(e)}")
            return {}
    
    @staticmethod
    def get_hardware_info() -> Dict:
        """Get hardware information."""
        try:
            # CPU information
            cpu_freq = psutil.cpu_freq()
            
            # Memory information
            virtual_mem = psutil.virtual_memory()
            swap_mem = psutil.swap_memory()
            
            # Disk information
            disk_partitions = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': usage.percent
                    })
                except PermissionError:
                    continue
            
            return {
                'cpu': {
                    'physical_cores': psutil.cpu_count(logical=False),
                    'logical_cores': psutil.cpu_count(logical=True),
                    'max_frequency': cpu_freq.max if cpu_freq else None,
                    'current_frequency': cpu_freq.current if cpu_freq else None
                },
                'memory': {
                    'total': virtual_mem.total,
                    'available': virtual_mem.available,
                    'used': virtual_mem.used,
                    'percent': virtual_mem.percent,
                    'total_human': SystemCollector._format_bytes(virtual_mem.total),
                    'available_human': SystemCollector._format_bytes(virtual_mem.available)
                },
                'swap': {
                    'total': swap_mem.total,
                    'used': swap_mem.used,
                    'free': swap_mem.free,
                    'percent': swap_mem.percent
                },
                'disk_partitions': disk_partitions
            }
        except Exception as e:
            logger.error(f"Error getting hardware info: {str(e)}")
            return {}
    
    @staticmethod
    def get_network_info() -> Dict:
        """Get network interface information."""
        try:
            interfaces = {}
            
            # Network interface addresses
            if_addrs = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()
            
            for interface_name, addrs in if_addrs.items():
                interface_info = {
                    'addresses': [],
                    'is_up': False,
                    'speed': 0,
                    'mtu': 0
                }
                
                # Get interface statistics
                if interface_name in if_stats:
                    stats = if_stats[interface_name]
                    interface_info['is_up'] = stats.isup
                    interface_info['speed'] = stats.speed
                    interface_info['mtu'] = stats.mtu
                
                # Get addresses
                for addr in addrs:
                    addr_info = {
                        'family': str(addr.family),
                        'address': addr.address
                    }
                    
                    if addr.netmask:
                        addr_info['netmask'] = addr.netmask
                    if addr.broadcast:
                        addr_info['broadcast'] = addr.broadcast
                    
                    interface_info['addresses'].append(addr_info)
                
                interfaces[interface_name] = interface_info
            
            return {
                'interfaces': interfaces,
                'hostname': socket.gethostname(),
                'fqdn': socket.getfqdn()
            }
            
        except Exception as e:
            logger.error(f"Error getting network info: {str(e)}")
            return {}
    
    @staticmethod
    def get_boot_time() -> Dict:
        """Get system boot time."""
        try:
            boot_timestamp = psutil.boot_time()
            boot_datetime = datetime.fromtimestamp(boot_timestamp)
            
            return {
                'timestamp': boot_timestamp,
                'datetime': boot_datetime.isoformat(),
                'human_readable': boot_datetime.strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Error getting boot time: {str(e)}")
            return {}
    
    @staticmethod
    def get_current_user() -> str:
        """Get current username."""
        try:
            import getpass
            return getpass.getuser()
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return "Unknown"
    
    @staticmethod
    def save_to_file(data: Dict, output_path: Path) -> bool:
        """
        Save system information to JSON file.
        
        Args:
            data: System information dictionary
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"System information saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving system information: {str(e)}")
            return False
    
    @staticmethod
    def _format_bytes(bytes_value: int) -> str:
        """Format bytes to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"