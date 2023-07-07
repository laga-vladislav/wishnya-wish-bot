from database.dbase import select_call
import datetime
from model.preferences import Premium
from bot.main import notify_premium

dates = select_call("SELECT id, leaving_date FROM premium")
for date in dates:
    if date['leaving_date'] is not None:
        try:
            print(date)
            if datetime.datetime.strptime(date['leaving_date'], "%Y-%m-%d").date() <= datetime.datetime.today().date():
                print(date['leaving_date'])
                Premium(int(date['id'])).lost_premium()
            elif (datetime.datetime.strptime(date['leaving_date'],
                                             "%Y-%m-%d").date() - datetime.datetime.today().date()) == datetime.timedelta(
                    days=3):
                print('3')
                notify_premium(int(date['id']), 3)
            elif (datetime.datetime.strptime(date['leaving_date'],
                                             "%Y-%m-%d").date() - datetime.datetime.today().date()) == datetime.timedelta(
                    days=1):
                print('1')
                notify_premium(int(date['id']), 1)
        except ValueError as e:
            pass
