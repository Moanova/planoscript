"""
Test T-001: Launch the application
ID: T-001
Title: Test FN001

Preconditions:
- The application is installed on a Windows PC
- The operating system meets the minimum requirements
- No instance of the application is already running

Steps:
1. Launch the application via its executable or desktop shortcut
2. Wait for the application window to appear

Expected Result:
- The application displays a welcome screen
- The welcome screen presents options including the creation of a new project
"""

import pytest
from pywinauto import Desktop
import time
import os


class TestFN001Launch:
    """Test suite for FN001: Launch the application"""

    @pytest.fixture(autouse=True)
    def setup_teardown(self, app_exe_path, kill_existing_instances):
        """Setup and teardown for each test in this class."""
        self.app_exe_path = app_exe_path
        # kill_existing_instances is handled by the fixture
        yield

    def test_launch_welcome_screen(self, launch_app):
        """
        Test T-001: Verify that the application displays the welcome screen on launch.
        
        This test:
        1. Launches the application using the provided executable path
        2. Waits for the main window to appear
        3. Verifies the welcome screen is displayed
        4. Verifies the "New Project" option is visible
        """
        app = launch_app
        
        # Wait for the main window to appear (timeout: 15s)
        main_window = None
        start_time = time.time()
        timeout = 15
        
        while time.time() - start_time < timeout:
            try:
                # Try to find the main window by title (supports multiple possible titles)
                desktop = Desktop(backend="uia")
                for window in desktop.windows():
                    window_text = window.window_text()
                    if window_text and any(
                        keyword.lower() in window_text.lower() 
                        for keyword in ["Planoscript", "Planoscript"]
                    ):
                        main_window = window
                        break
                
                if main_window:
                    break
            except Exception:
                pass
            time.sleep(0.5)
        
        assert main_window is not None, f"Main window not found after {timeout}s"
        
        # Verify welcome screen is displayed
        # Try to find elements that indicate the welcome screen
        welcome_indicators = [
            "welcome", "home", "accueil", 
            "new project", "nouveau projet", 
            "start", "démarrer"
        ]
        
        welcome_found = False
        new_project_found = False
        
        # Check window title and child elements
        window_text = main_window.window_text().lower()
        if any(indicator in window_text for indicator in welcome_indicators):
            welcome_found = True
        
        # Check child elements for welcome screen indicators
        try:
            for child in main_window.children():
                child_text = child.window_text().lower()
                if any(indicator in child_text for indicator in welcome_indicators[:3]):  # welcome/home/accueil
                    welcome_found = True
                if any(indicator in child_text for indicator in ["new project", "nouveau projet"]):
                    new_project_found = True
        except Exception:
            pass
        
        assert welcome_found, "Welcome screen indicators not found in the main window"
        assert new_project_found, "New Project option not found on the welcome screen"

    def test_launch_window_title(self, launch_app):
        """
        Additional test: Verify the window title contains expected keywords.
        """
        app = launch_app
        
        # Wait for the main window
        main_window = None
        start_time = time.time()
        timeout = 15
        
        while time.time() - start_time < timeout:
            try:
                desktop = Desktop(backend="uia")
                for window in desktop.windows():
                    window_text = window.window_text()
                    if window_text and "Planoscript" in window_text:
                        main_window = window
                        break
                
                if main_window:
                    break
            except Exception:
                pass
            time.sleep(0.5)
        
        assert main_window is not None, f"Main window not found after {timeout}s"
        
        # Verify window title
        window_title = main_window.window_text()
        assert "Planoscript" in window_title, f"Window title does not contain 'Planoscript': {window_title}"

    def test_launch_no_duplicate_instances(self, app_exe_path, kill_existing_instances):
        """
        Additional test: Verify that only one instance is running after launch.
        """
        from pywinauto import Application, Desktop
        
        # Launch a new instance
        app = Application(backend="uia").start(app_exe_path)
        
        # Count Planoscript windows
        exe_name = os.path.basename(app_exe_path).replace(".exe", "")
        desktop = Desktop(backend="uia")
        planoscript_windows = [
            w for w in desktop.windows() 
            if exe_name.lower() in w.window_text().lower()
        ]
        
        # Cleanup
        try:
            app.kill()
        except Exception:
            pass
        
        # Should have exactly one window (the one we just launched)
        assert len(planoscript_windows) == 1, \
            f"Expected 1 Planoscript window, found {len(planoscript_windows)}"
