from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .models import Accounts, deactivate_expired_accounts

def start_scheduler():
    scheduler = BackgroundScheduler()
    # Run the task daily at midnight
    trigger = CronTrigger(hour=0, minute=0)
    scheduler.add_job(deactivate_expired_accounts, trigger)
    scheduler.start()
