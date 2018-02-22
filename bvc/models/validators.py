from django.core.exceptions import ValidationError
from django.conf import settings

def validate_voucher_amount_multiple(value):
    if not value:
        raise ValidationError("Le montant ne peut être nul.")

    if value % settings.VOUCHER_AMOUNT_MULTIPLE:
        raise ValidationError(
            "{} n'est pas un multiple de {}.".format(
                value,
                settings.VOUCHER_AMOUNT_MULTIPLE
            )
        )


def validate_cash_amount_multiple(value):
    if value % settings.BANK_DEPOSIT_CASH_MULTIPLE:
        raise ValidationError(
            "{} n'est pas un multiple de {} (valeur minimale d'un billet).".format(
                value,
                settings.BANK_DEPOSIT_CASH_MULTIPLE
            )
        )
