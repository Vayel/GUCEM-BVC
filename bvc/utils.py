from django.conf import settings

def format_mail_subject(subject):
    tags = ''

    for tag in settings.BVC_MAIL_TAGS:
        tags += '[{}]'.format(tag)

    return tags + subject
