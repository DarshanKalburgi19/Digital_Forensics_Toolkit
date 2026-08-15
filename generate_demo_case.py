"""
Generate demo forensic case with synthetic evidence.

This script creates a demonstration case with safe, synthetic data
for testing and demonstration purposes.
"""

import json
from pathlib import Path
from datetime import datetime
import random

def create_demo_evidence_directory():
    """Create demo evidence directory with synthetic files."""
    demo_dir = Path("demo_evidence")
    demo_dir.mkdir(exist_ok=True)
    
    print("Creating demo evidence files...")
    
    # 1. Sample document
    sample_doc = demo_dir / "sample_document.txt"
    with open(sample_doc, 'w') as f:
        f.write("""CONFIDENTIAL INTERNAL MEMO

Date: 2024-01-15
From: IT Security Team
To: Management
Subject: Security Audit Findings

This is a sample document for forensic analysis demonstration.

The following findings were identified during our security audit:

1. Unauthorized software installations detected
2. Multiple failed login attempts from external IP addresses
3. Suspicious network traffic patterns observed
4. Missing security patches on critical systems

Recommendation: Immediate investigation required.

This is synthetic data for educational purposes only.
""")
    
    # 2. Suspicious script
    suspicious_script = demo_dir / "suspicious_script.txt"
    with open(suspicious_script, 'w') as f:
        f.write("""# Sample Script (HARMLESS - FOR DEMONSTRATION ONLY)
# This is NOT actual malware

echo "This is a demonstration script"
echo "Simulating suspicious activity logging"

# Fake commands that might appear suspicious:
# whoami
# net user
# ipconfig /all
# netstat -ano

echo "Educational demonstration complete"
# NO ACTUAL MALICIOUS CODE IS PRESENT
""")
    
    # 3. Browser history sample (CSV format)
    browser_history = demo_dir / "browser_history_sample.csv"
    with open(browser_history, 'w') as f:
        f.write("URL,Title,Visit Time,Visit Count\n")
        urls = [
            ("https://www.google.com", "Google", "2024-01-15 10:30:00", 5),
            ("https://github.com", "GitHub", "2024-01-15 11:15:00", 3),
            ("https://stackoverflow.com", "Stack Overflow", "2024-01-15 11:45:00", 8),
            ("https://pastebin.com/suspicious", "Suspicious Paste", "2024-01-15 14:20:00", 1),
            ("https://temp-mail.org", "Temporary Email", "2024-01-15 14:25:00", 2),
        ]
        for url, title, time, count in urls:
            f.write(f"{url},{title},{time},{count}\n")
    
    # 4. System artifacts JSON
    system_artifacts = demo_dir / "system_artifacts.json"
    artifacts = {
        "collection_time": datetime.now().isoformat(),
        "suspicious_processes": [
            {
                "pid": 1234,
                "name": "unknown_process.exe",
                "path": "C:\\Users\\Public\\Temp\\unknown_process.exe",
                "indicators": ["Running from temporary directory", "No digital signature"]
            },
            {
                "pid": 5678,
                "name": "svchost.exe",
                "path": "C:\\Windows\\Temp\\svchost.exe",
                "indicators": ["Unusual svchost location"]
            }
        ],
        "network_connections": [
            {
                "local": "192.168.1.100:49152",
                "remote": "203.0.113.50:443",
                "state": "ESTABLISHED",
                "process": "unknown_process.exe"
            }
        ],
        "note": "This is synthetic data for demonstration purposes"
    }
    
    with open(system_artifacts, 'w') as f:
        json.dump(artifacts, f, indent=2)
    
    # 5. Sample log file
    log_file = demo_dir / "security_events.log"
    with open(log_file, 'w') as f:
        f.write("2024-01-15 08:00:01 [INFO] System boot completed\n")
        f.write("2024-01-15 10:15:23 [WARNING] Failed login attempt from 203.0.113.25\n")
        f.write("2024-01-15 10:15:45 [WARNING] Failed login attempt from 203.0.113.25\n")
        f.write("2024-01-15 10:16:12 [WARNING] Failed login attempt from 203.0.113.25\n")
        f.write("2024-01-15 10:20:00 [INFO] Successful login: admin user\n")
        f.write("2024-01-15 14:30:15 [WARNING] Unauthorized software installation detected\n")
        f.write("2024-01-15 14:35:00 [CRITICAL] Suspicious outbound connection blocked\n")
        f.write("2024-01-15 16:00:00 [INFO] Security scan initiated\n")
    
    # 6. README for demo evidence
    readme = demo_dir / "README.txt"
    with open(readme, 'w') as f:
        f.write("""DEMO EVIDENCE FILES - README

This directory contains SYNTHETIC evidence files for demonstration purposes.

Files included:
1. sample_document.txt - Sample internal memo
2. suspicious_script.txt - Harmless script file
3. browser_history_sample.csv - Sample browser history
4. system_artifacts.json - Sample system artifacts
5. security_events.log - Sample security log

IMPORTANT:
- All data is FICTIONAL and created for educational purposes
- No real credentials, malware, or sensitive data is included
- Safe to use for testing and demonstration
- Do NOT use for actual forensic investigations

Created: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
""")
    
    print(f"\nDemo evidence created in: {demo_dir.absolute()}")
    print("\nFiles created:")
    for file in demo_dir.iterdir():
        print(f"  - {file.name}")
    
    return demo_dir


