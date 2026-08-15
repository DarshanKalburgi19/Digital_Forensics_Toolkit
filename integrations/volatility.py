"""
Volatility 3 integration for memory forensics.
"""

import subprocess
import shutil
import sys
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
from core.logger import setup_logger

logger = setup_logger("volatility")


class VolatilityCommand:
    """
    Represents a Volatility command execution result.
    """
    
    def __init__(
        self,
        plugin: str,
        memory_image: str,
        stdout: str,
        stderr: str,
        returncode: int,
        execution_time: float
    ):
        """Initialize command result."""
        self.plugin = plugin
        self.memory_image = memory_image
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode
        self.execution_time = execution_time
        self.timestamp = datetime.now().isoformat()
    
    def success(self) -> bool:
        """Check if command succeeded."""
        return self.returncode == 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'plugin': self.plugin,
            'memory_image': self.memory_image,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'returncode': self.returncode,
            'success': self.success(),
            'execution_time': self.execution_time,
            'timestamp': self.timestamp
        }


class VolatilityIntegration:
    """
    Integration with Volatility 3 for memory forensics.
    """
    
    # Common Volatility 3 plugins
    COMMON_PLUGINS = {
        'windows.info': 'Display Windows system information',
        'windows.pslist': 'List running processes',
        'windows.pstree': 'Process tree',
        'windows.psscan': 'Scan for process objects',
        'windows.dlllist': 'List loaded DLLs',
        'windows.cmdline': 'Display process command lines',
        'windows.netstat': 'Network connections',
        'windows.netscan': 'Scan for network objects',
        'windows.filescan': 'Scan for file objects',
        'windows.registry.hivelist': 'List registry hives',
        'linux.pslist': 'List Linux processes',
        'linux.bash': 'Bash history',
        'mac.pslist': 'List macOS processes'
    }
    
    def __init__(self):
        """Initialize Volatility integration."""
        self.vol_path = self._find_volatility()
        self.is_installed = self.vol_path is not None
        
        if self.is_installed:
            logger.info(f"Volatility 3 found: {self.vol_path}")
        else:
            logger.warning("Volatility 3 not detected")
    
    def _find_volatility(self) -> Optional[str]:
        """
        Find Volatility 3 installation.
        
        Returns:
            Path to Volatility or None
        """
        # Try common executable names
        for cmd in ['vol', 'vol.py', 'volatility3', 'volatility']:
            path = shutil.which(cmd)
            if path:
                # Verify it's actually Volatility 3
                try:
                    result = subprocess.run(
                        [path, '-h'],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if 'volatility' in result.stdout.lower() or 'volatility' in result.stderr.lower():
                        return path
                except:
                    continue
        
        # Try as Python module
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'volatility3', '-h'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return f"{sys.executable} -m volatility3"
        except:
            pass
        
        return None
    
    def is_available(self) -> bool:
        """Check if Volatility is available."""
        return self.is_installed
    
    def run_plugin(
        self,
        memory_image: Path,
        plugin: str,
        additional_args: Optional[List[str]] = None,
        timeout: int = 600
    ) -> Optional[VolatilityCommand]:
        """
        Run a Volatility plugin.
        
        Args:
            memory_image: Path to memory dump
            plugin: Plugin name
            additional_args: Additional arguments
            timeout: Command timeout in seconds
            
        Returns:
            VolatilityCommand object or None
        """
        if not self.is_installed:
            logger.error("Volatility not available")
            return None
        
        if not memory_image.exists():
            logger.error(f"Memory image not found: {memory_image}")
            return None
        
        # Build command
        if ' ' in self.vol_path:  # Python module format
            command = self.vol_path.split() + ['-f', str(memory_image), plugin]
        else:
            command = [self.vol_path, '-f', str(memory_image), plugin]
        
        if additional_args:
            command.extend(additional_args)
        
        try:
            logger.info(f"Running Volatility plugin: {plugin}")
            logger.info(f"Command: {' '.join(command)}")
            
            start_time = datetime.now()
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            vol_result = VolatilityCommand(
                plugin=plugin,
                memory_image=str(memory_image),
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                execution_time=execution_time
            )
            
            if vol_result.success():
                logger.info(f"Plugin {plugin} completed successfully")
            else:
                logger.warning(f"Plugin {plugin} returned code {result.returncode}")
                if result.stderr:
                    logger.warning(f"Error output: {result.stderr[:200]}")
            
            return vol_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Plugin {plugin} timed out after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error running plugin {plugin}: {str(e)}")
            return None
    
    def run_windows_info(self, memory_image: Path) -> Optional[VolatilityCommand]:
        """Run windows.info plugin."""
        return self.run_plugin(memory_image, 'windows.info')
    
    def run_windows_pslist(self, memory_image: Path) -> Optional[VolatilityCommand]:
        """Run windows.pslist plugin."""
        return self.run_plugin(memory_image, 'windows.pslist')
    
    def run_windows_pstree(self, memory_image: Path) -> Optional[VolatilityCommand]:
        """Run windows.pstree plugin."""
        return self.run_plugin(memory_image, 'windows.pstree')
    
    def run_windows_netstat(self, memory_image: Path) -> Optional[VolatilityCommand]:
        """Run windows.netstat plugin."""
        return self.run_plugin(memory_image, 'windows.netstat')
    
    def run_windows_cmdline(self, memory_image: Path) -> Optional[VolatilityCommand]:
        """Run windows.cmdline plugin."""
        return self.run_plugin(memory_image, 'windows.cmdline')
    
    def run_windows_dlllist(
        self,
        memory_image: Path,
        pid: Optional[int] = None
    ) -> Optional[VolatilityCommand]:
        """Run windows.dlllist plugin."""
        args = []
        if pid:
            args.extend(['--pid', str(pid)])
        return self.run_plugin(memory_image, 'windows.dlllist', args)
    
    def save_result(
        self,
        result: VolatilityCommand,
        output_path: Path
    ) -> bool:
        """
        Save plugin result to file.
        
        Args:
            result: VolatilityCommand object
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"Plugin: {result.plugin}\n")
                f.write(f"Memory Image: {result.memory_image}\n")
                f.write(f"Timestamp: {result.timestamp}\n")
                f.write(f"Execution Time: {result.execution_time:.2f}s\n")
                f.write(f"Return Code: {result.returncode}\n")
                f.write(f"\n{'='*80}\n")
                f.write(f"OUTPUT:\n{'='*80}\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"ERRORS:\n{'='*80}\n")
                    f.write(result.stderr)
            
            logger.info(f"Result saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            return False
    
    @staticmethod
    def get_installation_instructions() -> str:
        """Get installation instructions for Volatility 3."""
        return """
Volatility 3 Installation Instructions:

Python Package (Recommended):
1. Install Python 3.7 or higher
2. pip install volatility3

From Source:
1. Clone repository: git clone https://github.com/volatilityfoundation/volatility3.git
2. cd volatility3
3. pip install -r requirements.txt
4. python vol.py -h

Windows Standalone:
1. Download from: https://github.com/volatilityfoundation/volatility3/releases
2. Extract and add to PATH

Verify installation: vol -h
or: python -m volatility3 -h
"""