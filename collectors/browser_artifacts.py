"""
Browser artifact collector for forensic analysis.

SECURITY NOTE: This module only extracts browsing history and download metadata.
It does NOT extract, decrypt, or expose:
- Saved passwords
- Authentication cookies
- Session tokens
- Payment information
- Other credentials
"""

import sqlite3
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import tempfile
from core.logger import setup_logger

logger = setup_logger("browser_artifacts")


class BrowserHistory:
    """
    Represents a browser history entry.
    """
    
    def __init__(
        self,
        url: str,
        title: str,
        visit_time: Optional[str] = None,
        visit_count: int = 0
    ):
        """Initialize browser history entry."""
        self.url = url
        self.title = title
        self.visit_time = visit_time
        self.visit_count = visit_count
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'url': self.url,
            'title': self.title,
            'visit_time': self.visit_time,
            'visit_count': self.visit_count
        }


class BrowserDownload:
    """
    Represents a browser download entry.
    """
    
    def __init__(
        self,
        url: str,
        filename: str,
        download_time: Optional[str] = None
    ):
        """Initialize browser download entry."""
        self.url = url
        self.filename = filename
        self.download_time = download_time
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'url': self.url,
            'filename': self.filename,
            'download_time': self.download_time
        }


class BrowserArtifactsCollector:
    """
    Collect browser artifacts safely.
    
    IMPORTANT: This is for educational purposes. Only analyzes metadata.
    Does NOT decrypt or extract credentials.
    """
    
    # Common browser paths (Windows)
    CHROME_PATHS = [
        Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default",
        Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Profile 1"
    ]
    
    EDGE_PATHS = [
        Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default"
    ]
    
    FIREFOX_PATHS = [
        Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
    ]
    
    @staticmethod
    def collect_chrome_history(profile_path: Optional[Path] = None) -> List[BrowserHistory]:
        """
        Collect Chrome browsing history.
        
        Args:
            profile_path: Optional specific profile path
            
        Returns:
            List of BrowserHistory objects
        """
        history = []
        
        # Determine paths to check
        paths_to_check = [profile_path] if profile_path else BrowserArtifactsCollector.CHROME_PATHS
        
        for path in paths_to_check:
            if not path or not path.exists():
                continue
            
            history_db = path / "History"
            
            if not history_db.exists():
                continue
            
            try:
                # Create temporary copy (database may be locked)
                with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp:
                    tmp_path = Path(tmp.name)
                
                shutil.copy2(history_db, tmp_path)
                
                # Query history
                conn = sqlite3.connect(tmp_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT url, title, last_visit_time, visit_count
                    FROM urls
                    ORDER BY last_visit_time DESC
                    LIMIT 1000
                ''')
                
                for row in cursor.fetchall():
                    url, title, visit_time, visit_count = row
                    
                    # Convert Chrome timestamp (microseconds since 1601-01-01)
                    if visit_time:
                        try:
                            # Chrome epoch is 1601-01-01
                            epoch_start = datetime(1601, 1, 1)
                            visit_datetime = epoch_start + timedelta(microseconds=visit_time)
                            visit_time_str = visit_datetime.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            visit_time_str = str(visit_time)
                    else:
                        visit_time_str = None
                    
                    history.append(BrowserHistory(
                        url=url,
                        title=title or "No Title",
                        visit_time=visit_time_str,
                        visit_count=visit_count or 0
                    ))
                
                conn.close()
                tmp_path.unlink()  # Delete temporary file
                
                logger.info(f"Collected {len(history)} Chrome history entries")
                break  # Found valid database
                
            except sqlite3.DatabaseError as e:
                logger.warning(f"Database locked or corrupted: {history_db}")
                continue
            except Exception as e:
                logger.error(f"Error collecting Chrome history: {str(e)}")
                continue
        
        return history
    
    @staticmethod
    def collect_edge_history(profile_path: Optional[Path] = None) -> List[BrowserHistory]:
        """
        Collect Edge browsing history (same format as Chrome).
        
        Args:
            profile_path: Optional specific profile path
            
        Returns:
            List of BrowserHistory objects
        """
        # Edge uses same database format as Chrome
        paths_to_check = [profile_path] if profile_path else BrowserArtifactsCollector.EDGE_PATHS
        
        history = []
        
        for path in paths_to_check:
            if not path or not path.exists():
                continue
            
            # Temporarily set Chrome path for collection
            original_chrome_paths = BrowserArtifactsCollector.CHROME_PATHS
            BrowserArtifactsCollector.CHROME_PATHS = [path]
            
            history = BrowserArtifactsCollector.collect_chrome_history(path)
            
            BrowserArtifactsCollector.CHROME_PATHS = original_chrome_paths
            
            if history:
                logger.info(f"Collected {len(history)} Edge history entries")
                break
        
        return history
    
    @staticmethod
    def collect_firefox_history(profile_path: Optional[Path] = None) -> List[BrowserHistory]:
        """
        Collect Firefox browsing history.
        
        Args:
            profile_path: Optional specific profile path
            
        Returns:
            List of BrowserHistory objects
        """
        history = []
        
        # Find Firefox profiles
        if profile_path:
            profile_dirs = [profile_path]
        else:
            profile_dirs = []
            for base_path in BrowserArtifactsCollector.FIREFOX_PATHS:
                if base_path.exists():
                    profile_dirs.extend([d for d in base_path.iterdir() if d.is_dir()])
        
        for profile_dir in profile_dirs:
            places_db = profile_dir / "places.sqlite"
            
            if not places_db.exists():
                continue
            
            try:
                # Create temporary copy
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sqlite') as tmp:
                    tmp_path = Path(tmp.name)
                
                shutil.copy2(places_db, tmp_path)
                
                # Query history
                conn = sqlite3.connect(tmp_path)
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT url, title, last_visit_date, visit_count
                    FROM moz_places
                    WHERE last_visit_date IS NOT NULL
                    ORDER BY last_visit_date DESC
                    LIMIT 1000
                ''')
                
                for row in cursor.fetchall():
                    url, title, visit_time, visit_count = row
                    
                    # Convert Firefox timestamp (microseconds since Unix epoch)
                    if visit_time:
                        try:
                            visit_datetime = datetime.fromtimestamp(visit_time / 1000000)
                            visit_time_str = visit_datetime.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            visit_time_str = str(visit_time)
                    else:
                        visit_time_str = None
                    
                    history.append(BrowserHistory(
                        url=url,
                        title=title or "No Title",
                        visit_time=visit_time_str,
                        visit_count=visit_count or 0
                    ))
                
                conn.close()
                tmp_path.unlink()
                
                logger.info(f"Collected {len(history)} Firefox history entries")
                break
                
            except Exception as e:
                logger.error(f"Error collecting Firefox history: {str(e)}")
                continue
        
        return history
    
    @staticmethod
    def collect_all() -> Dict:
        """
        Collect history from all detected browsers.
        
        Returns:
            Dictionary with browser histories
        """
        logger.info("Collecting browser artifacts...")
        
        return {
            'collection_timestamp': datetime.now().isoformat(),
            'chrome_history': [h.to_dict() for h in BrowserArtifactsCollector.collect_chrome_history()],
            'edge_history': [h.to_dict() for h in BrowserArtifactsCollector.collect_edge_history()],
            'firefox_history': [h.to_dict() for h in BrowserArtifactsCollector.collect_firefox_history()]
        }