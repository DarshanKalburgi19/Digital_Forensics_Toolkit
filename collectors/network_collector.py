"""
Network information collector for live forensics.
"""

import psutil
import socket
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import json
from core.logger import setup_logger

logger = setup_logger("network_collector")


class NetworkConnection:
    """
    Represents a network connection.
    """
    
    def __init__(self, conn: psutil._common.sconn):
        """
        Initialize from psutil connection object.
        
        Args:
            conn: psutil network connection
        """
        self.family = str(conn.family)
        self.type = str(conn.type)
        self.local_address = conn.laddr.ip if conn.laddr else None
        self.local_port = conn.laddr.port if conn.laddr else None
        self.remote_address = conn.raddr.ip if conn.raddr else None
        self.remote_port = conn.raddr.port if conn.raddr else None
        self.status = conn.status
        self.pid = conn.pid
        
        # Try to get process name
        self.process_name = None
        if conn.pid:
            try:
                proc = psutil.Process(conn.pid)
                self.process_name = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'family': self.family,
            'type': self.type,
            'local_address': self.local_address,
            'local_port': self.local_port,
            'remote_address': self.remote_address,
            'remote_port': self.remote_port,
            'status': self.status,
            'pid': self.pid,
            'process_name': self.process_name
        }


class NetworkCollector:
    """
    Collect network connection information from live system.
    """
    
    @staticmethod
    def collect_connections() -> List[NetworkConnection]:
        """
        Collect all network connections.
        
        Returns:
            List of NetworkConnection objects
        """
        logger.info("Collecting network connections...")
        
        connections = []
        
        try:
            for conn in psutil.net_connections(kind='inet'):
                try:
                    net_conn = NetworkConnection(conn)
                    connections.append(net_conn)
                except Exception as e:
                    logger.warning(f"Error processing connection: {str(e)}")
                    continue
            
            logger.info(f"Collected {len(connections)} network connections")
            
        except psutil.AccessDenied:
            logger.warning(
                "Access denied collecting network connections. "
                "Administrator/root privileges may be required."
            )
        except Exception as e:
            logger.error(f"Error collecting network connections: {str(e)}")
        
        return connections
    
    @staticmethod
    def collect_interfaces() -> Dict:
        """
        Collect network interface information.
        
        Returns:
            Dictionary of interface information
        """
        logger.info("Collecting network interface information...")
        
        interfaces = {}
        
        try:
            if_addrs = psutil.net_if_addrs()
            if_stats = psutil.net_if_stats()
            
            for interface_name, addrs in if_addrs.items():
                interface_info = {
                    'addresses': [],
                    'is_up': False,
                    'speed': 0,
                    'mtu': 0
                }
                
                # Get statistics
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
                    
                    if hasattr(addr, 'netmask') and addr.netmask:
                        addr_info['netmask'] = addr.netmask
                    if hasattr(addr, 'broadcast') and addr.broadcast:
                        addr_info['broadcast'] = addr.broadcast
                    
                    interface_info['addresses'].append(addr_info)
                
                interfaces[interface_name] = interface_info
            
        except Exception as e:
            logger.error(f"Error collecting interface information: {str(e)}")
        
        return interfaces
    
    @staticmethod
    def collect_all() -> Dict:
        """
        Collect all network information.
        
        Returns:
            Dictionary with connections and interfaces
        """
        return {
            'collection_timestamp': datetime.now().isoformat(),
            'hostname': socket.gethostname(),
            'connections': [c.to_dict() for c in NetworkCollector.collect_connections()],
            'interfaces': NetworkCollector.collect_interfaces()
        }
    
    @staticmethod
    def save_to_file(data: Dict, output_path: Path) -> bool:
        """
        Save network information to JSON file.
        
        Args:
            data: Network information dictionary
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Network information saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving network information: {str(e)}")
            return False