"""
Centralized logging configuration for forensic operations.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_dir: str = "logs",
    level: int = logging.INFO
) -> logging.Logger:
    """
    Configure and return a logger instance.
    
    Args:
        name: Logger name
        log_dir: Directory for log files
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler with date-based filename
    log_file = log_path / f"forensics_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class ForensicLogger:
    """
    Specialized logger for forensic operations with structured logging.
    """
    
    def __init__(self, case_id: Optional[str] = None):
        """
        Initialize forensic logger.
        
        Args:
            case_id: Optional case identifier for context
        """
        self.case_id = case_id
        self.logger = setup_logger(f"forensics.{case_id}" if case_id else "forensics")
    
    def log_evidence_action(
        self,
        action: str,
        evidence_id: str,
        details: str,
        investigator: str
    ) -> None:
        """
        Log an evidence-related action.
        
        Args:
            action: Type of action performed
            evidence_id: Evidence identifier
            details: Action details
            investigator: Person performing action
        """
        self.logger.info(
            f"EVIDENCE ACTION | Case: {self.case_id} | "
            f"Evidence: {evidence_id} | Action: {action} | "
            f"Investigator: {investigator} | Details: {details}"
        )
    
    def log_integrity_check(
        self,
        evidence_id: str,
        result: bool,
        original_hash: str,
        current_hash: str
    ) -> None:
        """
        Log integrity verification result.
        
        Args:
            evidence_id: Evidence identifier
            result: Verification result (True=verified, False=compromised)
            original_hash: Original hash value
            current_hash: Current hash value
        """
        status = "VERIFIED" if result else "COMPROMISED"
        self.logger.warning(
            f"INTEGRITY CHECK | Case: {self.case_id} | "
            f"Evidence: {evidence_id} | Status: {status} | "
            f"Original: {original_hash[:16]}... | Current: {current_hash[:16]}..."
        )
    
    def log_analysis(
        self,
        analysis_type: str,
        target: str,
        status: str,
        details: str = ""
    ) -> None:
        """
        Log analysis operation.
        
        Args:
            analysis_type: Type of analysis
            target: Target file/image/memory
            status: Operation status
            details: Additional details
        """
        self.logger.info(
            f"ANALYSIS | Case: {self.case_id} | Type: {analysis_type} | "
            f"Target: {target} | Status: {status} | Details: {details}"
        )
    
    def log_error(self, operation: str, error: str) -> None:
        """
        Log error during forensic operation.
        
        Args:
            operation: Operation that failed
            error: Error description
        """
        self.logger.error(
            f"ERROR | Case: {self.case_id} | Operation: {operation} | Error: {error}"
        )