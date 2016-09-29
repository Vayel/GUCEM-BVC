from django.core.exceptions import ValidationError
from django.conf import settings

def validate_amount_multiple(value):
    if value % settings.VOUCHER_AMOUNT_MULTIPLE:
        raise ValidationError(
            "{} n'est pas un multiple de {}".format(
                value,
                settings.VOUCHER_AMOUNT_MULTIPLE
            )
        )
