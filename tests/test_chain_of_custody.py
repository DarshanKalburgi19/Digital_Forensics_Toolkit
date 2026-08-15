"""
Tests for chain of custody module.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from core.chain_of_custody import ChainOfCustody, ChainOfCustodyEntry


class TestChainOfCustody(unittest.TestCase):
    """Test cases for ChainOfCustody."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test case
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_create_chain_of_custody(self):
        """Test creating chain of custody instance."""
        coc = ChainOfCustody(self.test_dir)
        self.assertIsNotNone(coc)
        self.assertEqual(len(coc.entries), 0)
    
    def test_add_entry(self):
        """Test adding chain of custody entry."""
        coc = ChainOfCustody(self.test_dir)
        
        entry = coc.add_entry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Test Investigator",
            action="Evidence Added",
            description="Test evidence added",
            evidence_hash="abc123"
        )
        
        self.assertIsNotNone(entry)
        self.assertEqual(len(coc.entries), 1)
        self.assertEqual(entry.case_id, "TEST-001")
        self.assertEqual(entry.action, "Evidence Added")
    
    def test_add_multiple_entries(self):
        """Test adding multiple entries."""
        coc = ChainOfCustody(self.test_dir)
        
        coc.add_entry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Investigator A",
            action="Evidence Added",
            description="First action"
        )
        
        coc.add_entry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Investigator B",
            action="Integrity Verified",
            description="Second action"
        )
        
        self.assertEqual(len(coc.entries), 2)
    
    def test_get_entries_all(self):
        """Test retrieving all entries."""
        coc = ChainOfCustody(self.test_dir)
        
        coc.add_entry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Test",
            action="Action 1",
            description="Desc 1"
        )
        
        coc.add_entry(
            case_id="TEST-001",
            evidence_id="2",
            investigator="Test",
            action="Action 2",
            description="Desc 2"
        )
        
        entries = coc.get_entries()
        self.assertEqual(len(entries), 2)
    
    def test_get_entries_filtered(self):
        """Test retrieving filtered entries."""
        coc = ChainOfCustody(self.test_dir)
        
        coc.add_entry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Test",
            action="Action 1",
            description="Desc 1"
        )
        
        coc.add_entry(
            case_id="TEST-001",
            evidence_id="2",
            investigator="Test",
            action="Action 2",
            description="Desc 2"
        )
        
        entries = coc.get_entries(evidence_id="1")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].evidence_id, "1")
    
    def test_persistence(self):
        """Test that entries persist to file."""
        # Create and add entry
        coc1 = ChainOfCustody(self.test_dir)
        coc1.add_entry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Test",
            action="Test Action",
            description="Test Description"
        )
        
        # Create new instance and load
        coc2 = ChainOfCustody(self.test_dir)
        self.assertEqual(len(coc2.entries), 1)
        self.assertEqual(coc2.entries[0].action, "Test Action")
    
    def test_export_json(self):
        """Test exporting to JSON."""
        coc = ChainOfCustody(self.test_dir)
        coc.add_entry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Test",
            action="Test Action",
            description="Test Description"
        )
        
        output_path = self.test_dir / "coc_export.json"
        result = coc.export_json(output_path)
        
        self.assertTrue(result)
        self.assertTrue(output_path.exists())
    
    def test_export_csv(self):
        """Test exporting to CSV."""
        coc = ChainOfCustody(self.test_dir)
        coc.add_entry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Test",
            action="Test Action",
            description="Test Description"
        )
        
        output_path = self.test_dir / "coc_export.csv"
        result = coc.export_csv(output_path)
        
        self.assertTrue(result)
        self.assertTrue(output_path.exists())
    
    def test_entry_to_dict(self):
        """Test converting entry to dictionary."""
        entry = ChainOfCustodyEntry(
            case_id="TEST-001",
            evidence_id="1",
            investigator="Test",
            action="Test Action",
            description="Test Description",
            evidence_hash="abc123"
        )
        
        entry_dict = entry.to_dict()
        
        self.assertIn('timestamp', entry_dict)
        self.assertIn('case_id', entry_dict)
        self.assertIn('evidence_id', entry_dict)
        self.assertIn('action', entry_dict)
        self.assertEqual(entry_dict['case_id'], "TEST-001")
        self.assertEqual(entry_dict['evidence_hash'], "abc123")


if __name__ == '__main__':
    unittest.main()