from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.base import JobLookupError
from app.common.function import update_meal_board_views

sched = BackgroundScheduler()
sched.start()
# sched.add_job(lambda: update_meal_board_views(), 'cron', second='50', id="update_meal_board_views")
sched.add_job(lambda: update_meal_board_views(), 'cron', minute='*/10', id="update_meal_board_views")


# from flask_apscheduler import APScheduler as _BaseAPScheduler
# # from flask_apscheduler import Sche
#
#
# class APScheduler(_BaseAPScheduler):
#     def run_job(self, id, jobstore=None):
#         with self.app.app_context():
#             super().run_job(id=id, jobstore=jobstore)
#
# sched = APScheduler()
# sched.add_job( {
#             'id': 'job1',
#             'func': 'app.tasks:job1',
#             'trigger': 'cron',
#             'day': 7,
#             'hour': 8,
#         })
#
#
