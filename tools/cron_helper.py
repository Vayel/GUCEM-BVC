from crontab import CronTab


def bold(txt):
    return "\033[1m" + txt + "\033[0m"


def red(txt):
    return "\033[31m" + txt + "\033[0m"


def create(create_job, job_comment):
    cron = CronTab(user=True)

    try:
        next(cron.find_comment(job_comment))
    except StopIteration:
        create_job(cron)
    else:
        print(bold(red(
            "A job with the comment '{}' already exists. See it with 'crontab "
            "-e'.".format(job_comment)
        )))
        return

    cron.write_to_user(user=True)
