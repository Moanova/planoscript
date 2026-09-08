"""
Global pytest configuration for Planoscript tests.
This file provides fixtures and options used across all test modules.
"""

import pytest
import os


def pytest_addoption(parser):
    """Add custom command line options for pytest."""
    parser.addoption(
        "--app-path",
        action="store",
        default=None,
        help="Path to the Planoscript executable (e.g., C:/Program Files/Planoscript/planoscript.exe)"
    )
    parser.addoption(
        "--capture-screenshots",
        action="store_true",
        default=False,
        help="Capture screenshots on test failures"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run tests in headless mode (no visible UI)"
    )


@pytest.fixture(scope="session")
def app_exe_path(request):
    """Global fixture for the Planoscript executable path."""
    path = request.config.getoption("--app-path")
    if path is None:
        # Try environment variable
        path = os.getenv("PLANOSCRIPT_PATH")
    if path is None:
        # Default path (Windows)
        path = r"C:\Program Files\Planoscript\planoscript.exe"
    if not os.path.exists(path):
        pytest.skip(f"Planoscript executable not found at: {path}")
    return path


@pytest.fixture(scope="module")
def kill_existing_instances(app_exe_path):
    """Close all existing instances of Planoscript before running tests."""
    from pywinauto import Desktop
    import time
    
    exe_name = os.path.basename(app_exe_path).replace(".exe", "")
    
    try:
        desktop = Desktop(backend="uia")
        for window in desktop.windows():
            if exe_name.lower() in window.window_text().lower():
                window.close()
        time.sleep(1)  # Wait for windows to close
    except Exception:
        pass  # Ignore errors during cleanup
    
    yield
    
    # Additional cleanup after tests
    try:
        desktop = Desktop(backend="uia")
        for window in desktop.windows():
            if exe_name.lower() in window.window_text().lower():
                window.close()
    except Exception:
        pass


@pytest.fixture(scope="module")
def launch_app(app_exe_path, kill_existing_instances):
    """Launch Planoscript application and return the Application object."""
    from pywinauto import Application
    
    app = Application(backend="uia").start(app_exe_path)
    yield app
    
    # Teardown: Close the application
    try:
        app.kill()
    except Exception:
        pass
