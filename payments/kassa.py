import uuid

from yookassa import Configuration, Payment
from model.preferences import ins
import datetime

from settings import config

Configuration.account_id = config.ACCOUNT_ID
Configuration.secret_key = config.SECRET_KEY


def create_text(amount, name, description):
    return f'{name}\nЦена: {amount}.00 RUB\n\n{description}'


def create_payment(amount, name, message_id: int = None, user_id: int = None):
    idempotence_key = uuid.uuid4()
    payment = Payment.create({
        "amount": {
            "value": f"{amount}",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            # "return_url": f"https://t.me/wishnya_wish_bot?start=payment_{message_id}"
            # "return_url": f"https://t.me/lismus_bot?start=payment_{message_id}"
            "return_url": f"https://t.me/wishnya_wish_bot"
        },
        "capture": True,
        "description": f"{name}",
        "metadata":
            {
                'order_id': f'{user_id}'
            }
    }, idempotence_key)
    ins(id=user_id,
        payment_id=payment.id,
        product_name=name,
        status='pending',
        date=str(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")),
        idempotence_key=idempotence_key,
        message_id=message_id)
    return payment.confirmation.confirmation_url


def find_payment(payment_id):
    return Payment.find_one(payment_id=payment_id)
