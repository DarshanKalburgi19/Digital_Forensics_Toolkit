# Digital Forensics Toolkit

A comprehensive educational digital forensics platform for case management, evidence handling, disk forensics, memory forensics, and report generation.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.12%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎯 Overview

This toolkit provides a unified interface for common forensic investigation tasks including:

- **Case Management**: Create and organize forensic investigations
- **Evidence Handling**: Import, hash, and verify forensic evidence
- **Chain of Custody**: Maintain detailed audit trails
- **Live Collection**: Gather system, process, and network information
- **Disk Forensics**: Analyze disk images using Sleuth Kit integration
- **Memory Forensics**: Analyze memory dumps using Volatility 3 integration
- **Browser Artifacts**: Extract browsing history (metadata only)
- **Report Generation**: Create professional PDF investigation reports

## ⚠️ Important Disclaimers

**Educational Purpose**: This toolkit is designed for cybersecurity education and training. It is NOT a replacement for certified commercial forensic tools.

**Legal Compliance**: For production forensic investigations:
- Use certified forensic tools (EnCase, FTK, X-Ways, etc.)
- Follow proper legal procedures
- Maintain proper chain of custody per legal requirements
- Consult with legal counsel

**Security**: 
- Only analyze evidence files and your own test systems
- Never execute suspicious files from evidence
- Do not use on production systems without authorization

## 🚀 Features

### Core Capabilities

✅ **Case Management**
- Create forensic cases with full metadata
- Organize evidence and artifacts
- Track case status and timeline

✅ **Evidence Management**
- Support for multiple forensic image formats (E01, DD, RAW, etc.)
- Multi-algorithm hashing (MD5, SHA-1, SHA-256, SHA-512)
- Integrity verification
- Automatic evidence cataloging

✅ **Chain of Custody**
- Immutable-style audit logging
- Complete evidence handling history
- Export to JSON/CSV for documentation

✅ **Live System Collection**
- System information (OS, hardware, network)
- Running processes with suspicious indicators
- Network connections and interfaces
- All collection clearly marked as "LIVE"

✅ **File Analysis**
- Metadata extraction
- File type identification
- Cryptographic hashing
- Timestamp analysis

✅ **Browser Artifacts**
- Chrome history extraction
- Edge history extraction
- Firefox history extraction
- **Does NOT extract credentials** (security-focused)

✅ **Disk Forensics** (Sleuth Kit Integration)
- Partition analysis (mmls)
- Filesystem details (fsstat)
- File listing (fls)
- Inode analysis (istat)

✅ **Memory Forensics** (Volatility 3 Integration)
- windows.info - System information
- windows.pslist - Process listing
- windows.pstree - Process tree
- windows.netstat - Network connections
- windows.cmdline - Command lines
- windows.dlllist - DLL analysis

✅ **Professional Reporting**
- Comprehensive PDF reports
- Case information and evidence inventory
- Chain of custody documentation
- Analysis results integration
- Investigator findings section

### Tool Integration

| Tool | Status | Purpose |
|------|--------|---------|
| **Sleuth Kit** | Integrated | Disk forensics analysis |
| **Volatility 3** | Integrated | Memory dump analysis |
| **Autopsy** | Workflow Guide | Full forensic platform |
| **FTK Imager** | Workflow Guide | Evidence acquisition |

## 📋 Requirements

### Mandatory

- Python 3.12 or higher
- Windows, Linux, or macOS

### Python Dependencies


### Optional External Tools

- **Sleuth Kit** - For disk forensics
- **Volatility 3** - For memory forensics
- **Autopsy** - For comprehensive analysis (GUI)
- **FTK Imager** - For evidence acquisition (GUI)

## 🔧 Installation

### 1. Clone Repository

```bash
git clone https://github.com/DarshanKalburgi19/Digital_Forensics_Toolkit.git
cd Digital-Forensics-Toolkit

# pip install -r requirements.txt

#For windows 
# 1. Download from: https://www.sleuthkit.org/sleuthkit/download.php
# 2. Install and add to PATH
# 3. Verify: mmls -V

# For Linux 

# sudo apt-get install sleuthkit

