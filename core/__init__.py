"""
Core forensics modules for case management, evidence handling, and integrity verification.
"""

from .case_manager import CaseManager
from .evidence_manager import EvidenceManager
from .hashing import HashCalculator
from .chain_of_custody import ChainOfCustody
from .logger import setup_logger

__all__ = [
    'CaseManager',
    'EvidenceManager',
    'HashCalculator',
    'ChainOfCustody',
    'setup_logger'
]