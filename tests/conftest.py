import pytest
import time
import os
from PySide6.QtWidgets import QApplication
from unittest.mock import patch

def pytest_configure(config):
    """Configure pytest with timeout settings."""
    config.addinivalue_line(
        "markers", "timeout: timeout for each test in seconds"
    )
    
    # Disable deferred loading during tests for backward compatibility
    os.environ['ENABLE_DEFERRED_LOAD'] = 'false'

@pytest.fixture
def timeout_15s(request):
    """Fixture to apply 15 second timeout to tests."""
    timeout_value = 15
    
    # Import here to avoid import errors if timeout module isn't available
    try:
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Test exceeded {timeout_value} second timeout")
        
        # Set the signal handler and alarm
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_value)
        
        yield
        
        # Disable the alarm
        signal.alarm(0)
    except (ImportError, AttributeError):
        # signal.alarm not available on Windows, use pytest-timeout instead
        yield

def wait_for_deferred_load(editor, timeout=5):
    """Wait for deferred file loading to complete."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Process events to allow timers to run
        QApplication.processEvents()
        
        # Check if loading is complete
        if (not hasattr(editor, '_pending_file_load') or editor._pending_file_load is None) and \
           not hasattr(editor, '_load_chunks'):
            return True
        
        time.sleep(0.001)
    
    return False

# Add timeout marker to all tests automatically
def pytest_collection_modifyitems(config, items):
    """Add timeout to all tests."""
    timeout_value = 15
    for item in items:
        # Skip timeout for timing tests (they need much longer)
        if 'test_timing' in item.nodeid:
            item.add_marker(pytest.mark.timeout(600))  # 10 minutes for timing tests
        else:
            item.add_marker(pytest.mark.timeout(timeout_value))
