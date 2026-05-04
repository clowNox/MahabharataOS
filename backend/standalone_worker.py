import sys
import os
import asyncio
import logging
from datetime import datetime

# Add the parent directory to sys.path so we can import 'app'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.scheduler import start_scheduler, schedule_campaign
from app.db.task_repo import get_all_tasks

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("StandaloneWorker")

async def main():
    logger.info("--- MahabharataOS Standalone Worker Starting ---")
    
    # Initialize scheduler
    start_scheduler()
    
    logger.info("Worker active. Scanning for campaigns...")
    
    try:
        while True:
            # Note: This is a simple implementation. 
            # In a real app, we'd check a 'scheduled' flag in the DB.
            # For now, we'll just keep the process alive.
            await asyncio.sleep(60) 
    except (KeyboardInterrupt, SystemExit):
        logger.info("Worker stopping...")

if __name__ == "__main__":
    asyncio.run(main())
