"""
Main GUI window for Digital Forensics Toolkit.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import json
from typing import Optional
from datetime import datetime
from core.case_manager import CaseManager
from core.evidence_manager import EvidenceManager
from core.logger import ForensicLogger
from gui.case_tab import CaseTab
from gui.evidence_tab import EvidenceTab
from gui.analysis_tab import AnalysisTab
from gui.report_tab import ReportTab


class ForensicToolkitGUI:
    """
    Main GUI application for Digital Forensics Toolkit.
    """
    
    def __init__(self):
        """Initialize the GUI application."""
        self.root = tk.Tk()
        self.root.title("Digital Forensics Toolkit v1.0")
        self.root.geometry("1200x800")
        
        # Initialize managers
        self.case_manager = CaseManager()
        self.evidence_manager = EvidenceManager(
            self.case_manager.db_path,
            self.case_manager.base_dir
        )
        
        # Current case
        self.current_case = None
        self.logger = None
        
        # Load configuration
        self.config = self._load_config()
        
        # Create UI
        self._create_menu()
        self._create_header()
        self._create_main_area()
        self._create_status_bar()
        
        # Check tool availability
        self._check_tools()
    
    def _load_config(self) -> dict:
        """Load configuration from file."""
        config_path = Path("config/config.json")
        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Case", command=self._new_case)
        file_menu.add_command(label="Open Case", command=self._open_case)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Check Tool Status", command=self._check_tools)
        tools_menu.add_command(label="Installation Help", command=self._show_installation_help)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
    
    def _create_header(self):
        """Create header section."""
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="DIGITAL FORENSICS TOOLKIT",
            font=("Arial", 24, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=10)
        
        # Case info frame
        self.case_info_frame = tk.Frame(header_frame, bg="#2c3e50")
        self.case_info_frame.pack(fill=tk.X, padx=20)
        
        self.case_label = tk.Label(
            self.case_info_frame,
            text="No Case Loaded",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        self.case_label.pack(side=tk.LEFT)
        
        self.status_indicator = tk.Label(
            self.case_info_frame,
            text="",
            font=("Arial", 10),
            bg="#2c3e50",
            fg="#95a5a6"
        )
        self.status_indicator.pack(side=tk.RIGHT)
    
    def _create_main_area(self):
        """Create main tabbed interface."""
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.case_tab = CaseTab(self.notebook, self)
        self.evidence_tab = EvidenceTab(self.notebook, self)
        self.analysis_tab = AnalysisTab(self.notebook, self)
        self.report_tab = ReportTab(self.notebook, self)
        
        # Add tabs to notebook
        self.notebook.add(self.case_tab.frame, text="Case Management")
        self.notebook.add(self.evidence_tab.frame, text="Evidence")
        self.notebook.add(self.analysis_tab.frame, text="Analysis")
        self.notebook.add(self.report_tab.frame, text="Reports")
    
    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = tk.Label(
            self.root,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=("Arial", 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _new_case(self):
        """Create new case dialog."""
        self.case_tab.create_case_dialog()
    
    def _open_case(self):
        """Open existing case dialog."""
        self.case_tab.open_case_dialog()
    
    def load_case(self, case_id: str):
        """
        Load a case into the GUI.
        
        Args:
            case_id: Case identifier
        """
        case = self.case_manager.get_case(case_id)
        if case:
            self.current_case = case
            self.logger = ForensicLogger(case_id)
            
            # Update header
            self.case_label.config(
                text=f"Case: {case.case_id} - {case.case_name}"
            )
            self.status_indicator.config(
                text=f"Status: {case.status} | Investigator: {case.investigator}"
            )
            
            # Refresh tabs
            self.evidence_tab.refresh()
            self.analysis_tab.refresh()
            self.report_tab.refresh()
            
            self.set_status(f"Case loaded: {case.case_id}")
            messagebox.showinfo("Success", f"Case {case.case_id} loaded successfully")
        else:
            messagebox.showerror("Error", "Failed to load case")
    
    def _check_tools(self):
        """Check availability of external tools."""
        from integrations.sleuthkit import SleuthKitIntegration
        from integrations.volatility import VolatilityIntegration
        from integrations.autopsy import AutopsyIntegration
        from integrations.ftk_imager import FTKImagerIntegration
        
        # Check Sleuth Kit
        tsk = SleuthKitIntegration()
        tsk_status = "AVAILABLE" if tsk.is_available() else "NOT DETECTED"
        
        # Check Volatility
        vol = VolatilityIntegration()
        vol_status = "AVAILABLE" if vol.is_available() else "NOT DETECTED"
        
        # Autopsy and FTK Imager are documentation-only
        autopsy_status = "NOT DETECTED"
        ftk_status = "NOT DETECTED"
        
        # Update status
        status_text = (
            f"Tool Status:\n\n"
            f"Sleuth Kit: {tsk_status}\n"
            f"Volatility 3: {vol_status}\n"
            f"Autopsy: {autopsy_status} (GUI Tool)\n"
            f"FTK Imager: {ftk_status} (GUI Tool)"
        )
        
        messagebox.showinfo("Tool Status", status_text)
        
        # Store for later use
        self.tool_status = {
            'sleuthkit': tsk.is_available(),
            'volatility': vol.is_available(),
            'autopsy': False,
            'ftk_imager': False
        }
    
    def _show_installation_help(self):
        """Show installation help dialog."""
        from integrations.sleuthkit import SleuthKitIntegration
        from integrations.volatility import VolatilityIntegration
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Installation Help")
        help_window.geometry("800x600")
        
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sleuth Kit tab
        tsk_frame = tk.Frame(notebook)
        tsk_text = tk.Text(tsk_frame, wrap=tk.WORD, font=("Courier", 9))
        tsk_scroll = tk.Scrollbar(tsk_frame, command=tsk_text.yview)
        tsk_text.config(yscrollcommand=tsk_scroll.set)
        tsk_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tsk_text.pack(fill=tk.BOTH, expand=True)
        tsk_text.insert("1.0", SleuthKitIntegration.get_installation_instructions())
        tsk_text.config(state=tk.DISABLED)
        notebook.add(tsk_frame, text="Sleuth Kit")
        
        # Volatility tab
        vol_frame = tk.Frame(notebook)
        vol_text = tk.Text(vol_frame, wrap=tk.WORD, font=("Courier", 9))
        vol_scroll = tk.Scrollbar(vol_frame, command=vol_text.yview)
        vol_text.config(yscrollcommand=vol_scroll.set)
        vol_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        vol_text.pack(fill=tk.BOTH, expand=True)
        vol_text.insert("1.0", VolatilityIntegration.get_installation_instructions())
        vol_text.config(state=tk.DISABLED)
        notebook.add(vol_frame, text="Volatility 3")
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """
Digital Forensics Toolkit v1.0

An educational forensic investigation platform for:
- Case management
- Evidence handling
- Chain of custody
- Disk forensics
- Memory forensics
- Integrity verification
- Report generation

Developed for cybersecurity education and training.

DISCLAIMER: This is an educational tool. For production
forensic investigations, use industry-standard certified
tools and follow proper legal procedures.
        """
        messagebox.showinfo("About", about_text.strip())
    
    def _show_documentation(self):
        """Show documentation."""
        messagebox.showinfo(
            "Documentation",
            "Please refer to README.md for complete documentation.\n\n"
            "Key features:\n"
            "- Create and manage cases\n"
            "- Add and verify evidence\n"
            "- Maintain chain of custody\n"
            "- Analyze disk images and memory dumps\n"
            "- Generate professional reports"
        )
    
    def set_status(self, message: str):
        """
        Update status bar.
        
        Args:
            message: Status message
        """
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()