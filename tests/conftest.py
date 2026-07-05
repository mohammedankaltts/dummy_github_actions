import os
import logging
import pytest
import re
import subprocess
import time

# Directory where individual test logs and pcaps will be saved
LOG_DIR = "test-logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Global dictionary to track background tcpdump processes per test item
tcpdump_processes = {}

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Fires right before the test case starts executing."""
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', item.nodeid)
    pcap_path = os.path.join(LOG_DIR, f"{safe_name}.pcap")
    
    # Start tcpdump in the background capturing all traffic on the loopback and local eth interfaces
    # We use -w to write the raw packets directly to a file
    try:
        cmd = ["sudo", "tcpdump", "-i", "any", "-w", pcap_path, "-U"]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tcpdump_processes[item.nodeid] = proc
        time.sleep(0.2) # Give tcpdump a fraction of a second to hook into the interface card
    except Exception as e:
        print(f"\n[ERROR] Failed to start tcpdump for {item.nodeid}: {e}")

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Executes during the test execution and captures logs."""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call":
        # 1. Gracefully terminate the packet capture for this specific test case
        proc = tcpdump_processes.get(item.nodeid)
        if proc:
            subprocess.run(["sudo", "kill", "-SIGINT", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            proc.wait()
            
            # Change permissions so GitHub actions can copy the file out of root ownership
            safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', item.nodeid)
            pcap_path = os.path.join(LOG_DIR, f"{safe_name}.pcap")
            if os.path.exists(pcap_path):
                subprocess.run(["sudo", "chmod", "666", pcap_path])
        
        # 2. Save text log file output
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', item.nodeid)
        log_file_path = os.path.join(LOG_DIR, f"{safe_name}.log")
        
        with open(log_file_path, "w", encoding="utf-8") as f:
            f.write(f"=== Test Case: {item.nodeid} ===\n")
            f.write(f"Outcome: {report.outcome.upper()}\n")
            f.write(f"Duration: {report.duration:.2f}s\n\n")
            
            if report.longrepr:
                f.write("=== Traceback / Errors ===\n")
                f.write(str(report.longrepr) + "\n\n")
                
            f.write("=== Captured Console Logs ===\n")
            f.write(report.caplog.text or "No logging captured.\n")
