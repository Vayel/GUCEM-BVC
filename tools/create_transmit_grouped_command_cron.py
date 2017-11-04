import os

from cron_helper import create

JOB_COMMENT = 'BVC transmit grouped command reminder'
HERE = os.path.dirname(os.path.abspath(__file__))


def create_job(cron):
    job = cron.new(
        command=os.path.join(HERE, 'manage.sh transmit_grouped_command_reminder'),
        comment=JOB_COMMENT,
    )
    job.day.every(1)
    job.hour.on(2)
    job.minute.on(10)
        

if __name__ == '__main__':
    create(create_job, JOB_COMMENT)
