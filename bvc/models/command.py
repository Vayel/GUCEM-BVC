PLACED_STATE = 'placed'
PREPARED_STATE = 'prepared'
CANCELLED_STATE = 'cancelled'
RECEIVED_STATE = 'received'
SOLD_STATE = 'sold'
TO_BE_BANKED_STATE = 'to_be_banked'
BANKED_STATE = 'banked'
GIVEN_STATE = 'given'
CHECK_PAYMENT = 'check'
CASH_PAYMENT = 'cash'


class InvalidState(Exception): pass
class InvalidPaymentType(Exception): pass
