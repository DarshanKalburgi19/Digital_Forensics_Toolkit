"""
Evidence management system for forensic investigations.
"""

import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from .hashing import HashCalculator
from .chain_of_custody import ChainOfCustody
from .logger import setup_logger

logger = setup_logger("evidence_manager")


class Evidence:
    """
    Represents a piece of forensic evidence.
    """
    
    def __init__(
        self,
        evidence_id: int,
        case_id: str,
        filename: str,
        original_path: str,
        evidence_type: str,
        file_size: int,
        added_date: str,
        added_by: str,
        md5_hash: Optional[str] = None,
        sha1_hash: Optional[str] = None,
        sha256_hash: Optional[str] = None,
        sha512_hash: Optional[str] = None,
        notes: str = ""
    ):
        """Initialize evidence object."""
        self.evidence_id = evidence_id
        self.case_id = case_id
        self.filename = filename
        self.original_path = original_path
        self.evidence_type = evidence_type
        self.file_size = file_size
        self.added_date = added_date
        self.added_by = added_by
        self.md5_hash = md5_hash
        self.sha1_hash = sha1_hash
        self.sha256_hash = sha256_hash
        self.sha512_hash = sha512_hash
        self.notes = notes
    
    def to_dict(self) -> Dict:
        """Convert evidence to dictionary."""
        return {
            'evidence_id': self.evidence_id,
            'case_id': self.case_id,
            'filename': self.filename,
            'original_path': self.original_path,
            'evidence_type': self.evidence_type,
            'file_size': self.file_size,
            'added_date': self.added_date,
            'added_by': self.added_by,
            'md5_hash': self.md5_hash,
            'sha1_hash': self.sha1_hash,
            'sha256_hash': self.sha256_hash,
            'sha512_hash': self.sha512_hash,
            'notes': self.notes
        }


