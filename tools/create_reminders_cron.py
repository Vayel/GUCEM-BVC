import os

from crontab import CronTab

JOB_COMMENT = 'BVC reminders'
HERE = os.path.dirname(os.path.abspath(__file__))


def create():
    cron = CronTab(user=True)

    try:
        next(cron.find_comment(JOB_COMMENT))
    except StopIteration:
        job = cron.new(
            command=os.path.join(HERE, 'manage.sh launch_reminders'),
            comment=JOB_COMMENT,
        )
        job.day.every(1)
        job.hour.on(1)
        job.minute.on(0)
    else:
        print('A job with the comment {} already exists.'.format(JOB_COMMENT))
        return

    cron.write_to_user(user=True)
        

if __name__ == '__main__':
    create()
