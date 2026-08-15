"""
Chain of custody management for forensic evidence.
Educational implementation for tracking evidence handling.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from .logger import setup_logger

logger = setup_logger("chain_of_custody")


class ChainOfCustodyEntry:
    """
    Single entry in the chain of custody log.
    """
    
    def __init__(
        self,
        case_id: str,
        evidence_id: str,
        investigator: str,
        action: str,
        description: str,
        evidence_hash: Optional[str] = None,
        source: Optional[str] = None,
        destination: Optional[str] = None
    ):
        """
        Initialize chain of custody entry.
        
        Args:
            case_id: Case identifier
            evidence_id: Evidence identifier
            investigator: Person handling evidence
            action: Action performed
            description: Detailed description
            evidence_hash: Current hash of evidence
            source: Source location
            destination: Destination location
        """
        self.timestamp = datetime.now().isoformat()
        self.case_id = case_id
        self.evidence_id = evidence_id
        self.investigator = investigator
        self.action = action
        self.description = description
        self.evidence_hash = evidence_hash
        self.source = source
        self.destination = destination
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary."""
        return {
            'timestamp': self.timestamp,
            'case_id': self.case_id,
            'evidence_id': self.evidence_id,
            'investigator': self.investigator,
            'action': self.action,
            'description': self.description,
            'evidence_hash': self.evidence_hash,
            'source': self.source,
            'destination': self.destination
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ChainOfCustodyEntry':
        """Create entry from dictionary."""
        entry = cls(
            case_id=data['case_id'],
            evidence_id=data['evidence_id'],
            investigator=data['investigator'],
            action=data['action'],
            description=data['description'],
            evidence_hash=data.get('evidence_hash'),
            source=data.get('source'),
            destination=data.get('destination')
        )
        entry.timestamp = data['timestamp']
        return entry


class ChainOfCustody:
    """
    Manage chain of custody for forensic evidence.
    
    NOTE: This is an educational implementation. In real forensic investigations,
    legal chain of custody requires additional procedures, physical signatures,
    secure storage, and may need to meet specific legal standards.
    """
    
    def __init__(self, case_dir: Path):
        """
        Initialize chain of custody manager.
        
        Args:
            case_dir: Case directory path
        """
        self.case_dir = Path(case_dir)
        self.coc_file = self.case_dir / "chain_of_custody.json"
        self.entries: List[ChainOfCustodyEntry] = []
        
        # Load existing entries
        self._load()
    
    def add_entry(
        self,
        case_id: str,
        evidence_id: str,
        investigator: str,
        action: str,
        description: str,
        evidence_hash: Optional[str] = None,
        source: Optional[str] = None,
        destination: Optional[str] = None
    ) -> ChainOfCustodyEntry:
        """
        Add new chain of custody entry.
        
        Args:
            case_id: Case identifier
            evidence_id: Evidence identifier
            investigator: Person handling evidence
            action: Action performed
            description: Detailed description
            evidence_hash: Current hash of evidence
            source: Source location
            destination: Destination location
            
        Returns:
            Created entry
        """
        entry = ChainOfCustodyEntry(
            case_id=case_id,
            evidence_id=evidence_id,
            investigator=investigator,
            action=action,
            description=description,
            evidence_hash=evidence_hash,
            source=source,
            destination=destination
        )
        
        self.entries.append(entry)
        self._save()
        
        logger.info(
            f"Chain of custody entry added: {action} on {evidence_id} by {investigator}"
        )
        
        return entry
    
    def get_entries(
        self,
        evidence_id: Optional[str] = None
    ) -> List[ChainOfCustodyEntry]:
        """
        Get chain of custody entries.
        
        Args:
            evidence_id: Filter by evidence ID (optional)
            
        Returns:
            List of entries
        """
        if evidence_id:
            return [e for e in self.entries if e.evidence_id == evidence_id]
        return self.entries
    
    def export_json(self, output_path: Path) -> bool:
        """
        Export chain of custody to JSON file.
        
        Args:
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            data = {
                'export_date': datetime.now().isoformat(),
                'case_dir': str(self.case_dir),
                'total_entries': len(self.entries),
                'entries': [entry.to_dict() for entry in self.entries]
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Chain of custody exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting chain of custody: {str(e)}")
            return False
    
    def export_csv(self, output_path: Path) -> bool:
        """
        Export chain of custody to CSV file.
        
        Args:
            output_path: Output file path
            
        Returns:
            True if successful
        """
        import csv
        
        try:
            with open(output_path, 'w', newline='') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Timestamp',
                    'Case ID',
                    'Evidence ID',
                    'Investigator',
                    'Action',
                    'Description',
                    'Evidence Hash',
                    'Source',
                    'Destination'
                ])
                
                # Entries
                for entry in self.entries:
                    writer.writerow([
                        entry.timestamp,
                        entry.case_id,
                        entry.evidence_id,
                        entry.investigator,
                        entry.action,
                        entry.description,
                        entry.evidence_hash or '',
                        entry.source or '',
                        entry.destination or ''
                    ])
            
            logger.info(f"Chain of custody exported to CSV: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting chain of custody to CSV: {str(e)}")
            return False
    
    def _load(self) -> None:
        """Load chain of custody from file."""
        if not self.coc_file.exists():
            return
        
        try:
            with open(self.coc_file, 'r') as f:
                data = json.load(f)
                self.entries = [
                    ChainOfCustodyEntry.from_dict(entry_data)
                    for entry_data in data.get('entries', [])
                ]
            logger.info(f"Loaded {len(self.entries)} chain of custody entries")
            
        except Exception as e:
            logger.error(f"Error loading chain of custody: {str(e)}")
            self.entries = []
    
    def _save(self) -> None:
        """Save chain of custody to file."""
        try:
            # Ensure directory exists
            self.case_dir.mkdir(parents=True, exist_ok=True)
            
            data = {
                'last_updated': datetime.now().isoformat(),
                'total_entries': len(self.entries),
                'entries': [entry.to_dict() for entry in self.entries]
            }
            
            with open(self.coc_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving chain of custody: {str(e)}")