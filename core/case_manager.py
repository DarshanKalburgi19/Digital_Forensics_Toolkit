"""
Case management system for forensic investigations.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
from .logger import setup_logger

logger = setup_logger("case_manager")


class ForensicCase:
    """
    Represents a forensic investigation case.
    """
    
    def __init__(
        self,
        case_id: str,
        case_name: str,
        investigator: str,
        description: str = "",
        status: str = "ACTIVE"
    ):
        """
        Initialize forensic case.
        
        Args:
            case_id: Unique case identifier
            case_name: Case name
            investigator: Lead investigator
            description: Case description
            status: Case status (ACTIVE, CLOSED, etc.)
        """
        self.case_id = case_id
        self.case_name = case_name
        self.investigator = investigator
        self.description = description
        self.status = status
        self.created_date = datetime.now().isoformat()
        self.modified_date = self.created_date
    
    def to_dict(self) -> Dict:
        """Convert case to dictionary."""
        return {
            'case_id': self.case_id,
            'case_name': self.case_name,
            'investigator': self.investigator,
            'description': self.description,
            'status': self.status,
            'created_date': self.created_date,
            'modified_date': self.modified_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ForensicCase':
        """Create case from dictionary."""
        case = cls(
            case_id=data['case_id'],
            case_name=data['case_name'],
            investigator=data['investigator'],
            description=data.get('description', ''),
            status=data.get('status', 'ACTIVE')
        )
        case.created_date = data.get('created_date', case.created_date)
        case.modified_date = data.get('modified_date', case.modified_date)
        return case


class CaseManager:
    """
    Manage forensic investigation cases.
    """
    
    def __init__(self, base_dir: str = "cases", db_dir: str = "database"):
        """
        Initialize case manager.
        
        Args:
            base_dir: Base directory for case storage
            db_dir: Directory for database files
        """
        self.base_dir = Path(base_dir)
        self.db_dir = Path(db_dir)
        
        # Create directories
        self.base_dir.mkdir(exist_ok=True)
        self.db_dir.mkdir(exist_ok=True)
        
        # Database path
        self.db_path = self.db_dir / "forensic.db"
        
        # Initialize database
        self._init_database()
        
        logger.info("Case manager initialized")
    
    def _init_database(self) -> None:
        """Initialize SQLite database with required tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    case_name TEXT NOT NULL,
                    investigator TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'ACTIVE',
                    created_date TEXT NOT NULL,
                    modified_date TEXT NOT NULL
                )
            ''')
            
            # Evidence table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    original_path TEXT,
                    evidence_type TEXT,
                    file_size INTEGER,
                    md5_hash TEXT,
                    sha1_hash TEXT,
                    sha256_hash TEXT,
                    sha512_hash TEXT,
                    added_date TEXT NOT NULL,
                    added_by TEXT NOT NULL,
                    notes TEXT,
                    FOREIGN KEY (case_id) REFERENCES cases (case_id)
                )
            ''')
            
            # Artifacts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT NOT NULL,
                    evidence_id INTEGER,
                    artifact_type TEXT NOT NULL,
                    artifact_name TEXT NOT NULL,
                    artifact_path TEXT,
                    description TEXT,
                    extracted_date TEXT NOT NULL,
                    metadata TEXT,
                    FOREIGN KEY (case_id) REFERENCES cases (case_id),
                    FOREIGN KEY (evidence_id) REFERENCES evidence (evidence_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def create_case(
        self,
        case_id: str,
        case_name: str,
        investigator: str,
        description: str = ""
    ) -> Optional[ForensicCase]:
        """
        Create a new forensic case.
        
        Args:
            case_id: Unique case identifier
            case_name: Case name
            investigator: Lead investigator
            description: Case description
            
        Returns:
            ForensicCase object or None if creation failed
        """
        # Validate case_id doesn't already exist
        if self.get_case(case_id):
            logger.error(f"Case ID already exists: {case_id}")
            return None
        
        try:
            # Create case object
            case = ForensicCase(
                case_id=case_id,
                case_name=case_name,
                investigator=investigator,
                description=description
            )
            
            # Create case directory structure
            case_dir = self.base_dir / case_id
            case_dir.mkdir(exist_ok=True)
            
            (case_dir / "evidence").mkdir(exist_ok=True)
            (case_dir / "hashes").mkdir(exist_ok=True)
            (case_dir / "artifacts").mkdir(exist_ok=True)
            (case_dir / "reports").mkdir(exist_ok=True)
            (case_dir / "logs").mkdir(exist_ok=True)
            (case_dir / "artifacts" / "memory").mkdir(exist_ok=True)
            (case_dir / "artifacts" / "disk").mkdir(exist_ok=True)
            (case_dir / "artifacts" / "browser").mkdir(exist_ok=True)
            (case_dir / "artifacts" / "system").mkdir(exist_ok=True)
            
            # Save case metadata to JSON
            case_metadata_file = case_dir / "case_metadata.json"
            with open(case_metadata_file, 'w') as f:
                json.dump(case.to_dict(), f, indent=2)
            
            # Insert into database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO cases (case_id, case_name, investigator, description, status, created_date, modified_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                case.case_id,
                case.case_name,
                case.investigator,
                case.description,
                case.status,
                case.created_date,
                case.modified_date
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Case created successfully: {case_id}")
            return case
            
        except Exception as e:
            logger.error(f"Error creating case: {str(e)}")
            return None
    
    def get_case(self, case_id: str) -> Optional[ForensicCase]:
        """
        Retrieve a case by ID.
        
        Args:
            case_id: Case identifier
            
        Returns:
            ForensicCase object or None if not found
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM cases WHERE case_id = ?', (case_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return ForensicCase.from_dict(dict(row))
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving case: {str(e)}")
            return None
    
    def list_cases(self) -> List[ForensicCase]:
        """
        List all cases.
        
        Returns:
            List of ForensicCase objects
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM cases ORDER BY created_date DESC')
            rows = cursor.fetchall()
            conn.close()
            
            return [ForensicCase.from_dict(dict(row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Error listing cases: {str(e)}")
            return []
    
    def update_case_status(self, case_id: str, status: str) -> bool:
        """
        Update case status.
        
        Args:
            case_id: Case identifier
            status: New status
            
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE cases 
                SET status = ?, modified_date = ?
                WHERE case_id = ?
            ''', (status, datetime.now().isoformat(), case_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Case {case_id} status updated to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating case status: {str(e)}")
            return False
    
    def get_case_directory(self, case_id: str) -> Optional[Path]:
        """
        Get the directory path for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Path object or None if case doesn't exist
        """
        case_dir = self.base_dir / case_id
        if case_dir.exists():
            return case_dir
        return None
    
    def get_case_stats(self, case_id: str) -> Dict:
        """
        Get statistics for a case.
        
        Args:
            case_id: Case identifier
            
        Returns:
            Dictionary with case statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count evidence
            cursor.execute('SELECT COUNT(*) FROM evidence WHERE case_id = ?', (case_id,))
            evidence_count = cursor.fetchone()[0]
            
            # Count artifacts
            cursor.execute('SELECT COUNT(*) FROM artifacts WHERE case_id = ?', (case_id,))
            artifact_count = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'evidence_count': evidence_count,
                'artifact_count': artifact_count
            }
            
        except Exception as e:
            logger.error(f"Error getting case stats: {str(e)}")
            return {
                'evidence_count': 0,
                'artifact_count': 0
            }