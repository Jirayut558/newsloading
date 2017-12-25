from apscheduler.schedulers.blocking import BlockingScheduler
import loadscript

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', hour=23)
def scheduled_job():
    loadscript.main()

sched.start()
