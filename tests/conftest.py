import os
import logging
import pytest
import re

# Directory where individual test logs will be saved
LOG_DIR = "test-logs"
os.makedirs(LOG_DIR, exist_ok=True)

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Execute the actual test step (setup, call, or teardown)
    outcome = yield
    report = outcome.get_result()
    
    # We only care about the actual test execution phase ('call')
    if report.when == "call":
        # Make the test name safe for URLs/Filenames (removes brackets, slashes, etc.)
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', item.nodeid)
        log_file_path = os.path.join(LOG_DIR, f"{safe_name}.log")
        
        # Capture stdout, stderr, and Python log messages
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write(f"=== Test Case: {item.nodeid} ===\n")
            f.write(f"Outcome: {report.outcome.upper()}\n")
            f.write(f"Duration: {report.duration:.2f}s\n\n")
            
            if report.longrepr:
                f.write("=== Traceback / Errors ===\n")
                f.write(str(report.longrepr) + "\n\n")
                
            f.write("=== Captured Console Logs ===\n")
            f.write(report.caplog.text or "No logging captured.\n")
