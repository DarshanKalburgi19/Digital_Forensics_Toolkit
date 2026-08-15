"""
Evidence management tab for GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path


class EvidenceTab:
    """
    Evidence management tab.
    """
    
    def __init__(self, parent, app):
        """
        Initialize evidence tab.
        
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
            text="Evidence Management",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            button_frame,
            text="Add Evidence",
            command=self.add_evidence_dialog,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Verify Integrity",
            command=self.verify_selected_evidence,
            bg="#e67e22",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="View Chain of Custody",
            command=self.view_chain_of_custody,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Evidence list
        list_frame = tk.LabelFrame(self.frame, text="Evidence Items", font=("Arial", 12))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview for evidence
        columns = ("ID", "Filename", "Type", "Size", "SHA-256", "Added")
        self.evidence_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.evidence_tree.heading("ID", text="ID")
        self.evidence_tree.heading("Filename", text="Filename")
        self.evidence_tree.heading("Type", text="Type")
        self.evidence_tree.heading("Size", text="Size")
        self.evidence_tree.heading("SHA-256", text="SHA-256")
        self.evidence_tree.heading("Added", text="Added")
        
        self.evidence_tree.column("ID", width=50)
        self.evidence_tree.column("Filename", width=200)
        self.evidence_tree.column("Type", width=120)
        self.evidence_tree.column("Size", width=100)
        self.evidence_tree.column("SHA-256", width=300)
        self.evidence_tree.column("Added", width=150)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.evidence_tree.yview)
        self.evidence_tree.configure(yscrollcommand=scrollbar.set)
        
        self.evidence_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def add_evidence_dialog(self):
        """Show add evidence dialog."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "Please open or create a case first")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Evidence File",
            filetypes=[
                ("All Files", "*.*"),
                ("Forensic Images", "*.e01 *.e02 *.001 *.dd *.raw *.img"),
                ("Memory Dumps", "*.mem *.dmp *.vmem")
            ]
        )
        
        if not file_path:
            return
        
        # Get investigator name
        investigator = self.app.current_case.investigator
        
        # Ask for notes
        notes = tk.simpledialog.askstring(
            "Evidence Notes",
            "Enter notes about this evidence (optional):",
            parent=self.app.root
        )
        
        # Add evidence
        self.app.set_status("Adding evidence...")
        self.app.root.update()
        
        evidence = self.app.evidence_manager.add_evidence(
            case_id=self.app.current_case.case_id,
            source_path=file_path,
            investigator=investigator,
            notes=notes or "",
            copy_file=True
        )
        
        if evidence:
            messagebox.showinfo("Success", f"Evidence added: {evidence.filename}")
            self.refresh()
        else:
            messagebox.showerror("Error", "Failed to add evidence")
        
        self.app.set_status("Ready")
    
    def verify_selected_evidence(self):
        """Verify integrity of selected evidence."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "No case loaded")
            return
        
        selection = self.evidence_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select evidence to verify")
            return
        
        item = self.evidence_tree.item(selection[0])
        evidence_id = int(item['values'][0])
        
        self.app.set_status("Verifying integrity...")
        self.app.root.update()
        
        verified, message = self.app.evidence_manager.verify_integrity(
            evidence_id=evidence_id,
            investigator=self.app.current_case.investigator
        )
        
        if verified:
            messagebox.showinfo("Integrity Verified", message)
        else:
            messagebox.showwarning("Integrity Check", message)
        
        self.app.set_status("Ready")
    
    def view_chain_of_custody(self):
        """View chain of custody for selected evidence."""
        if not self.app.current_case:
            messagebox.showwarning("Warning", "No case loaded")
            return
        
        from core.chain_of_custody import ChainOfCustody
        
        case_dir = self.app.case_manager.get_case_directory(self.app.current_case.case_id)
        coc = ChainOfCustody(case_dir)
        entries = coc.get_entries()
        
        # Create dialog
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Chain of Custody")
        dialog.geometry("900x600")
        
        # Treeview
        columns = ("Timestamp", "Evidence ID", "Action", "Investigator", "Description")
        tree = ttk.Treeview(dialog, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
        
        tree.column("Timestamp", width=150)
        tree.column("Evidence ID", width=100)
        tree.column("Action", width=150)
        tree.column("Investigator", width=120)
        tree.column("Description", width=300)
        
        scrollbar = tk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Populate
        for entry in entries:
            tree.insert("", tk.END, values=(
                entry.timestamp,
                entry.evidence_id,
                entry.action,
                entry.investigator,
                entry.description
            ))
        
        # Export buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def export_json():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON", "*.json")]
            )
            if file_path:
                coc.export_json(Path(file_path))
                messagebox.showinfo("Success", "Exported to JSON")
        
        def export_csv():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")]
            )
            if file_path:
                coc.export_csv(Path(file_path))
                messagebox.showinfo("Success", "Exported to CSV")
        
        tk.Button(button_frame, text="Export JSON", command=export_json).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Export CSV", command=export_csv).pack(side=tk.LEFT, padx=5)
    
    def refresh(self):
        """Refresh evidence list."""
        # Clear existing
        for item in self.evidence_tree.get_children():
            self.evidence_tree.delete(item)
        
        if not self.app.current_case:
            return
        
        # Load evidence
        evidence_list = self.app.evidence_manager.list_evidence(self.app.current_case.case_id)
        
        for evidence in evidence_list:
            # Format size
            size_mb = evidence.file_size / (1024 * 1024)
            size_str = f"{size_mb:.2f} MB"
            
            # Truncate hash for display
            sha256_display = evidence.sha256_hash[:16] + "..." if evidence.sha256_hash else "N/A"
            
            self.evidence_tree.insert("", tk.END, values=(
                evidence.evidence_id,
                evidence.filename,
                evidence.evidence_type,
                size_str,
                sha256_display,
                evidence.added_date[:16]
            ))