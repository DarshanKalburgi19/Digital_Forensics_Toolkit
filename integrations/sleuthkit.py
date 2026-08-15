"""
Sleuth Kit integration for disk forensics.
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from core.logger import setup_logger

logger = setup_logger("sleuthkit")


class SleuthKitCommand:
    """
    Represents a Sleuth Kit command execution result.
    """
    
    def __init__(
        self,
        command: str,
        args: List[str],
        stdout: str,
        stderr: str,
        returncode: int,
        execution_time: float
    ):
        """Initialize command result."""
        self.command = command
        self.args = args
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
            'command': self.command,
            'args': self.args,
            'stdout': self.stdout,
            'stderr': self.stderr,
            'returncode': self.returncode,
            'success': self.success(),
            'execution_time': self.execution_time,
            'timestamp': self.timestamp
        }


class SleuthKitIntegration:
    """
    Integration with The Sleuth Kit for disk forensics.
    
    Provides safe command-line interface to TSK tools.
    """
    
    # Sleuth Kit commands to check
    COMMANDS = {
        'mmls': 'mmls',      # Display partition layout
        'fsstat': 'fsstat',  # Display filesystem details
        'fls': 'fls',        # List files and directories
        'istat': 'istat',    # Display inode details
        'icat': 'icat'       # Output file contents
    }
    
    def __init__(self):
        """Initialize Sleuth Kit integration."""
        self.available_commands = self._check_availability()
        
        if self.available_commands:
            logger.info(f"Sleuth Kit available: {', '.join(self.available_commands.keys())}")
        else:
            logger.warning("Sleuth Kit not detected")
    
    def _check_availability(self) -> Dict[str, str]:
        """
        Check which Sleuth Kit commands are available.
        
        Returns:
            Dictionary of available commands and their paths
        """
        available = {}
        
        for name, cmd in self.COMMANDS.items():
            path = shutil.which(cmd)
            if path:
                available[name] = path
        
        return available
    
    def is_available(self) -> bool:
        """Check if any Sleuth Kit commands are available."""
        return len(self.available_commands) > 0
    
    def run_mmls(self, image_path: Path) -> Optional[SleuthKitCommand]:
        """
        Run mmls to display partition layout.
        
        Args:
            image_path: Path to disk image
            
        Returns:
            SleuthKitCommand object or None
        """
        if 'mmls' not in self.available_commands:
            logger.error("mmls command not available")
            return None
        
        return self._run_command('mmls', [str(image_path)])
    
    def run_fsstat(
        self,
        image_path: Path,
        offset: Optional[int] = None
    ) -> Optional[SleuthKitCommand]:
        """
        Run fsstat to display filesystem details.
        
        Args:
            image_path: Path to disk image
            offset: Byte offset to filesystem (optional)
            
        Returns:
            SleuthKitCommand object or None
        """
        if 'fsstat' not in self.available_commands:
            logger.error("fsstat command not available")
            return None
        
        args = []
        if offset is not None:
            args.extend(['-o', str(offset)])
        args.append(str(image_path))
        
        return self._run_command('fsstat', args)
    
    def run_fls(
        self,
        image_path: Path,
        offset: Optional[int] = None,
        path: str = '/',
        recursive: bool = False
    ) -> Optional[SleuthKitCommand]:
        """
        Run fls to list files and directories.
        
        Args:
            image_path: Path to disk image
            offset: Byte offset to filesystem (optional)
            path: Directory path to list
            recursive: Recursively list directories
            
        Returns:
            SleuthKitCommand object or None
        """
        if 'fls' not in self.available_commands:
            logger.error("fls command not available")
            return None
        
        args = []
        if offset is not None:
            args.extend(['-o', str(offset)])
        if recursive:
            args.append('-r')
        args.append(str(image_path))
        if path != '/':
            args.append(path)
        
        return self._run_command('fls', args)
    
    def run_istat(
        self,
        image_path: Path,
        inode: int,
        offset: Optional[int] = None
    ) -> Optional[SleuthKitCommand]:
        """
        Run istat to display inode details.
        
        Args:
            image_path: Path to disk image
            inode: Inode number
            offset: Byte offset to filesystem (optional)
            
        Returns:
            SleuthKitCommand object or None
        """
        if 'istat' not in self.available_commands:
            logger.error("istat command not available")
            return None
        
        args = []
        if offset is not None:
            args.extend(['-o', str(offset)])
        args.extend([str(image_path), str(inode)])
        
        return self._run_command('istat', args)
    
    def _run_command(
        self,
        command_name: str,
        args: List[str],
        timeout: int = 300
    ) -> Optional[SleuthKitCommand]:
        """
        Execute a Sleuth Kit command safely.
        
        Args:
            command_name: Name of command
            args: Command arguments
            timeout: Command timeout in seconds
            
        Returns:
            SleuthKitCommand object or None
        """
        if command_name not in self.available_commands:
            logger.error(f"Command not available: {command_name}")
            return None
        
        command_path = self.available_commands[command_name]
        full_command = [command_path] + args
        
        try:
            logger.info(f"Executing: {' '.join(full_command)}")
            
            start_time = datetime.now()
            
            result = subprocess.run(
                full_command,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False  # Don't raise exception on non-zero return
            )
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            cmd_result = SleuthKitCommand(
                command=command_name,
                args=args,
                stdout=result.stdout,
                stderr=result.stderr,
                returncode=result.returncode,
                execution_time=execution_time
            )
            
            if cmd_result.success():
                logger.info(f"{command_name} completed successfully")
            else:
                logger.warning(
                    f"{command_name} returned code {result.returncode}: {result.stderr}"
                )
            
            return cmd_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"{command_name} timed out after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error executing {command_name}: {str(e)}")
            return None
    
    def save_result(
        self,
        result: SleuthKitCommand,
        output_path: Path
    ) -> bool:
        """
        Save command result to file.
        
        Args:
            result: SleuthKitCommand object
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            with open(output_path, 'w') as f:
                f.write(f"Command: {result.command}\n")
                f.write(f"Arguments: {' '.join(result.args)}\n")
                f.write(f"Timestamp: {result.timestamp}\n")
                f.write(f"Execution Time: {result.execution_time:.2f}s\n")
                f.write(f"Return Code: {result.returncode}\n")
                f.write(f"\n{'='*80}\n")
                f.write(f"STDOUT:\n{'='*80}\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write(f"\n{'='*80}\n")
                    f.write(f"STDERR:\n{'='*80}\n")
                    f.write(result.stderr)
            
            logger.info(f"Result saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving result: {str(e)}")
            return False
    
    @staticmethod
    def get_installation_instructions() -> str:
        """Get installation instructions for Sleuth Kit."""
        return """
Sleuth Kit Installation Instructions:

Windows:
1. Download Sleuth Kit from: https://www.sleuthkit.org/sleuthkit/download.php
2. Install the Windows package
3. Add installation directory to PATH environment variable
   (e.g., C:\\Program Files\\sleuthkit\\bin)
4. Restart the application

Linux:
1. Ubuntu/Debian: sudo apt-get install sleuthkit
2. Fedora/RHEL: sudo yum install sleuthkit
3. From source: https://github.com/sleuthkit/sleuthkit

macOS:
1. Using Homebrew: brew install sleuthkit

Verify installation by running: mmls -V
"""