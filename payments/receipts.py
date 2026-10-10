# payments/receipts.py
from decimal import Decimal

def _registration_context(payment):
    reg = payment.registration_payment
    athletes = reg.athletes.all()
    unit_price = Decimal("3000")
    flat_fee = Decimal("500")
    subtotal = unit_price * athletes.count()
    return {
        'title': 'Athlete Registration Receipt',
        'recipient_name': reg.school.name,
        'recipient_address': f"{reg.school.district.zone} {reg.school.district}",
        'line_items': [
            {
                'service': 'Athlete Registration', 'description': 'Registration fees',
                'qty': athletes.count(), 'cost': unit_price, 'total': subtotal,
                'sub_items': [f"{a.fname} {a.lname}" for a in athletes],
            },
            {
                'service': 'Processing Fee', 'description': 'Transaction processing fee',
                'qty': 1, 'cost': flat_fee, 'total': flat_fee,
            },
        ],
        'subtotal': subtotal + flat_fee,
    }

def _transfer_context(payment):
    tp = payment.transfer_payments.select_related(
        "transfer__requester__district__zone", "transfer__athlete"
    ).first()
    if tp is None:
        raise ValueError(f"No TransferPayment found for payment {payment.id}")

    transfer = tp.transfer
    return {
        'title': 'Athlete Transfer Receipt',
        'recipient_name': transfer.requester.name,
        'recipient_address': f"{transfer.requester.district.zone} {transfer.requester.district}",
        'line_items': [{
            'service': 'Athlete Transfer', 'description': str(transfer.athlete),
            'qty': 1, 'cost': payment.amount, 'total': payment.amount,
        }],
        'subtotal': payment.amount,
    }

def _edit_context(payment):
    edit = payment.edit_request
    return {
        'title': 'Athlete Edit Request Receipt',
        'recipient_name': edit.school.name,
        'recipient_address': f"{edit.school.district.zone} {edit.school.district}",
        'line_items': [{
            'service': 'Athlete Edit Request', 'description': str(edit.athlete),
            'qty': 1, 'cost': payment.amount, 'total': payment.amount,
        }],
        'subtotal': payment.amount,
    }

RECEIPT_CONTEXT_BUILDERS = {
    'REGISTRATION': _registration_context,
    'TRANSFER': _transfer_context,
    'EDIT': _edit_context,
}