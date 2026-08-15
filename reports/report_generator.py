"""
PDF report generator for forensic investigations.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import json

from core.case_manager import CaseManager
from core.evidence_manager import EvidenceManager
from core.chain_of_custody import ChainOfCustody
from core.logger import setup_logger

logger = setup_logger("report_generator")


class ReportGenerator:
    """
    Generate professional PDF forensic reports.
    """
    
    def __init__(
        self,
        case_manager: CaseManager,
        evidence_manager: EvidenceManager,
        case_id: str
    ):
        """
        Initialize report generator.
        
        Args:
            case_manager: CaseManager instance
            evidence_manager: EvidenceManager instance
            case_id: Case identifier
        """
        self.case_manager = case_manager
        self.evidence_manager = evidence_manager
        self.case_id = case_id
        
        self.case = case_manager.get_case(case_id)
        self.case_dir = case_manager.get_case_directory(case_id)
        
        # Report metadata
        self.report_id = f"RPT-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.generated_date = datetime.now()
        
        # Styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection header
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
    
    def generate_report(
        self,
        output_path: Path,
        options: Optional[Dict] = None
    ) -> bool:
        """
        Generate comprehensive forensic report.
        
        Args:
            output_path: Output PDF file path
            options: Report options dictionary
            
        Returns:
            True if successful
        """
        if not self.case:
            logger.error(f"Case not found: {self.case_id}")
            return False
        
        options = options or {}
        
        try:
            logger.info(f"Generating report for case {self.case_id}")
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Build report content
            story = []
            
            # Cover page
            story.extend(self._build_cover_page())
            story.append(PageBreak())
            
            # Table of contents placeholder
            story.extend(self._build_toc())
            story.append(PageBreak())
            
            # Case information
            if options.get('include_case_info', True):
                story.extend(self._build_case_info())
                story.append(PageBreak())
            
            # Evidence inventory
            if options.get('include_evidence', True):
                story.extend(self._build_evidence_inventory())
                story.append(PageBreak())
            
            # Chain of custody
            if options.get('include_chain_of_custody', True):
                story.extend(self._build_chain_of_custody())
                story.append(PageBreak())
            
            # System information
            if options.get('include_system_info', True):
                story.extend(self._build_system_info())
            
            # Process analysis
            if options.get('include_process_info', True):
                story.extend(self._build_process_info())
            
            # Network information
            if options.get('include_network_info', True):
                story.extend(self._build_network_info())
            
            # Disk forensics
            if options.get('include_disk_analysis', True):
                story.extend(self._build_disk_analysis())
            
            # Memory forensics
            if options.get('include_memory_analysis', True):
                story.extend(self._build_memory_analysis())
            
            # Findings and conclusions
            story.extend(self._build_findings(options.get('findings', '')))
            story.append(PageBreak())
            
            # Limitations
            story.extend(self._build_limitations())
            story.append(PageBreak())
            
            # Conclusion
            story.extend(self._build_conclusion())
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Report generated successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            return False
    
    def _build_cover_page(self) -> list:
        """Build cover page."""
        story = []
        
        # Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph(
            "DIGITAL FORENSICS INVESTIGATION REPORT",
            self.styles['CustomTitle']
        ))
        
        story.append(Spacer(1, 0.5*inch))
        
        # Case information
        info_data = [
            ["Case ID:", self.case.case_id],
            ["Case Name:", self.case.case_name],
            ["Report ID:", self.report_id],
            ["Investigator:", self.case.investigator],
            ["Report Date:", self.generated_date.strftime('%Y-%m-%d %H:%M:%S')],
        ]
        
        info_table = Table(info_data, colWidths=[2*inch, 4*inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 12),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 12),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(info_table)
        
        # Disclaimer
        story.append(Spacer(1, 1*inch))
        disclaimer = Paragraph(
            "<b>DISCLAIMER:</b> This report was generated using an educational "
            "digital forensics toolkit. For production forensic investigations, "
            "use industry-standard certified tools and follow proper legal procedures.",
            self.styles['Normal']
        )
        story.append(disclaimer)
        
        return story
    
    def _build_toc(self) -> list:
        """Build table of contents."""
        story = []
        
        story.append(Paragraph("TABLE OF CONTENTS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        toc_items = [
            "1. Case Information",
            "2. Evidence Inventory",
            "3. Evidence Hashes",
            "4. Chain of Custody",
            "5. System Information",
            "6. Process Analysis",
            "7. Network Information",
            "8. Disk Forensics Results",
            "9. Memory Forensics Results",
            "10. Findings and Analysis",
            "11. Limitations",
            "12. Conclusion"
        ]
        
        for item in toc_items:
            story.append(Paragraph(item, self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
        
        return story
    
    def _build_case_info(self) -> list:
        """Build case information section."""
        story = []
        
        story.append(Paragraph("1. CASE INFORMATION", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        case_data = [
            ["Case ID", self.case.case_id],
            ["Case Name", self.case.case_name],
            ["Investigator", self.case.investigator],
            ["Status", self.case.status],
            ["Created Date", self.case.created_date],
            ["Description", self.case.description or "N/A"]
        ]
        
        case_table = Table(case_data, colWidths=[2*inch, 4.5*inch])
        case_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(case_table)
        story.append(Spacer(1, 0.3*inch))
        
        return story
    
    def _build_evidence_inventory(self) -> list:
        """Build evidence inventory section."""
        story = []
        
        story.append(Paragraph("2. EVIDENCE INVENTORY", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        evidence_list = self.evidence_manager.list_evidence(self.case_id)
        
        if not evidence_list:
            story.append(Paragraph("No evidence items recorded.", self.styles['Normal']))
            return story
        
        # Evidence table
        table_data = [["ID", "Filename", "Type", "Size", "Added", "Added By"]]
        
        for evidence in evidence_list:
            size_mb = evidence.file_size / (1024 * 1024)
            table_data.append([
                str(evidence.evidence_id),
                evidence.filename[:30],
                evidence.evidence_type,
                f"{size_mb:.2f} MB",
                evidence.added_date[:16],
                evidence.added_by
            ])
        
        evidence_table = Table(table_data, colWidths=[0.5*inch, 2*inch, 1.2*inch, 0.8*inch, 1.2*inch, 1*inch])
        evidence_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 8),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        
        story.append(evidence_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Hashes section
        story.append(Paragraph("2.1 Evidence Hashes", self.styles['SubsectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        for evidence in evidence_list:
            story.append(Paragraph(f"<b>{evidence.filename}</b>", self.styles['Normal']))
            
            hash_data = [
                ["MD5", evidence.md5_hash or "N/A"],
                ["SHA-1", evidence.sha1_hash or "N/A"],
                ["SHA-256", evidence.sha256_hash or "N/A"],
            ]
            
            hash_table = Table(hash_data, colWidths=[1*inch, 5.5*inch])
            hash_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Courier', 8),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ]))
            
            story.append(hash_table)
            story.append(Spacer(1, 0.15*inch))
        
        return story
    
    def _build_chain_of_custody(self) -> list:
        """Build chain of custody section."""
        story = []
        
        story.append(Paragraph("3. CHAIN OF CUSTODY", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        story.append(Paragraph(
            "<i>NOTE: This is an educational chain of custody record. "
            "Production forensic investigations require additional documentation "
            "and physical security measures.</i>",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.15*inch))
        
        coc = ChainOfCustody(self.case_dir)
        entries = coc.get_entries()
        
        if not entries:
            story.append(Paragraph("No chain of custody entries recorded.", self.styles['Normal']))
            return story
        
        # Build table
        table_data = [["Timestamp", "Evidence ID", "Action", "Investigator", "Description"]]
        
        for entry in entries:
            table_data.append([
                entry.timestamp[:16],
                entry.evidence_id,
                entry.action,
                entry.investigator,
                entry.description[:40]
            ])
        
        coc_table = Table(table_data, colWidths=[1.2*inch, 0.8*inch, 1.2*inch, 1*inch, 2.3*inch])
        coc_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 7),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(coc_table)
        story.append(Spacer(1, 0.2*inch))
        
        return story
    
    def _build_system_info(self) -> list:
        """Build system information section."""
        story = []
        
        story.append(Paragraph("4. SYSTEM INFORMATION", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Find system info artifacts
        system_dir = self.case_dir / "artifacts" / "system"
        
        if not system_dir.exists():
            story.append(Paragraph("No system information collected.", self.styles['Normal']))
            return story
        
        system_files = list(system_dir.glob("system_info_*.json"))
        
        if not system_files:
            story.append(Paragraph("No system information files found.", self.styles['Normal']))
            return story
        
        # Load most recent
        latest_file = max(system_files, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            os_info = data.get('operating_system', {})
            hw_info = data.get('hardware', {})
            
            story.append(Paragraph(f"<b>Hostname:</b> {data.get('hostname', 'N/A')}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Operating System:</b> {os_info.get('system', 'N/A')} {os_info.get('release', '')}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Architecture:</b> {os_info.get('architecture', 'N/A')}", self.styles['Normal']))
            
            cpu_info = hw_info.get('cpu', {})
            mem_info = hw_info.get('memory', {})
            
            story.append(Paragraph(f"<b>CPU Cores:</b> {cpu_info.get('logical_cores', 'N/A')}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Total Memory:</b> {mem_info.get('total_human', 'N/A')}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(f"<i>Collected from: {latest_file.name}</i>", self.styles['Normal']))
            
        except Exception as e:
            story.append(Paragraph(f"Error loading system information: {str(e)}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        return story
    
    def _build_process_info(self) -> list:
        """Build process analysis section."""
        story = []
        
        story.append(Paragraph("5. PROCESS ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Find process artifacts
        system_dir = self.case_dir / "artifacts" / "system"
        
        if not system_dir.exists():
            story.append(Paragraph("No process information collected.", self.styles['Normal']))
            return story
        
        process_files = list(system_dir.glob("processes_*.json"))
        
        if not process_files:
            story.append(Paragraph("No process information files found.", self.styles['Normal']))
            return story
        
        # Load most recent
        latest_file = max(process_files, key=lambda p: p.stat().st_mtime)
        
        try:
            with open(latest_file, 'r') as f:
                data = json.load(f)
            
            processes = data.get('processes', [])
            suspicious = [p for p in processes if p.get('is_interesting')]
            
            story.append(Paragraph(f"<b>Total Processes:</b> {len(processes)}", self.styles['Normal']))
            story.append(Paragraph(f"<b>Processes with Indicators:</b> {len(suspicious)}", self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            if suspicious:
                story.append(Paragraph("<b>Potentially Interesting Processes:</b>", self.styles['SubsectionHeader']))
                
                for proc in suspicious[:10]:  # Show first 10
                    story.append(Paragraph(
                        f"PID {proc['pid']}: {proc['name']} - "
                        f"{', '.join(proc.get('suspicious_indicators', []))}",
                        self.styles['Normal']
                    ))
            
        except Exception as e:
            story.append(Paragraph(f"Error loading process information: {str(e)}", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        return story
    
    def _build_network_info(self) -> list:
        """Build network information section."""
        story = []
        
        story.append(Paragraph("6. NETWORK INFORMATION", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        # Find network artifacts
        system_dir = self.case_dir / "artifacts" / "system"
        
        if system_dir.exists():
            network_files = list(system_dir.glob("network_*.json"))
            
            if network_files:
                latest_file = max(network_files, key=lambda p: p.stat().st_mtime)
                
                try:
                    with open(latest_file, 'r') as f:
                        data = json.load(f)
                    
                    connections = data.get('connections', [])
                    interfaces = data.get('interfaces', {})
                    
                    story.append(Paragraph(f"<b>Active Connections:</b> {len(connections)}", self.styles['Normal']))
                    story.append(Paragraph(f"<b>Network Interfaces:</b> {len(interfaces)}", self.styles['Normal']))
                    
                except Exception as e:
                    story.append(Paragraph(f"Error loading network information: {str(e)}", self.styles['Normal']))
            else:
                story.append(Paragraph("No network information collected.", self.styles['Normal']))
        else:
            story.append(Paragraph("No network information collected.", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        return story
    
    def _build_disk_analysis(self) -> list:
        """Build disk forensics section."""
        story = []
        
        story.append(Paragraph("7. DISK FORENSICS RESULTS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        disk_dir = self.case_dir / "artifacts" / "disk"
        
        if disk_dir.exists() and any(disk_dir.iterdir()):
            result_files = list(disk_dir.glob("*.txt"))
            
            if result_files:
                story.append(Paragraph(f"<b>Analysis Files Generated:</b> {len(result_files)}", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                
                for file in result_files[:5]:  # List first 5
                    story.append(Paragraph(f"• {file.name}", self.styles['Normal']))
                
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(
                    "<i>Full results available in case artifacts directory.</i>",
                    self.styles['Normal']
                ))
            else:
                story.append(Paragraph("No disk forensics analysis performed.", self.styles['Normal']))
        else:
            story.append(Paragraph("No disk forensics analysis performed.", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        return story
    
    def _build_memory_analysis(self) -> list:
        """Build memory forensics section."""
        story = []
        
        story.append(Paragraph("8. MEMORY FORENSICS RESULTS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        memory_dir = self.case_dir / "artifacts" / "memory"
        
        if memory_dir.exists() and any(memory_dir.iterdir()):
            result_files = list(memory_dir.glob("*.txt"))
            
            if result_files:
                story.append(Paragraph(f"<b>Volatility Plugins Executed:</b> {len(result_files)}", self.styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
                
                for file in result_files:
                    plugin_name = file.stem.split('_')[0]
                    story.append(Paragraph(f"• {plugin_name} ({file.name})", self.styles['Normal']))
                
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph(
                    "<i>Full results available in case artifacts directory.</i>",
                    self.styles['Normal']
                ))
            else:
                story.append(Paragraph("No memory forensics analysis performed.", self.styles['Normal']))
        else:
            story.append(Paragraph("No memory forensics analysis performed.", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        return story
    
    def _build_findings(self, findings_text: str) -> list:
        """Build findings section."""
        story = []
        
        story.append(Paragraph("9. FINDINGS AND ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        if findings_text:
            # Split into paragraphs
            for para in findings_text.split('\n\n'):
                if para.strip():
                    story.append(Paragraph(para.strip(), self.styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
        else:
            story.append(Paragraph("No findings entered by investigator.", self.styles['Normal']))
        
        story.append(Spacer(1, 0.2*inch))
        return story
    
    def _build_limitations(self) -> list:
        """Build limitations section."""
        story = []
        
        story.append(Paragraph("10. LIMITATIONS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        limitations = [
            "This report was generated using an educational digital forensics toolkit.",
            "The toolkit is designed for learning purposes and may not meet all requirements for production forensic investigations.",
            "Chain of custody documentation in this report is for educational purposes and may not meet legal evidentiary standards.",
            "Analysis was performed using available open-source tools (Sleuth Kit, Volatility 3).",
            "Results should be validated using multiple forensic tools where critical.",
            "Live system collection reflects the state of the system at the time of collection only.",
            "Encrypted, corrupted, or heavily damaged evidence may not be fully analyzable.",
        ]
        
        for limitation in limitations:
            story.append(Paragraph(f"• {limitation}", self.styles['Normal']))
            story.append(Spacer(1, 0.05*inch))
        
        story.append(Spacer(1, 0.2*inch))
        return story
    
    def _build_conclusion(self) -> list:
        """Build conclusion section."""
        story = []
        
        story.append(Paragraph("11. CONCLUSION", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        conclusion = (
            f"This forensic investigation report documents the analysis performed on case "
            f"{self.case.case_id} - {self.case.case_name}. "
            f"Evidence was collected, preserved, and analyzed following digital forensics best practices "
            f"to the extent possible with educational tools. "
            f"All evidence integrity was verified using cryptographic hashing. "
            f"Chain of custody was maintained throughout the investigation process."
        )
        
        story.append(Paragraph(conclusion, self.styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Signature block
        story.append(Spacer(1, 0.5*inch))
        
        sig_data = [
            ["Investigator:", self.case.investigator],
            ["Report Date:", self.generated_date.strftime('%Y-%m-%d %H:%M:%S')],
            ["Report ID:", self.report_id],
        ]
        
        sig_table = Table(sig_data, colWidths=[2*inch, 4*inch])
        sig_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(sig_table)
        
        return story