import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.engines.campaign_runner import run_campaign_step
from app.services.vault import get_all_secrets
from app.db.task_repo import get_campaign

logger = logging.getLogger("uvicorn.error")
scheduler = AsyncIOScheduler()

async def execute_scheduled_step(campaign_id: str, day: int):
    """Worker function to run a campaign step autonomously."""
    logger.info(f"[Scheduler] Executing Campaign {campaign_id} Day {day}...")
    
    # 1. Fetch API keys from secure vault
    secrets = get_all_secrets()
    user_context = {"api_keys": secrets}
    
    try:
        # 2. Run the campaign step
        result = run_campaign_step(campaign_id, day, user_context)
        logger.info(f"[Scheduler] Step completed: {result.get('status', 'unknown')}")
    except Exception as e:
        logger.error(f"[Scheduler] Step failed: {e}")

def schedule_campaign(campaign_id: str, start_time: datetime = None):
    """Schedules all steps of a campaign to run once per day."""
    if not start_time:
        start_time = datetime.now() + timedelta(minutes=5) # start in 5 mins by default
    
    campaign = get_campaign(campaign_id)
    if not campaign:
        logger.error(f"Cannot schedule unknown campaign {campaign_id}")
        return
        
    plan = campaign.get("plan", [])
    for step in plan:
        day = step.get("day", 1)
        # Schedule for (start_time + day-1 days)
        run_time = start_time + timedelta(days=day-1)
        
        job_id = f"campaign_{campaign_id}_day_{day}"
        scheduler.add_job(
            execute_scheduled_step,
            'date',
            run_date=run_time,
            args=[campaign_id, day],
            id=job_id,
            replace_existing=True
        )
        logger.info(f"[Scheduler] Scheduled {job_id} for {run_time}")

def start_scheduler():
    if not scheduler.running:
        scheduler.start()
        logger.info("[Scheduler] Autonomous Campaign Runner initialized.")

def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("[Scheduler] Autonomous Campaign Runner stopped.")
