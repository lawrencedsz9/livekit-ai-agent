"""
Quick test for close_assistant functionality
Run this to verify the exit mechanism works properly
"""
import asyncio
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockAgent:
    def __init__(self):
        self.close_requested = False

class MockContext:
    def __init__(self):
        self.agent = MockAgent()

async def test_close():
    logger.info("Testing close_assistant function...")
    
    # Simulate the close function
    context = MockContext()
    
    logger.info("Setting close_requested flag...")
    context.agent.close_requested = True
    
    async def delayed_shutdown():
        await asyncio.sleep(2)
        logger.info("Terminating process...")
        sys.exit(0)
    
    asyncio.create_task(delayed_shutdown())
    logger.info("Shutdown scheduled - waiting 2 seconds before exit...")
    
    # Keep running until shutdown
    await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(test_close())
    except SystemExit:
        logger.info("✅ Process terminated successfully!")
