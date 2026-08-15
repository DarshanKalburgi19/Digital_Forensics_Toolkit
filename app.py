"""
Digital Forensics Toolkit - Main Application Entry Point
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import ForensicToolkitGUI
from core.logger import setup_logger

logger = setup_logger("main")


def main():
    """
    Main application entry point.
    """
    try:
        logger.info("Starting Digital Forensics Toolkit")
        
        # Create and run GUI
        app = ForensicToolkitGUI()
        app.run()
        
        logger.info("Application closed")
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "Fatal Error",
            f"An unexpected error occurred:\n{str(e)}\n\nCheck logs for details."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()