class EvidenceManager:
    """
    Manage forensic evidence with integrity verification.
    """
    
    # Supported evidence file types
    EVIDENCE_TYPES = {
        '.e01': 'EnCase Image',
        '.e02': 'EnCase Image',
        '.001': 'Forensic Image',
        '.raw': 'Raw Disk Image',
        '.dd': 'DD Image',
        '.img': 'Disk Image',
        '.mem': 'Memory Dump',
        '.dmp': 'Memory Dump',
        '.vmem': 'VMware Memory',
        '.bin': 'Binary File',
        '.txt': 'Text File',
        '.log': 'Log File',
        '.pcap': 'Network Capture',
        '.zip': 'Archive',
        '.tar': 'Archive',
        '.gz': 'Archive'
    }
    
    def __init__(self, db_path: Path, cases_dir: Path):
        """
        Initialize evidence manager.
        
        Args:
            db_path: Path to SQLite database
            cases_dir: Base directory for cases
        """
        self.db_path = db_path
        self.cases_dir = cases_dir
        logger.info("Evidence manager initialized")
    
    def add_evidence(
        self,
        case_id: str,
        source_path: str,
        investigator: str,
        notes: str = "",
        copy_file: bool = True
    ) -> Optional[Evidence]:
        """
        Add evidence to a case.
        
        Args:
            case_id: Case identifier
            source_path: Path to evidence file
            investigator: Person adding evidence
            notes: Optional notes
            copy_file: Whether to copy file to case directory
            
        Returns:
            Evidence object or None if failed
        """
        source_path = Path(source_path)
        
        if not source_path.exists():
            logger.error(f"Evidence file not found: {source_path}")
            return None
        
        try:
            # Get file info
            stat = source_path.stat()
            file_size = stat.st_size
            filename = source_path.name
            
            # Determine evidence type
            extension = source_path.suffix.lower()
            evidence_type = self.EVIDENCE_TYPES.get(extension, 'Unknown')
            
            # Calculate hashes
            logger.info(f"Calculating hashes for {filename}...")
            hashes = HashCalculator.hash_file_multiple(source_path)
            
            # Copy evidence to case directory if requested
            evidence_path = source_path
            if copy_file:
                case_evidence_dir = self.cases_dir / case_id / "evidence"
                case_evidence_dir.mkdir(parents=True, exist_ok=True)
                
                destination = case_evidence_dir / filename
                
                # Avoid overwriting - add suffix if needed
                counter = 1
                while destination.exists():
                    stem = source_path.stem
                    destination = case_evidence_dir / f"{stem}_{counter}{extension}"
                    counter += 1
                
                logger.info(f"Copying evidence to {destination}...")
                shutil.copy2(source_path, destination)
                evidence_path = destination
            
            # Insert into database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO evidence (
                    case_id, filename, original_path, evidence_type, file_size,
                    md5_hash, sha1_hash, sha256_hash, sha512_hash,
                    added_date, added_by, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                case_id,
                filename,
                str(source_path.absolute()),
                evidence_type,
                file_size,
                hashes.get('md5'),
                hashes.get('sha1'),
                hashes.get('sha256'),
                hashes.get('sha512'),
                datetime.now().isoformat(),
                investigator,
                notes
            ))
            
            evidence_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            # Create evidence object
            evidence = Evidence(
                evidence_id=evidence_id,
                case_id=case_id,
                filename=filename,
                original_path=str(source_path.absolute()),
                evidence_type=evidence_type,
                file_size=file_size,
                added_date=datetime.now().isoformat(),
                added_by=investigator,
                md5_hash=hashes.get('md5'),
                sha1_hash=hashes.get('sha1'),
                sha256_hash=hashes.get('sha256'),
                sha512_hash=hashes.get('sha512'),
                notes=notes
            )
            
            # Add chain of custody entry
            case_dir = self.cases_dir / case_id
            coc = ChainOfCustody(case_dir)
            coc.add_entry(
                case_id=case_id,
                evidence_id=str(evidence_id),
                investigator=investigator,
                action="Evidence Added",
                description=f"Evidence file '{filename}' added to case",
                evidence_hash=hashes.get('sha256'),
                source=str(source_path.absolute()),
                destination=str(evidence_path.absolute()) if copy_file else None
            )
            
            logger.info(f"Evidence added successfully: {filename} (ID: {evidence_id})")
            return evidence
            
        except Exception as e:
            logger.error(f"Error adding evidence: {str(e)}")
            return None
    
    def get_evidence(self, evidence_id: int) -> Optional[Evidence]:
        """
        Get evidence by ID.
        
        Args:
            evidence_id: Evidence identifier
            
        Returns:
            Evidence object or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM evidence WHERE evidence_id = ?', (evidence_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                row_dict = dict(row)
                return Evidence(**row_dict)
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving evidence: {str(e)}")
            return None
    
    def list_evidence(self, case_id: str) -> List[Evidence]:
        """
        List all evidence for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            List of Evidence objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT * FROM evidence WHERE case_id = ? ORDER BY added_date DESC',
                (case_id,)
            )
            rows = cursor.fetchall()
            conn.close()
            
            return [Evidence(**dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error listing evidence: {str(e)}")
            return []
    
    def verify_integrity(
        self,
        evidence_id: int,
        investigator: str
    ) -> tuple[bool, Optional[str]]:
        """
        Verify evidence integrity by recalculating hash.
        
        Args:
            evidence_id: Evidence identifier
            investigator: Person performing verification
            
        Returns:
            Tuple of (verified: bool, message: str)
        """
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            return False, "Evidence not found"
        
        # Find the evidence file
        case_evidence_dir = self.cases_dir / evidence.case_id / "evidence"
        evidence_file = case_evidence_dir / evidence.filename
        
        # Try original path if not in case directory
        if not evidence_file.exists():
            evidence_file = Path(evidence.original_path)
        
        if not evidence_file.exists():
            return False, f"Evidence file not found: {evidence.filename}"
        
        try:
            # Recalculate SHA-256
            current_hash = HashCalculator.hash_file(evidence_file, 'sha256')
            
            if current_hash is None:
                return False, "Failed to calculate hash"
            
            # Compare with stored hash
            verified = (current_hash.lower() == evidence.sha256_hash.lower())
            
            # Add chain of custody entry
            case_dir = self.cases_dir / evidence.case_id
            coc = ChainOfCustody(case_dir)
            coc.add_entry(
                case_id=evidence.case_id,
                evidence_id=str(evidence_id),
                investigator=investigator,
                action="Integrity Verification",
                description=f"Integrity {'VERIFIED' if verified else 'COMPROMISED'}",
                evidence_hash=current_hash
            )
            
            if verified:
                message = f"Integrity VERIFIED for {evidence.filename}"
                logger.info(message)
            else:
                message = (
                    f"Integrity COMPROMISED for {evidence.filename}\n"
                    f"Original: {evidence.sha256_hash}\n"
                    f"Current:  {current_hash}"
                )
                logger.warning(message)
            
            return verified, message
            
        except Exception as e:
            error_msg = f"Error verifying integrity: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_evidence_path(self, evidence_id: int) -> Optional[Path]:
        """
        Get the file path for evidence.
        
        Args:
            evidence_id: Evidence identifier
            
        Returns:
            Path to evidence file or None
        """
        evidence = self.get_evidence(evidence_id)
        if not evidence:
            return None
        
        # Try case evidence directory first
        case_evidence_dir = self.cases_dir / evidence.case_id / "evidence"
        evidence_file = case_evidence_dir / evidence.filename
        
        if evidence_file.exists():
            return evidence_file
        
        # Try original path
        original_file = Path(evidence.original_path)
        if original_file.exists():
            return original_file
        
        return None