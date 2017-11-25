from django.conf import settings

def format_mail_subject(subject, reminder=False):
    tags = ['[{}]'.format(tag) for tag in settings.BVC_MAIL_TAGS]
    if reminder:
        tags.append('[RAPPEL]')

    return ''.join(tags) + ' ' + subject
