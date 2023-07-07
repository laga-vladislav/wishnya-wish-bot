import datetime
import threading
import time
import traceback

from listeners.notifications import show_notification
from model.preferences import select_pending_payments, delete_pending_payments, succeeded_payment
from payments.kassa import find_payment


def check_for_new_payments():
    while True:
        try:
            for item in select_pending_payments():
                print(item['date'])
                if datetime.datetime.strptime(item["date"], '%Y/%m/%d %H:%M:%S') + datetime.timedelta(
                        days=1) < datetime.datetime.now():
                    delete_pending_payments(
                        chat_id=item['id'],
                        idempotence_key=item['idempotence_key'],
                        message_id=item['message_id'])
                    continue
                payment = find_payment(item['payment_id'])
                if payment.status == 'succeeded':
                    succeeded_payment(id=int(item['id']),
                                      product_name=item['product_name'],
                                      payment_id=item['payment_id'],
                                      idempotence_key=item['idempotence_key'],
                                      status='succeeded',
                                      date=datetime.datetime.now(),
                                      message_id=item['message_id'])
                    delete_pending_payments(
                        chat_id=item['id'],
                        idempotence_key=item['idempotence_key'],
                        message_id=item['message_id'])
            time.sleep(5)
        except Exception as e:
            show_notification(f'Ошибка в check_for_new_payments:\n\n{traceback.format_exc()}\n\nException:\n\n{e}')
            time.sleep(1)


def polling():
    try:
        names = []
        for item in threading.enumerate():
            names.append(item.name)
        if 'pending_payments' not in names:
            print('pending_payments is running')
            threading.Thread(target=check_for_new_payments, name='pending_payments').start()
        if 'bot_main' not in names:
            print('bot is running')
            from bot.main import bot_polling
            threading.Thread(target=bot_polling, name='bot_main').start()
        print('threads =', *[i.name for i in threading.enumerate()])
    except Exception as e:
        show_notification(f'Проблема с проверкой на pending_payments или bot_main в одном из потоков:\n\n{e}')
        time.sleep(1)
        polling()


if __name__ == '__main__':
    polling()