def create_demo_case_instructions():
    """Create instructions for using demo case."""
    instructions = """
DEMO CASE SETUP INSTRUCTIONS
=============================

Follow these steps to create and analyze the demo case:

1. LAUNCH APPLICATION:
   python app.py

2. CREATE DEMO CASE:
   - Click "Create New Case"
   - Case ID: DEMO-2024-001
   - Case Name: Demonstration Investigation
   - Investigator: Your Name
   - Description: Educational demonstration of forensic toolkit

3. ADD EVIDENCE:
   - Click "Add Evidence" tab
   - Add files from demo_evidence/ directory:
     * sample_document.txt
     * suspicious_script.txt
     * browser_history_sample.csv
     * system_artifacts.json
     * security_events.log

4. VERIFY INTEGRITY:
   - Select each evidence item
   - Click "Verify Integrity"
   - Observe hash verification

5. PERFORM ANALYSIS:
   - Go to Analysis tab
   - Collect system information (live collection)
   - Collect process information
   - Analyze individual files

6. VIEW CHAIN OF CUSTODY:
   - Click "View Chain of Custody"
   - Observe all evidence handling actions
   - Export to JSON or CSV

7. GENERATE REPORT:
   - Go to Reports tab
   - Select report sections
   - Add your findings
   - Generate PDF report

DEMONSTRATION SCENARIOS:
-----------------------

Scenario 1: Basic Evidence Handling
- Add evidence
- Calculate hashes
- Verify integrity
- Review chain of custody

Scenario 2: File Analysis
- Analyze sample_document.txt
- Review metadata and hashes
- Document findings

Scenario 3: Artifact Review
- Review system_artifacts.json
- Identify suspicious indicators
- Document in report

Scenario 4: Complete Investigation
- Perform all analysis steps
- Document findings
- Generate comprehensive report

SCREENSHOTS FOR DOCUMENTATION:
-----------------------------
Recommended screenshots to capture:
1. Case creation dialog
2. Evidence inventory
3. Integrity verification result
4. Chain of custody view
5. File analysis results
6. System information collection
7. Report generation options
8. Generated PDF report

"""
    
    instructions_file = Path("DEMO_INSTRUCTIONS.txt")
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"\nInstructions created: {instructions_file.absolute()}")


def main():
    """Main demo generation function."""
    print("=" * 60)
    print("DIGITAL FORENSICS TOOLKIT - DEMO GENERATOR")
    print("=" * 60)
    print()
    
    # Create demo evidence
    demo_dir = create_demo_evidence_directory()
    
    # Create instructions
    create_demo_case_instructions()
    
    print("\n" + "=" * 60)
    print("DEMO SETUP COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Read DEMO_INSTRUCTIONS.txt")
    print("2. Run: python app.py")
    print("3. Follow the demo instructions")
    print("\nAll demo files are safe, synthetic, and for educational use only.")
    print()


if __name__ == "__main__":
    main()