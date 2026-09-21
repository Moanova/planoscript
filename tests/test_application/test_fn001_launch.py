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
        # Indicators that suggest the welcome screen is displayed.
        welcome_indicators = [
            "welcome", "home", "accueil", "start", "démarrer",
            "build the plan", "start your new project",
        ]
        # Indicators that the "new project" entry point is offered.
        new_project_indicators = ["new project", "nouveau projet"]

        welcome_found = False
        new_project_found = False

        # Check the window title first.
        window_text = main_window.window_text().lower()
        if any(indicator in window_text for indicator in welcome_indicators):
            welcome_found = True
        if any(indicator in window_text for indicator in new_project_indicators):
            new_project_found = True

        # Then walk the whole UI tree (descendants, not just direct children)
        # so that nested widgets such as the welcome QLabel and menu items
        # are taken into account.
        try:
            for desc in main_window.descendants():
                desc_text = desc.window_text().lower()
                if any(indicator in desc_text for indicator in welcome_indicators):
                    welcome_found = True
                if any(indicator in desc_text for indicator in new_project_indicators):
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

    def test_launch_no_duplicate_instances(self, app_exe_path, app_window_name, kill_existing_instances):
        """
        Additional test: Verify that only one instance is running after launch.
        """
        from pywinauto import Application, Desktop

        # Launch a new instance (wait_for_idle=False: python.exe is not a GUI process)
        app = Application(backend="uia").start(app_exe_path, wait_for_idle=False)

        # Give the second instance a moment to (fail to) show its window
        time.sleep(2)

        # Count Planoscript windows
        desktop = Desktop(backend="uia")
        planoscript_windows = [
            w for w in desktop.windows()
            if app_window_name.lower() in w.window_text().lower()
        ]

        # Debug: show what the test actually sees
        print(f"\n[debug] app_exe_path = {app_exe_path!r}")
        print(f"[debug] app_window_name = {app_window_name!r}")
        print(f"[debug] matched windows = {len(planoscript_windows)}")
        for w in planoscript_windows:
            print(f"[debug]   - {w.window_text()!r}")
        try:
            print(f"[debug] second process alive? pid={app.process_id()} "
                  f"alive={app.is_process_running()}")
        except Exception as exc:
            print(f"[debug] second process status unavailable: {exc!r}")
        
        # Cleanup
        try:
            app.kill()
        except Exception:
            pass
        
        # Should have exactly one window (the one we just launched)
        assert len(planoscript_windows) == 1, \
            f"Expected 1 Planoscript window, found {len(planoscript_windows)}"
