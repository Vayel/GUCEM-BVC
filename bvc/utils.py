from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

def format_mail_subject(subject):
    tags = ''

    for tag in settings.BVC_MAIL_TAGS:
        tags += '[{}]'.format(tag)

    return tags + subject

# TODO
def get_cmd_discount(cmd):
    if isinstance(cmd, models.command.CommissionCommand) or cmd.member.vip:
        return settings.VIP_DISCOUNT
    elif cmd.member.club == models.user.Member.ESMUG:
        return settings.ESMUG_DISCOUNT
    elif cmd.member.club == models.user.Member.GUCEM: 
        return settings.GUCEM_DISCOUNT

    raise ValueError("cmd object must be a member command or a commission command.")

def get_cmd_price(cmd):
    return (1 - get_cmd_discount(cmd)) * cmd.amount

def get_cmd_email(cmd):
    if isinstance(cmd, models.command.MemberCommand):
        return cmd.member.user.email
    elif isinstance(cmd, models.command.CommissionCommand):
        return cmd.commission.user.email

    raise ValueError("cmd object must be a member command or a commission command.")

def get_voucher_stock():
    try:
        return models.voucher.Operation.objects.latest('id').stock
    except ObjectDoesNotExist:
        return 0
