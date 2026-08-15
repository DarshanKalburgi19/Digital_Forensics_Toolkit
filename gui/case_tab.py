"""
Case management tab for GUI.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime


class CaseTab:
    """
    Case management tab.
    """
    
    def __init__(self, parent, app):
        """
        Initialize case tab.
        
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
            text="Case Management",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=10)
        
        # Button frame
        button_frame = tk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Button(
            button_frame,
            text="Create New Case",
            command=self.create_case_dialog,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Open Existing Case",
            command=self.open_case_dialog,
            bg="#3498db",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Refresh List",
            command=self.refresh_case_list,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Cases list
        list_frame = tk.LabelFrame(self.frame, text="Existing Cases", font=("Arial", 12))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Treeview for cases
        columns = ("Case ID", "Case Name", "Investigator", "Status", "Created")
        self.cases_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.cases_tree.heading(col, text=col)
            self.cases_tree.column(col, width=150)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.cases_tree.yview)
        self.cases_tree.configure(yscrollcommand=scrollbar.set)
        
        self.cases_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Double-click to open
        self.cases_tree.bind("<Double-1>", self.on_case_double_click)
        
        # Load cases
        self.refresh_case_list()
    
    def create_case_dialog(self):
        """Show create case dialog."""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Create New Case")
        dialog.geometry("500x400")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Case ID
        tk.Label(dialog, text="Case ID:", font=("Arial", 10)).pack(pady=5)
        case_id_entry = tk.Entry(dialog, font=("Arial", 10), width=40)
        case_id_entry.pack(pady=5)
        case_id_entry.insert(0, f"DF-{datetime.now().strftime('%Y')}-")
        
        # Case Name
        tk.Label(dialog, text="Case Name:", font=("Arial", 10)).pack(pady=5)
        case_name_entry = tk.Entry(dialog, font=("Arial", 10), width=40)
        case_name_entry.pack(pady=5)
        
        # Investigator
        tk.Label(dialog, text="Investigator:", font=("Arial", 10)).pack(pady=5)
        investigator_entry = tk.Entry(dialog, font=("Arial", 10), width=40)
        investigator_entry.pack(pady=5)
        
        # Description
        tk.Label(dialog, text="Description:", font=("Arial", 10)).pack(pady=5)
        description_text = tk.Text(dialog, font=("Arial", 10), width=40, height=5)
        description_text.pack(pady=5)
        
        def create_case():
            case_id = case_id_entry.get().strip()
            case_name = case_name_entry.get().strip()
            investigator = investigator_entry.get().strip()
            description = description_text.get("1.0", tk.END).strip()
            
            if not case_id or not case_name or not investigator:
                messagebox.showerror("Error", "Please fill all required fields")
                return
            
            case = self.app.case_manager.create_case(
                case_id=case_id,
                case_name=case_name,
                investigator=investigator,
                description=description
            )
            
            if case:
                messagebox.showinfo("Success", f"Case {case_id} created successfully")
                dialog.destroy()
                self.refresh_case_list()
                self.app.load_case(case_id)
            else:
                messagebox.showerror("Error", "Failed to create case. Case ID may already exist.")
        
        # Buttons
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(
            button_frame,
            text="Create Case",
            command=create_case,
            bg="#27ae60",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def open_case_dialog(self):
        """Show open case dialog."""
        cases = self.app.case_manager.list_cases()
        
        if not cases:
            messagebox.showinfo("No Cases", "No cases found. Create a new case first.")
            return
        
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Open Case")
        dialog.geometry("400x300")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select a case to open:", font=("Arial", 11)).pack(pady=10)
        
        # Listbox with cases
        listbox = tk.Listbox(dialog, font=("Arial", 10), height=10)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for case in cases:
            listbox.insert(tk.END, f"{case.case_id} - {case.case_name}")
        
        def open_selected():
            selection = listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a case")
                return
            
            selected_case = cases[selection[0]]
            dialog.destroy()
            self.app.load_case(selected_case.case_id)
        
        tk.Button(
            dialog,
            text="Open Case",
            command=open_selected,
            bg="#3498db",
            fg="white",
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def refresh_case_list(self):
        """Refresh the cases list."""
        # Clear existing
        for item in self.cases_tree.get_children():
            self.cases_tree.delete(item)
        
        # Load cases
        cases = self.app.case_manager.list_cases()
        
        for case in cases:
            created_date = datetime.fromisoformat(case.created_date).strftime('%Y-%m-%d %H:%M')
            self.cases_tree.insert("", tk.END, values=(
                case.case_id,
                case.case_name,
                case.investigator,
                case.status,
                created_date
            ))
    
    def on_case_double_click(self, event):
        """Handle double-click on case."""
        selection = self.cases_tree.selection()
        if selection:
            item = self.cases_tree.item(selection[0])
            case_id = item['values'][0]
            self.app.load_case(case_id)