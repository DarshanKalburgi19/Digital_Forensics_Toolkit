"""
Report generation tab for GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from datetime import datetime


class ReportTab:
    """
    Report generation tab.
    """
    
    def __init__(self, parent, app):
        """
        Initialize report tab.
        
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
            text="Report Generation",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)
        
        # Report options
        options_frame = tk.LabelFrame(self.frame, text="Report Options", font=("Arial", 12))
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Checkboxes for report sections
        self.include_case_info = tk.BooleanVar(value=True)
        self.include_evidence = tk.BooleanVar(value=True)
        self.include_chain_of_custody = tk.BooleanVar(value=True)
        self.include_system_info = tk.BooleanVar(value=True)
        self.include_process_info = tk.BooleanVar(value=True)
        self.include_network_info = tk.BooleanVar(value=True)
        self.include_disk_analysis = tk.BooleanVar(value=True)
        self.include_memory_analysis = tk.BooleanVar(value=True)
        
        tk.Checkbutton(
            options_frame,
            text="Case Information",
            variable=self.include_case_info,
            font=("Arial", 10)
        ).grid(row=0, column=0, sticky=tk.W, padx=20, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Evidence Inventory",
            variable=self.include_evidence,
            font=("Arial", 10)
        ).grid(row=0, column=1, sticky=tk.W, padx=20, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Chain of Custody",
            variable=self.include_chain_of_custody,
            font=("Arial", 10)
        ).grid(row=1, column=0, sticky=tk.W, padx=20, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="System Information",
            variable=self.include_system_info,
            font=("Arial", 10)
        ).grid(row=1, column=1, sticky=tk.W, padx=20, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Process Analysis",
            variable=self.include_process_info,
            font=("Arial", 10)
        ).grid(row=2, column=0, sticky=tk.W, padx=20, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Network Information",
            variable=self.include_network_info,
            font=("Arial", 10)
        ).grid(row=2, column=1, sticky=tk.W, padx=20, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Disk Forensics Results",
            variable=self.include_disk_analysis,
            font=("Arial", 10)
        ).grid(row=3, column=0, sticky=tk.W, padx=20, pady=5)
        
        tk.Checkbutton(
            options_frame,
            text="Memory Forensics Results",
            variable=self.include_memory_analysis,
            font=("Arial", 10)
        ).grid(row=3, column=1, sticky=tk.W, padx=20, pady=5)
        
        # Findings section
        findings_frame = tk.LabelFrame(self.frame, text="Investigation Findings", font=("Arial", 12))
        findings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        tk.Label(
            findings_frame,
            text="Enter your investigative findings and conclusions:",
            font=("Arial", 10)
        ).pack(pady=5)
        
        self.findings_text = tk.Text(findings_frame, height=10, font=("Arial", 10))
        self.findings_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generate button
        tk.Button(
            self.frame,
            text="Generate PDF Report",
            command=self.generate_report,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=30,
            pady=15
        ).pack(pady=20)
        
        # Tool documentation buttons
        doc_frame = tk.LabelFrame(self.frame, text="Tool Documentation", font=("Arial", 12))
        doc_frame.pack(fill=tk.X, padx=20, pady=10)
        
        button_frame = tk.Frame(doc_frame)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Autopsy Workflow",
            command=self.show_autopsy_workflow,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="FTK Imager Workflow",
            command=self.show_ftk_workflow,
            bg="#3498db",
            fg="white",
            padx=15,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
    
    def generate_report(self):
        """Generate PDF report."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "Please open a case first")
            return
        
        from reports.report_generator import ReportGenerator
        
        # Get findings
        findings = self.findings_text.get("1.0", tk.END).strip()
        
        # Create report options
        options = {
            'include_case_info': self.include_case_info.get(),
            'include_evidence': self.include_evidence.get(),
            'include_chain_of_custody': self.include_chain_of_custody.get(),
            'include_system_info': self.include_system_info.get(),
            'include_process_info': self.include_process_info.get(),
            'include_network_info': self.include_network_info.get(),
            'include_disk_analysis': self.include_disk_analysis.get(),
            'include_memory_analysis': self.include_memory_analysis.get(),
            'findings': findings
        }
        
        # Ask for output location
        default_filename = f"{self.app.current_case.case_id}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        output_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=default_filename,
            filetypes=[("PDF", "*.pdf")]
        )
        
        if not output_path:
            return
        
        self.app.set_status("Generating report...")
        self.app.root.update()
        
        try:
            generator = ReportGenerator(
                case_manager=self.app.case_manager,
                evidence_manager=self.app.evidence_manager,
                case_id=self.app.current_case.case_id
            )
            
            success = generator.generate_report(
                output_path=Path(output_path),
                options=options
            )
            
            if success:
                messagebox.showinfo("Success", f"Report generated successfully:\n{output_path}")
                
                # Ask to open
                if messagebox.askyesno("Open Report", "Would you like to open the report?"):
                    import os
                    os.startfile(output_path) if os.name == 'nt' else os.system(f'open "{output_path}"')
            else:
                messagebox.showerror("Error", "Failed to generate report")
        
        except Exception as e:
            messagebox.showerror("Error", f"Error generating report:\n{str(e)}")
        
        self.app.set_status("Ready")
    
    def show_autopsy_workflow(self):
        """Show Autopsy workflow documentation."""
        from integrations.autopsy import AutopsyIntegration
        
        window = tk.Toplevel(self.app.root)
        window.title("Autopsy Workflow")
        window.geometry("800x600")
        
        text = tk.Text(window, wrap=tk.WORD, font=("Courier", 9))
        scrollbar = tk.Scrollbar(window, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)
        
        text.insert("1.0", AutopsyIntegration.get_workflow_documentation())
        text.config(state=tk.DISABLED)
    
    def show_ftk_workflow(self):
        """Show FTK Imager workflow documentation."""
        from integrations.ftk_imager import FTKImagerIntegration
        
        window = tk.Toplevel(self.app.root)
        window.title("FTK Imager Workflow")
        window.geometry("800x600")
        
        text = tk.Text(window, wrap=tk.WORD, font=("Courier", 9))
        scrollbar = tk.Scrollbar(window, command=text.yview)
        text.config(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text.pack(fill=tk.BOTH, expand=True)
        
        text.insert("1.0", FTKImagerIntegration.get_workflow_documentation())
        text.config(state=tk.DISABLED)
    
    def refresh(self):
        """Refresh report tab."""
        pass