import os

from cron_helper import create

JOB_COMMENT = 'BVC reminders'
HERE = os.path.dirname(os.path.abspath(__file__))


def create_job(cron):
    job = cron.new(
        command=os.path.join(HERE, 'manage.sh launch_reminders'),
        comment=JOB_COMMENT,
    )
    job.day.every(1)
    job.hour.on(1)
    job.minute.on(0)


if __name__ == '__main__':
    create(create_job, JOB_COMMENT)
