"""
Analysis tab for forensic investigations.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
from pathlib import Path
import json
from datetime import datetime

from collectors.system_collector import SystemCollector
from collectors.process_collector import ProcessCollector
from collectors.network_collector import NetworkCollector
from collectors.file_metadata import FileMetadataCollector
from collectors.browser_artifacts import BrowserArtifactsCollector
from integrations.sleuthkit import SleuthKitIntegration
from integrations.volatility import VolatilityIntegration


class AnalysisTab:
    """
    Analysis operations tab.
    """
    
    def __init__(self, parent, app):
        """
        Initialize analysis tab.
        
        Args:
            parent: Parent widget
            app: Main application instance
        """
        self.app = app
        self.frame = tk.Frame(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create tab widgets."""
        # Title
        title = tk.Label(
            self.frame,
            text="Forensic Analysis",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)
        
        # Create notebook for analysis categories
        self.analysis_notebook = ttk.Notebook(self.frame)
        self.analysis_notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Live Collection tab
        self._create_live_collection_tab()
        
        # Disk Forensics tab
        self._create_disk_forensics_tab()
        
        # Memory Forensics tab
        self._create_memory_forensics_tab()
        
        # File Analysis tab
        self._create_file_analysis_tab()
        
        # Browser Artifacts tab
        self._create_browser_artifacts_tab()
    
    def _create_live_collection_tab(self):
        """Create live system collection tab."""
        frame = tk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(frame, text="Live Collection")
        
        tk.Label(
            frame,
            text="Live System Collection",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        tk.Label(
            frame,
            text="Collect information from the LIVE SYSTEM where this toolkit is running",
            font=("Arial", 10),
            fg="red"
        ).pack(pady=5)
        
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Collect System Info",
            command=self.collect_system_info,
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10
        ).grid(row=0, column=0, padx=10, pady=5)
        
        tk.Button(
            button_frame,
            text="Collect Process Info",
            command=self.collect_process_info,
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10
        ).grid(row=0, column=1, padx=10, pady=5)
        
        tk.Button(
            button_frame,
            text="Collect Network Info",
            command=self.collect_network_info,
            bg="#3498db",
            fg="white",
            padx=20,
            pady=10
        ).grid(row=1, column=0, padx=10, pady=5)
        
        tk.Button(
            button_frame,
            text="Collect All",
            command=self.collect_all_live,
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=10
        ).grid(row=1, column=1, padx=10, pady=5)
        
        # Results area
        tk.Label(frame, text="Collection Results:", font=("Arial", 11)).pack(pady=5)
        self.live_results = scrolledtext.ScrolledText(frame, height=15, font=("Courier", 9))
        self.live_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def _create_disk_forensics_tab(self):
        """Create disk forensics tab."""
        frame = tk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(frame, text="Disk Forensics")
        
        tk.Label(
            frame,
            text="Disk Image Analysis (Sleuth Kit)",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Evidence selection
        select_frame = tk.Frame(frame)
        select_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(select_frame, text="Select Evidence:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.disk_evidence_var = tk.StringVar()
        self.disk_evidence_combo = ttk.Combobox(
            select_frame,
            textvariable=self.disk_evidence_var,
            state="readonly",
            width=50
        )
        self.disk_evidence_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            select_frame,
            text="Refresh",
            command=self.refresh_disk_evidence_list
        ).pack(side=tk.LEFT, padx=5)
        
        # Commands
        command_frame = tk.Frame(frame)
        command_frame.pack(pady=10)
        
        tk.Button(
            command_frame,
            text="mmls (Partitions)",
            command=self.run_mmls,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8
        ).grid(row=0, column=0, padx=5, pady=5)
        
        tk.Button(
            command_frame,
            text="fsstat (Filesystem)",
            command=self.run_fsstat,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8
        ).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(
            command_frame,
            text="fls (File List)",
            command=self.run_fls,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8
        ).grid(row=0, column=2, padx=5, pady=5)
        
        # Results
        tk.Label(frame, text="Analysis Results:", font=("Arial", 11)).pack(pady=5)
        self.disk_results = scrolledtext.ScrolledText(frame, height=15, font=("Courier", 9))
        self.disk_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def _create_memory_forensics_tab(self):
        """Create memory forensics tab."""
        frame = tk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(frame, text="Memory Forensics")
        
        tk.Label(
            frame,
            text="Memory Dump Analysis (Volatility 3)",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        # Evidence selection
        select_frame = tk.Frame(frame)
        select_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(select_frame, text="Select Memory Dump:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.memory_evidence_var = tk.StringVar()
        self.memory_evidence_combo = ttk.Combobox(
            select_frame,
            textvariable=self.memory_evidence_var,
            state="readonly",
            width=50
        )
        self.memory_evidence_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            select_frame,
            text="Refresh",
            command=self.refresh_memory_evidence_list
        ).pack(side=tk.LEFT, padx=5)
        
        # Plugins
        plugin_frame = tk.Frame(frame)
        plugin_frame.pack(pady=10)
        
        tk.Button(
            plugin_frame,
            text="windows.info",
            command=lambda: self.run_volatility_plugin("windows.info"),
            bg="#9b59b6",
            fg="white",
            padx=12,
            pady=8
        ).grid(row=0, column=0, padx=5, pady=5)
        
        tk.Button(
            plugin_frame,
            text="windows.pslist",
            command=lambda: self.run_volatility_plugin("windows.pslist"),
            bg="#9b59b6",
            fg="white",
            padx=12,
            pady=8
        ).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Button(
            plugin_frame,
            text="windows.pstree",
            command=lambda: self.run_volatility_plugin("windows.pstree"),
            bg="#9b59b6",
            fg="white",
            padx=12,
            pady=8
        ).grid(row=0, column=2, padx=5, pady=5)
        
        tk.Button(
            plugin_frame,
            text="windows.netstat",
            command=lambda: self.run_volatility_plugin("windows.netstat"),
            bg="#9b59b6",
            fg="white",
            padx=12,
            pady=8
        ).grid(row=1, column=0, padx=5, pady=5)
        
        tk.Button(
            plugin_frame,
            text="windows.cmdline",
            command=lambda: self.run_volatility_plugin("windows.cmdline"),
            bg="#9b59b6",
            fg="white",
            padx=12,
            pady=8
        ).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(
            plugin_frame,
            text="windows.dlllist",
            command=lambda: self.run_volatility_plugin("windows.dlllist"),
            bg="#9b59b6",
            fg="white",
            padx=12,
            pady=8
        ).grid(row=1, column=2, padx=5, pady=5)
        
        # Results
        tk.Label(frame, text="Plugin Results:", font=("Arial", 11)).pack(pady=5)
        self.memory_results = scrolledtext.ScrolledText(frame, height=15, font=("Courier", 9))
        self.memory_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def _create_file_analysis_tab(self):
        """Create file analysis tab."""
        frame = tk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(frame, text="File Analysis")
        
        tk.Label(
            frame,
            text="File Metadata Analysis",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        tk.Button(
            frame,
            text="Select File to Analyze",
            command=self.analyze_file,
            bg="#e67e22",
            fg="white",
            padx=20,
            pady=10
        ).pack(pady=20)
        
        # Results
        tk.Label(frame, text="Analysis Results:", font=("Arial", 11)).pack(pady=5)
        self.file_results = scrolledtext.ScrolledText(frame, height=20, font=("Courier", 9))
        self.file_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    def _create_browser_artifacts_tab(self):
        """Create browser artifacts tab."""
        frame = tk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(frame, text="Browser Artifacts")
        
        tk.Label(
            frame,
            text="Browser History Collection",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        tk.Label(
            frame,
            text="NOTE: Only collects browsing history metadata. Does NOT extract credentials.",
            font=("Arial", 9),
            fg="red"
        ).pack(pady=5)
        
        button_frame = tk.Frame(frame)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Collect Chrome History",
            command=self.collect_chrome_history,
            bg="#1abc9c",
            fg="white",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Collect Edge History",
            command=self.collect_edge_history,
            bg="#1abc9c",
            fg="white",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame,
            text="Collect Firefox History",
            command=self.collect_firefox_history,
            bg="#1abc9c",
            fg="white",
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)
        
        # Results
        tk.Label(frame, text="Collection Results:", font=("Arial", 11)).pack(pady=5)
        self.browser_results = scrolledtext.ScrolledText(frame, height=15, font=("Courier", 9))
        self.browser_results.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
    
    # Live Collection Methods
    
    def collect_system_info(self):
        """Collect system information."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "Please open a case first")
            return
        
        self.app.set_status("Collecting system information...")
        self.live_results.delete("1.0", tk.END)
        
        info = SystemCollector.collect_all()
        
        # Save to case directory
        case_dir = self.app.case_manager.get_case_directory(self.app.current_case.case_id)
        output_path = case_dir / "artifacts" / "system" / f"system_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        SystemCollector.save_to_file(info, output_path)
        
        # Display
        self.live_results.insert("1.0", json.dumps(info, indent=2))
        messagebox.showinfo("Success", f"System information saved to:\n{output_path}")
        self.app.set_status("Ready")
    
    def collect_process_info(self):
        """Collect process information."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "Please open a case first")
            return
        
        self.app.set_status("Collecting process information...")
        self.live_results.delete("1.0", tk.END)
        
        processes = ProcessCollector.collect_all()
        
        # Save to case directory
        case_dir = self.app.case_manager.get_case_directory(self.app.current_case.case_id)
        output_path = case_dir / "artifacts" / "system" / f"processes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        ProcessCollector.save_to_file(processes, output_path)
        
        # Display summary
        suspicious = [p for p in processes if p.suspicious_indicators]
        
        summary = f"Total Processes: {len(processes)}\n"
        summary += f"Processes with Indicators: {len(suspicious)}\n\n"
        
        if suspicious:
            summary += "Potentially Interesting Processes:\n"
            summary += "=" * 80 + "\n"
            for proc in suspicious:
                summary += f"\nPID: {proc.pid} | Name: {proc.name}\n"
                summary += f"Executable: {proc.exe}\n"
                summary += f"Indicators: {', '.join(proc.suspicious_indicators)}\n"
        
        self.live_results.insert("1.0", summary)
        messagebox.showinfo("Success", f"Process information saved to:\n{output_path}")
        self.app.set_status("Ready")
    
    def collect_network_info(self):
        """Collect network information."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "Please open a case first")
            return
        
        self.app.set_status("Collecting network information...")
        self.live_results.delete("1.0", tk.END)
        
        info = NetworkCollector.collect_all()
        
        # Save to case directory
        case_dir = self.app.case_manager.get_case_directory(self.app.current_case.case_id)
        output_path = case_dir / "artifacts" / "system" / f"network_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        NetworkCollector.save_to_file(info, output_path)
        
        # Display summary
        summary = f"Hostname: {info.get('hostname')}\n"
        summary += f"Connections: {len(info.get('connections', []))}\n"
        summary += f"Interfaces: {len(info.get('interfaces', {}))}\n\n"
        
        if info.get('connections'):
            summary += "Active Connections:\n"
            summary += "=" * 80 + "\n"
            for conn in info['connections'][:20]:  # Show first 20
                summary += f"{conn['local_address']}:{conn['local_port']} -> "
                summary += f"{conn['remote_address']}:{conn['remote_port']} "
                summary += f"({conn['status']}) PID: {conn['pid']}\n"
        
        self.live_results.insert("1.0", summary)
        messagebox.showinfo("Success", f"Network information saved to:\n{output_path}")
        self.app.set_status("Ready")
    
    def collect_all_live(self):
        """Collect all live system information."""
        self.collect_system_info()
        self.collect_process_info()
        self.collect_network_info()
    
    # Disk Forensics Methods
    
    def refresh_disk_evidence_list(self):
        """Refresh disk evidence list."""
        if not self.app.current_case:
            return
        
        evidence_list = self.app.evidence_manager.list_evidence(self.app.current_case.case_id)
        disk_evidence = [
            f"{e.evidence_id}: {e.filename}"
            for e in evidence_list
            if e.evidence_type in ['Forensic Image', 'Disk Image']
        ]
        
        self.disk_evidence_combo['values'] = disk_evidence
        if disk_evidence:
            self.disk_evidence_combo.current(0)
    
    def run_mmls(self):
        """Run mmls command."""
        if not self._check_disk_prerequisites():
            return
        
        tsk = SleuthKitIntegration()
        if not tsk.is_available():
            messagebox.showerror("Error", "Sleuth Kit not available.\n\n" + 
                               SleuthKitIntegration.get_installation_instructions())
            return
        
        evidence_path = self._get_selected_disk_evidence_path()
        if not evidence_path:
            return
        
        self.app.set_status("Running mmls...")
        self.disk_results.delete("1.0", tk.END)
        
        result = tsk.run_mmls(evidence_path)
        
        if result and result.success():
            self.disk_results.insert("1.0", result.stdout)
            self._save_disk_result(result, "mmls")
        else:
            error_msg = result.stderr if result else "Command failed"
            self.disk_results.insert("1.0", f"Error:\n{error_msg}")
        
        self.app.set_status("Ready")
    
    def run_fsstat(self):
        """Run fsstat command."""
        if not self._check_disk_prerequisites():
            return
        
        tsk = SleuthKitIntegration()
        if not tsk.is_available():
            messagebox.showerror("Error", "Sleuth Kit not available")
            return
        
        evidence_path = self._get_selected_disk_evidence_path()
        if not evidence_path:
            return
        
        self.app.set_status("Running fsstat...")
        self.disk_results.delete("1.0", tk.END)
        
        result = tsk.run_fsstat(evidence_path)
        
        if result and result.success():
            self.disk_results.insert("1.0", result.stdout)
            self._save_disk_result(result, "fsstat")
        else:
            error_msg = result.stderr if result else "Command failed"
            self.disk_results.insert("1.0", f"Error:\n{error_msg}")
        
        self.app.set_status("Ready")
    
    def run_fls(self):
        """Run fls command."""
        if not self._check_disk_prerequisites():
            return
        
        tsk = SleuthKitIntegration()
        if not tsk.is_available():
            messagebox.showerror("Error", "Sleuth Kit not available")
            return
        
        evidence_path = self._get_selected_disk_evidence_path()
        if not evidence_path:
            return
        
        self.app.set_status("Running fls...")
        self.disk_results.delete("1.0", tk.END)
        
        result = tsk.run_fls(evidence_path, recursive=False)
        
        if result and result.success():
            self.disk_results.insert("1.0", result.stdout)
            self._save_disk_result(result, "fls")
        else:
            error_msg = result.stderr if result else "Command failed"
            self.disk_results.insert("1.0", f"Error:\n{error_msg}")
        
        self.app.set_status("Ready")
    
    def _check_disk_prerequisites(self) -> bool:
        """Check disk analysis prerequisites."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "Please open a case first")
            return False
        
        if not self.disk_evidence_var.get():
            messagebox.showwarning("Warning", "Please select a disk image")
            return False
        
        return True
    
    def _get_selected_disk_evidence_path(self) -> Path:
        """Get path to selected disk evidence."""
        selection = self.disk_evidence_var.get()
        if not selection:
            return None
        
        evidence_id = int(selection.split(':')[0])
        return self.app.evidence_manager.get_evidence_path(evidence_id)
    
    def _save_disk_result(self, result, command_name: str):
        """Save disk analysis result."""
        case_dir = self.app.case_manager.get_case_directory(self.app.current_case.case_id)
        output_path = case_dir / "artifacts" / "disk" / f"{command_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        tsk = SleuthKitIntegration()
        tsk.save_result(result, output_path)
    
    # Memory Forensics Methods
    
    def refresh_memory_evidence_list(self):
        """Refresh memory evidence list."""
        if not self.app.current_case:
            return
        
        evidence_list = self.app.evidence_manager.list_evidence(self.app.current_case.case_id)
        memory_evidence = [
            f"{e.evidence_id}: {e.filename}"
            for e in evidence_list
            if e.evidence_type == 'Memory Dump'
        ]
        
        self.memory_evidence_combo['values'] = memory_evidence
        if memory_evidence:
            self.memory_evidence_combo.current(0)
    
    def run_volatility_plugin(self, plugin_name: str):
        """Run Volatility plugin."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "Please open a case first")
            return
        
        if not self.memory_evidence_var.get():
            messagebox.showwarning("Warning", "Please select a memory dump")
            return
        
        vol = VolatilityIntegration()
        if not vol.is_available():
            messagebox.showerror("Error", "Volatility 3 not available.\n\n" + 
                               VolatilityIntegration.get_installation_instructions())
            return
        
        evidence_path = self._get_selected_memory_evidence_path()
        if not evidence_path:
            return
        
        self.app.set_status(f"Running Volatility plugin: {plugin_name}...")
        self.memory_results.delete("1.0", tk.END)
        self.memory_results.insert("1.0", f"Executing {plugin_name}...\nThis may take several minutes.\n")
        self.app.root.update()
        
        result = vol.run_plugin(evidence_path, plugin_name)
        
        if result and result.success():
            self.memory_results.delete("1.0", tk.END)
            self.memory_results.insert("1.0", result.stdout)
            self._save_memory_result(result)
            messagebox.showinfo("Success", f"Plugin {plugin_name} completed successfully")
        else:
            error_msg = result.stderr if result else "Plugin failed"
            self.memory_results.delete("1.0", tk.END)
            self.memory_results.insert("1.0", f"Error:\n{error_msg}")
            messagebox.showerror("Error", f"Plugin {plugin_name} failed")
        
        self.app.set_status("Ready")
    
    def _get_selected_memory_evidence_path(self) -> Path:
        """Get path to selected memory evidence."""
        selection = self.memory_evidence_var.get()
        if not selection:
            return None
        
        evidence_id = int(selection.split(':')[0])
        return self.app.evidence_manager.get_evidence_path(evidence_id)
    
    def _save_memory_result(self, result):
        """Save memory analysis result."""
        case_dir = self.app.case_manager.get_case_directory(self.app.current_case.case_id)
        output_path = case_dir / "artifacts" / "memory" / f"{result.plugin}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        vol = VolatilityIntegration()
        vol.save_result(result, output_path)
    
    # File Analysis Methods
    
    def analyze_file(self):
        """Analyze selected file."""
        file_path = filedialog.askopenfilename(title="Select File to Analyze")
        if not file_path:
            return
        
        self.app.set_status("Analyzing file...")
        self.file_results.delete("1.0", tk.END)
        
        metadata = FileMetadataCollector.collect(Path(file_path))
        
        if metadata:
            result_text = "FILE ANALYSIS RESULTS\n"
            result_text += "=" * 80 + "\n\n"
            result_text += f"Filename: {metadata['filename']}\n"
            result_text += f"Full Path: {metadata['full_path']}\n"
            result_text += f"Extension: {metadata['extension']}\n"
            result_text += f"Size: {metadata['size_human']} ({metadata['size']} bytes)\n"
            result_text += f"MIME Type: {metadata['mime_type']}\n\n"
            
            result_text += "Timestamps:\n"
            result_text += f"  Created:  {metadata['created_str']}\n"
            result_text += f"  Modified: {metadata['modified_str']}\n"
            result_text += f"  Accessed: {metadata['accessed_str']}\n\n"
            
            result_text += "Cryptographic Hashes:\n"
            for algo, hash_value in metadata['hashes'].items():
                if hash_value:
                    result_text += f"  {algo.upper()}: {hash_value}\n"
            
            self.file_results.insert("1.0", result_text)
        else:
            self.file_results.insert("1.0", "Failed to analyze file")
        
        self.app.set_status("Ready")
    
    # Browser Artifacts Methods
    
    def collect_chrome_history(self):
        """Collect Chrome history."""
        self.app.set_status("Collecting Chrome history...")
        self.browser_results.delete("1.0", tk.END)
        
        history = BrowserArtifactsCollector.collect_chrome_history()
        
        if history:
            result_text = f"Chrome History - {len(history)} entries\n"
            result_text += "=" * 80 + "\n\n"
            
            for entry in history[:100]:  # Show first 100
                result_text += f"URL: {entry.url}\n"
                result_text += f"Title: {entry.title}\n"
                result_text += f"Visit Time: {entry.visit_time}\n"
                result_text += f"Visit Count: {entry.visit_count}\n"
                result_text += "-" * 80 + "\n"
            
            self.browser_results.insert("1.0", result_text)
            
            if self.app.current_case:
                case_dir = self.app.case_manager.get_case_directory(self.app.current_case.case_id)
                output_path = case_dir / "artifacts" / "browser" / f"chrome_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(output_path, 'w') as f:
                    json.dump([h.to_dict() for h in history], f, indent=2)
                
                messagebox.showinfo("Success", f"Collected {len(history)} Chrome history entries")
        else:
            self.browser_results.insert("1.0", "No Chrome history found or browser not installed")
        
        self.app.set_status("Ready")
    
    def collect_edge_history(self):
        """Collect Edge history."""
        self.app.set_status("Collecting Edge history...")
        self.browser_results.delete("1.0", tk.END)
        
        history = BrowserArtifactsCollector.collect_edge_history()
        
        if history:
            result_text = f"Edge History - {len(history)} entries\n"
            result_text += "=" * 80 + "\n\n"
            
            for entry in history[:100]:
                result_text += f"URL: {entry.url}\n"
                result_text += f"Title: {entry.title}\n"
                result_text += f"Visit Time: {entry.visit_time}\n"
                result_text += f"Visit Count: {entry.visit_count}\n"
                result_text += "-" * 80 + "\n"
            
            self.browser_results.insert("1.0", result_text)
            messagebox.showinfo("Success", f"Collected {len(history)} Edge history entries")
        else:
            self.browser_results.insert("1.0", "No Edge history found or browser not installed")
        
        self.app.set_status("Ready")
    
    def collect_firefox_history(self):
        """Collect Firefox history."""
        self.app.set_status("Collecting Firefox history...")
        self.browser_results.delete("1.0", tk.END)
        
        history = BrowserArtifactsCollector.collect_firefox_history()
        
        if history:
            result_text = f"Firefox History - {len(history)} entries\n"
            result_text += "=" * 80 + "\n\n"
            
            for entry in history[:100]:
                result_text += f"URL: {entry.url}\n"
                result_text += f"Title: {entry.title}\n"
                result_text += f"Visit Time: {entry.visit_time}\n"
                result_text += f"Visit Count: {entry.visit_count}\n"
                result_text += "-" * 80 + "\n"
            
            self.browser_results.insert("1.0", result_text)
            messagebox.showinfo("Success", f"Collected {len(history)} Firefox history entries")
        else:
            self.browser_results.insert("1.0", "No Firefox history found or browser not installed")
        
        self.app.set_status("Ready")
    
    def refresh(self):
        """Refresh analysis tab."""
        self.refresh_disk_evidence_list()
        self.refresh_memory_evidence_list()