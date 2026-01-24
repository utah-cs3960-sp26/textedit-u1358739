import pytest

def pytest_configure(config):
    """Configure pytest with timeout settings."""
    config.addinivalue_line(
        "markers", "timeout: timeout for each test in seconds"
    )

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

# Add timeout marker to all tests automatically
def pytest_collection_modifyitems(config, items):
    """Add timeout to all tests."""
    timeout_value = 15
    for item in items:
        item.add_marker(pytest.mark.timeout(timeout_value))
