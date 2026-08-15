"""
FTK Imager integration and workflow documentation.
"""

from core.logger import setup_logger

logger = setup_logger("ftk_imager")


class FTKImagerIntegration:
    """
    FTK Imager workflow integration and documentation.
    
    NOTE: FTK Imager is primarily a GUI tool for evidence acquisition.
    This module provides workflow guidance.
    """
    
    @staticmethod
    def is_available() -> bool:
        """
        Check if FTK Imager is installed.
        
        Returns:
            False - this is documentation only
        """
        # FTK Imager doesn't expose a reliable cross-platform CLI
        return False
    
    @staticmethod
    def get_workflow_documentation() -> str:
        """
        Get FTK Imager workflow documentation.
        
        Returns:
            Workflow documentation string
        """
        return """
================================================================================
FTK IMAGER WORKFLOW INTEGRATION
================================================================================

FTK Imager is an industry-standard tool for creating forensic images of
storage media. Use it to acquire evidence, then import into this toolkit.

FTK IMAGER INSTALLATION:
-----------------------

Windows:
1. Download from: https://www.exterro.com/ftk-imager
2. Install (free tool, no license required)
3. Run as Administrator for physical disk access

EVIDENCE ACQUISITION WORKFLOW:
-----------------------------

1. PREPARE FOR ACQUISITION:
   - Connect storage device (write-blocker recommended)
   - Launch FTK Imager as Administrator
   - Document device information

2. CREATE FORENSIC IMAGE:
   - File → Create Disk Image
   - Select source type:
     * Physical Drive (entire disk)
     * Logical Drive (partition)
     * Image File (convert existing image)
     * Contents of a Folder
   
3. SELECT IMAGE FORMAT:
   - E01 (Expert Witness / EnCase) - RECOMMENDED
     * Supports compression
     * Includes metadata
     * Industry standard
   - Raw (dd)
     * No compression
     * Universal compatibility
   - SMART
   - AFF

4. CONFIGURE IMAGE OPTIONS:
   - Case Number
   - Evidence Number
   - Unique Description
   - Examiner Name
   - Notes
   - Compression level (E01)
   - Fragment size (if needed)

5. VERIFY IMAGE:
   - Enable "Verify images after creation"
   - FTK Imager will calculate hashes
   - Document hash values

6. IMPORT TO TOOLKIT:
   - Launch Digital Forensics Toolkit
   - Create or open case
   - Add Evidence → Select created image file
   - Toolkit will:
     * Calculate hashes
     * Verify integrity
     * Add to chain of custody

BEST PRACTICES:
--------------

1. WRITE PROTECTION:
   - Use hardware write blocker when possible
   - For USB: Enable write protection
   - Document write protection method

2. DOCUMENTATION:
   - Photograph device and connections
   - Record device serial numbers
   - Note date, time, location
   - Document chain of custody

3. VERIFICATION:
   - Always verify images after creation
   - Compare hash values
   - Test image before removing original

4. STORAGE:
   - Store images on dedicated forensic drive
   - Maintain multiple copies
   - Secure storage location

5. METADATA:
   - Fill all case information fields
   - Include detailed notes
   - Record acquisition parameters

COMMON TASKS:
------------

PHYSICAL DRIVE IMAGING:
1. File → Create Disk Image
2. Physical Drive → Select drive
3. Add destination → E01 format
4. Fill case information
5. Start imaging
6. Verify hashes

LOGICAL DRIVE IMAGING:
1. File → Create Disk Image
2. Logical Drive → Select partition
3. Configure as above

MEMORY CAPTURE:
1. File → Capture Memory
2. Select destination folder
3. Include pagefile if available
4. Capture and verify

FILE/FOLDER IMAGING:
1. File → Create Disk Image
2. Contents of a Folder
3. Browse to folder
4. Create image

INTEGRATION WITH THIS TOOLKIT:
-----------------------------

After creating image with FTK Imager:

1. In This Toolkit:
   - Create case
   - Add evidence (select FTK image)
   - Verify hash matches FTK hash
   - Document in chain of custody

2. Analysis Options:
   - Use Sleuth Kit integration for disk analysis
   - Use Autopsy for comprehensive analysis
   - Use file analysis for specific artifacts

3. Reporting:
   - Generate report including:
     * FTK acquisition details
     * Hash verification
     * Analysis results

SUPPORTED FORMATS:
-----------------

FTK Imager can create:
- E01 (EnCase)
- Ex01 (EnCase v7+)
- Raw (dd)
- SMART
- AFF

This Toolkit can analyze:
- E01, E02 (via Sleuth Kit)
- Raw, DD
- Other formats supported by Sleuth Kit

For detailed FTK Imager documentation:
https://www.exterro.com/digital-forensics-software/ftk-imager
"""
    
    @staticmethod
    def get_hash_verification_guide() -> str:
        """Get guide for hash verification workflow."""
        return """
HASH VERIFICATION WORKFLOW:
--------------------------

1. FTK IMAGER CREATES IMAGE:
   - Calculates MD5 and SHA1 during creation
   - Stores hashes in image metadata (E01)
   - Displays in verification report

2. IMPORT TO TOOLKIT:
   - Toolkit calculates SHA256, MD5, SHA1, SHA512
   - Compares MD5 with FTK value
   - Documents match in chain of custody

3. VERIFICATION POINTS:
   - Original acquisition (FTK Imager)
   - Import to toolkit
   - Before each analysis
   - Regular integrity checks

4. DOCUMENTATION:
   - Record all hash values
   - Note any discrepancies immediately
   - Maintain in chain of custody
   - Include in final report
"""