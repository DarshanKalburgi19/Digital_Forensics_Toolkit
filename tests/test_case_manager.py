"""
Tests for case manager module.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from core.case_manager import CaseManager


class TestCaseManager(unittest.TestCase):
    """Test cases for CaseManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directories
        self.test_base_dir = Path(tempfile.mkdtemp())
        self.test_db_dir = Path(tempfile.mkdtemp())
        
        self.case_manager = CaseManager(
            base_dir=str(self.test_base_dir),
            db_dir=str(self.test_db_dir)
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_base_dir.exists():
            shutil.rmtree(self.test_base_dir)
        if self.test_db_dir.exists():
            shutil.rmtree(self.test_db_dir)
    
    def test_create_case(self):
        """Test creating a case."""
        case = self.case_manager.create_case(
            case_id="TEST-001",
            case_name="Test Case",
            investigator="Test Investigator",
            description="Test Description"
        )
        
        self.assertIsNotNone(case)
        self.assertEqual(case.case_id, "TEST-001")
        self.assertEqual(case.case_name, "Test Case")
        self.assertEqual(case.investigator, "Test Investigator")
    
    def test_create_duplicate_case(self):
        """Test that duplicate case IDs are rejected."""
        self.case_manager.create_case(
            case_id="TEST-001",
            case_name="Test Case 1",
            investigator="Investigator"
        )
        
        # Try to create duplicate
        case2 = self.case_manager.create_case(
            case_id="TEST-001",
            case_name="Test Case 2",
            investigator="Investigator"
        )
        
        self.assertIsNone(case2)
    
    def test_get_case(self):
        """Test retrieving a case."""
        self.case_manager.create_case(
            case_id="TEST-002",
            case_name="Test Case",
            investigator="Investigator"
        )
        
        case = self.case_manager.get_case("TEST-002")
        
        self.assertIsNotNone(case)
        self.assertEqual(case.case_id, "TEST-002")
    
    def test_get_nonexistent_case(self):
        """Test retrieving nonexistent case."""
        case = self.case_manager.get_case("NONEXISTENT")
        self.assertIsNone(case)
    
    def test_list_cases(self):
        """Test listing all cases."""
        self.case_manager.create_case(
            case_id="TEST-003",
            case_name="Case 1",
            investigator="Inv 1"
        )
        
        self.case_manager.create_case(
            case_id="TEST-004",
            case_name="Case 2",
            investigator="Inv 2"
        )
        
        cases = self.case_manager.list_cases()
        
        self.assertEqual(len(cases), 2)
    
    def test_update_case_status(self):
        """Test updating case status."""
        self.case_manager.create_case(
            case_id="TEST-005",
            case_name="Test Case",
            investigator="Investigator"
        )
        
        result = self.case_manager.update_case_status("TEST-005", "CLOSED")
        self.assertTrue(result)
        
        case = self.case_manager.get_case("TEST-005")
        self.assertEqual(case.status, "CLOSED")
    
    def test_case_directory_creation(self):
        """Test that case directories are created."""
        self.case_manager.create_case(
            case_id="TEST-006",
            case_name="Test Case",
            investigator="Investigator"
        )
        
        case_dir = self.case_manager.get_case_directory("TEST-006")
        
        self.assertIsNotNone(case_dir)
        self.assertTrue(case_dir.exists())
        self.assertTrue((case_dir / "evidence").exists())
        self.assertTrue((case_dir / "artifacts").exists())
        self.assertTrue((case_dir / "reports").exists())
    
    def test_get_case_stats(self):
        """Test getting case statistics."""
        self.case_manager.create_case(
            case_id="TEST-007",
            case_name="Test Case",
            investigator="Investigator"
        )
        
        stats = self.case_manager.get_case_stats("TEST-007")
        
        self.assertIn('evidence_count', stats)
        self.assertIn('artifact_count', stats)
        self.assertEqual(stats['evidence_count'], 0)


if __name__ == '__main__':
    unittest.main()