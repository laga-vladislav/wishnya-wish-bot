import telebot

from settings import config

bot = telebot.TeleBot(token=config.TELEGRAM_NOTIFICATIONS_BOT_TOKEN)

def show_notification(text: str, id: int = config.TELEGRAM_ADMIN_ID):
    bot.send_message(chat_id=id,
                     text=text)
