from apscheduler.schedulers.background import BlockingScheduler
from apscheduler.triggers.combining import OrTrigger 
from apscheduler.triggers.cron import CronTrigger
from scheduler_utils import runUpdateSheet

job_defaults = {
    'coalesce': True,
    'max_instances': 3
}
scheduler = BlockingScheduler(timezone='Asia/Singapore')

# GMT-5 > 09:30am - 4pm
# GMT+8 > 10:30pm - 5am
trigger = OrTrigger([
    CronTrigger(minute='2', day_of_week='mon-fri', hour='9-18', timezone='Asia/Singapore'),
    CronTrigger(minute='32', day_of_week='mon-fri', hour='21', timezone='Asia/Singapore'),
    CronTrigger(minute='2', day_of_week='mon-fri', hour='22-23', timezone='Asia/Singapore'),
    CronTrigger(minute='2', day_of_week='tue-sat', hour='0-5', timezone='Asia/Singapore')
])

scheduler.add_job(runUpdateSheet, trigger=trigger, name='runUpdateSheet') # args=[]
scheduler.start()
