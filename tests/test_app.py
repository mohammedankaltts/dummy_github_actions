import logging
import pytest

# Configure logger inside your test file
logger = logging.getLogger(__name__)

def test_successful_login():
    """A standard test that passes and prints basic logs."""
    print("\n[STDOUT] Navigating to login page...")
    logger.info("Sending authentication request for user: admin")
    
    auth_status = True
    
    logger.info("Authentication response received: 200 OK")
    assert auth_status is True


def test_failed_payment():
    """A test that fails intentionally to capture tracebacks and error logs."""
    print("\n[STDOUT] Processing shopping cart checkout...")
    logger.info("Attempting to charge credit card ending in 4242...")
    logger.warning("Bank API timeout detected, retrying connection...")
    
    account_balance = 50
    item_cost = 120
    
    logger.error("Transaction declined: Insufficient funds.")
    # This will fail and generate a traceback in your log file
    assert account_balance >= item_cost


@pytest.mark.skip(reason="Database maintenance in progress, skipping integration test.")
def test_database_connection():
    """A test marked as skipped to see how the summary table handles it."""
    pass


def test_data_processing_performance():
    """A complex loop execution to simulate test duration and detailed debug logging."""
    logger.info("Loading dataset of 10,000 items...")
    processed_count = 0
    
    for i in range(5):
        logger.debug(f"Processing chunk {i+1}/5...")
        processed_count += 2000
        
    logger.info("Dataset processing complete.")
    assert processed_count == 10000
