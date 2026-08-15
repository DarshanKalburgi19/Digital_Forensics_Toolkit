"""
Autopsy integration and workflow documentation.
"""

from pathlib import Path
from typing import Dict
from core.logger import setup_logger

logger = setup_logger("autopsy")


class AutopsyIntegration:
    """
    Autopsy workflow integration and documentation.
    
    NOTE: Autopsy is a full-featured forensic platform. This module provides
    workflow guidance rather than attempting to recreate Autopsy functionality.
    """
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if Autopsy is installed.
        
        Returns:
            False - this is documentation only
        """
        # Autopsy doesn't expose a reliable CLI interface for automation
        return False
    
    @staticmethod
    def get_workflow_documentation() -> str:
        """
        Get Autopsy workflow documentation.
        
        Returns:
            Workflow documentation string
        """
        return """
================================================================================
AUTOPSY WORKFLOW INTEGRATION
================================================================================

Autopsy is a powerful digital forensics platform that provides comprehensive
analysis capabilities. This toolkit complements Autopsy by handling evidence
collection, hashing, and chain of custody.

RECOMMENDED WORKFLOW:
--------------------

1. EVIDENCE COLLECTION (This Toolkit)
   - Create a forensic case
   - Add evidence files
   - Calculate and verify hashes
   - Maintain chain of custody

2. AUTOPSY ANALYSIS
   - Launch Autopsy
   - Create new case or open existing
   - Add data source (evidence file)
   - Configure ingest modules
   - Run analysis
   - Review results

3. RESULTS INTEGRATION (This Toolkit)
   - Export findings from Autopsy
   - Document findings in case notes
   - Generate comprehensive report including Autopsy results
   - Update chain of custody

AUTOPSY INSTALLATION:
--------------------

Windows:
1. Download from: https://www.autopsy.com/download/
2. Install Windows package
3. Follow setup wizard

Linux:
1. Download from Autopsy website
2. Follow installation instructions for your distribution

USING AUTOPSY WITH THIS TOOLKIT:
--------------------------------

1. Prepare Evidence:
   - Use this toolkit to import and hash evidence
   - Verify integrity
   - Document in chain of custody

2. Analyze in Autopsy:
   - Create Autopsy case
   - Add evidence file (E01, DD, RAW, etc.)
   - Select ingest modules:
     * File Type Identification
     * Extension Mismatch Detection
     * Embedded File Extraction
     * EXIF Parser
     * Hash Lookup
     * Keyword Search
     * Email Parser
     * Registry Analysis (Windows)
     * Web Artifacts
     * Recent Activity
     * etc.

3. Export Results:
   - Generate reports from Autopsy
   - Export tagged items
   - Export timeline
   - Save case files

4. Integrate Results:
   - Import Autopsy findings into case notes
   - Include in final report
   - Update chain of custody with analysis activities

KEY AUTOPSY FEATURES:
--------------------

- Timeline Analysis
- Keyword Search
- Hash Filtering
- Email Analysis
- Registry Analysis
- Web Artifacts
- Deleted File Recovery
- File Type Detection
- EXIF Metadata
- Data Carving
- Multi-user Cases
- Extensible Modules

COMPLEMENTARY USE:
-----------------

This Toolkit:               Autopsy:
- Evidence collection       - Deep forensic analysis
- Hash verification         - Timeline reconstruction
- Chain of custody          - Keyword searching
- Live system collection    - Registry analysis
- Quick analysis            - Comprehensive investigation
- Report generation         - Advanced carving
- Process monitoring        - Email parsing

For detailed Autopsy documentation: https://www.autopsy.com/support/
"""
    
    @staticmethod
    def get_case_export_guide() -> str:
        """Get guide for exporting Autopsy results."""
        return """
EXPORTING AUTOPSY RESULTS FOR REPORT INTEGRATION:
-------------------------------------------------

1. GENERATE AUTOPSY REPORT:
   - Tools → Generate Report
   - Select report type:
     * HTML Report (recommended for integration)
     * Excel Report
     * KML Report
     * Tab-delimited text

2. EXPORT TAGGED ITEMS:
   - Right-click tagged results
   - Select "Export to CSV" or "Export Selected Rows"
   - Save to case directory

3. EXPORT TIMELINE:
   - Tools → Timeline
   - Export timeline events
   - Save as CSV or Excel

4. SAVE CASE:
   - File → Save Case
   - Backup case directory

5. INTEGRATE WITH THIS TOOLKIT:
   - Place Autopsy reports in: cases/<case_id>/artifacts/autopsy/
   - Update case notes with key findings
   - Reference in final report
"""


class FTKImagerIntegration:
    """FTK Imager integration documentation - now in separate module."""
    pass