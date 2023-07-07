import telebot
from telebot import types

from model.preferences import *

bot = telebot.TeleBot(token=config.TELEGRAM_BOT_TOKEN)


def ID(message):
    id = message.chat.id
    return id


def start_inline_keyboard(names: dict, buttons_in_row: int = 2, pay_text: str = None):
    buttons = []
    for name in names:
        buttons.append(telebot.types.InlineKeyboardButton(f'{name}', callback_data=f'{names[name]}'))
    if pay_text is not None:
        return telebot.types.InlineKeyboardMarkup(row_width=buttons_in_row).add(
            telebot.types.InlineKeyboardButton(pay_text, pay=True)).add(*[button for button in buttons])
    else:
        return telebot.types.InlineKeyboardMarkup(row_width=buttons_in_row).add(*[button for button in buttons])


def start_modified_inline_keyboard(names: tuple, buttons_in_row: int = 2):
    buttons = []
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=buttons_in_row)
    for name in names:
        for button in name:
            buttons.append(telebot.types.InlineKeyboardButton(f'{button}', callback_data=f'{name[button]}'))
        keyboard.row(*[but for but in buttons])
        buttons = []
    return keyboard


def start_keyboard(names: list, one_time_keyboard: bool, first: str = '', last: str = ''):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                 one_time_keyboard=one_time_keyboard,
                                                 row_width=2)
    if first != '':
        keyboard.row(first)
    if last != '':
        keyboard.add(*names)
        keyboard.row(last)
    else:
        keyboard.add(*names)
    return keyboard


def add_back(keyboard, back_button: dict):
    button = []
    for name in back_button:
        button.append(telebot.types.InlineKeyboardButton(f'{name}', callback_data=f'{back_button[name]}'))
    return keyboard.row(*[but for but in button])


# -------СТАРТ-----------------------------------
@bot.message_handler(commands=['start'])
def start(message):
    print(message.text)
    id = ID(message)
    invited = False
    if len(message.text.split(' ')) == 2:
        invited = True
    print(invited)
    if invited:
        friend_id = message.text.split(' ')[1]
        if registered(id):
            answer_request(message, friend_id)
        else:
            bot.send_message(id, 'Прежде чем подписаться на кого-то, нужно пройти регистрацию!\n'
                                 'Приступай: /registration')
        pass
    else:
        if registered(id):
            bot.send_message(id, 'Привет! Мы уже знакомы', reply_markup=types.ReplyKeyboardRemove())
        else:
            bot.send_message(id,
                             'Давайте начнём работу со списком ваших желаний.\n\n'
                             'Какова моя главная задача?\n'
                             'Сделать так, чтобы вы перестали волноваться на счёт подарков!\n'
                             'Вы спросите, как я смогу это сделать? А очень просто!\n'
                             'Вы заполните список своих желаний, ваш друг или родственник добавит вас в свой список отслеживаемых и всегда будет знать, что вам подарить. И наоборот!\n'
                             'Конечно же, если вы будете ответственно и регулярно изменять свой список желаний :)\n'
                             'Желания не обязательно должны быть глобальными, я могу хранить десятки безделушек, которые сами вы себе никогда бы не купили, но с удовольствием бы получили в качестве подарка.\n\n'
                             'Приступайте к регистрации:\n/registration',
                             reply_markup=types.ReplyKeyboardRemove())


# -------РЕГИСТРАЦИЯ-----------------------------------
@bot.message_handler(commands=['registration'])
def registration(message):
    id = ID(message)
    if registered(id):
        bot.send_message(id, 'Регистрация успешно пройдена')
    else:
        user = User(id)
        if user.register(message.from_user.first_name, message.from_user.username):
            bot.send_message(id, 'Успешно')
            keyboard = start_inline_keyboard({'Пропустить': 'menu',
                                              'Добавить': 'createRequest'}, 2)
            bot.send_message(id,
                             'Регистрация прошла успешно\n\nХотите отправить друзьям запрос на добавление в их список Отслеживаемых?',
                             reply_markup=keyboard)
        else:
            bot.send_message(id, 'Что-то пошло не так...')


# -------ДОБАВИТЬ ДРУГА-----------------------------------
def create_request(call):
    user_id = ID(call.message)
    usr = User(user_id)
    link = usr.get_link()
    if link is None:
        link = usr.get_link()
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text='Как это работает?\nВаш друг переходит по ссылке, чтобы подписаться на вас. Ваши подписчики смогут видеть ваш список желаний, тогда как вы их — нет.\n'
                                   'Ваш друг будет видеть вас во вкладке "Подписки", а вы его сможете найти перейдя в меню "Подписчики".\n'
                                   'Чтобы отобразиться подружиться и отображаться друг у друга в друзьях, вам следует перейти по пригласительной ссылке вашего знакомого или нажать "Добавить в друзья" во вкладке "Подписчики".')
        bot.send_message(user_id,
                         f'Вот ваша ссылка ссылка на добавление в друзья 👇\n\n{link}',
                         reply_markup=start_inline_keyboard({'Назад': 'friends_friends'}))
    else:
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=f'Вот ваша ссылка ссылка на добавление в друзья 👇\n\n'
                                   f'{link}\n\n'
                                   f'У вас есть возможность обновить вашу ссылку. Делается это по нажатию кнопки Обновить данные во вкладке Аккаунт.',
                              reply_markup=start_inline_keyboard(
                                  {'Обновить ссылку': 'account_update', 'Назад': 'friends_friends'}, 1))


def answer_request(message, code):
    user_id = ID(message)
    friend_id = decipher_request_link(code)
    if registered(friend_id):
        friend = User(friend_id)
        print(friend)
        name = friend.get_name()
        sent = bot.send_message(chat_id=user_id,
                                text=f'Хотите подписаться на {name}?',
                                reply_markup=start_keyboard(['Да', "Нет"], True))
        bot.register_next_step_handler(sent, poll_answer_request, friend_id, name)
    else:
        bot.send_message(user_id, 'Кажется, этот человек мне не знаком',
                         reply_markup=start_inline_keyboard({'Главное меню': 'menu'}))


def poll_answer_request(message, friend_id, name):
    user_id = ID(message)
    if message.text == 'Да':
        subscribed = User(user_id).subscribe(str(friend_id))
        bot.send_message(chat_id=user_id,
                         text='Добавляю',
                         reply_markup=types.ReplyKeyboardRemove())
        print(subscribed)
        # пока что так будет, потом ошибки переделаю
        if isinstance(subscribed, Errors):
            if subscribed.__str__() == 'subNotRegistered':
                bot.send_message(user_id, 'Кажется, этот человек мне не знаком',
                                 reply_markup=start_inline_keyboard({'Главное меню': 'menu'}))
            elif subscribed.__str__() == 'subscribesHimself':
                bot.send_message(user_id, 'Вы пытаетесь добавить самого себя',
                                 reply_markup=start_inline_keyboard({'Главное меню': 'menu'}))
            elif subscribed.__str__() == 'alreadySubscribed':
                bot.send_message(user_id, f'Вы уже подписаны на {name}',
                                 reply_markup=start_inline_keyboard({'Главное меню': 'menu'}))
        else:
            bot.send_message(user_id, f'Вы успешно подписались на {name}!',
                             reply_markup=start_inline_keyboard({'Подписки': 'friends_subscribes', 'Меню': 'menu'}, 1))
    elif message.text == 'Нет':
        bot.send_message(chat_id=user_id,
                         text='Отмена',
                         reply_markup=types.ReplyKeyboardRemove())
        bot.send_message(chat_id=user_id,
                         text='Отмена прошла успешно',
                         reply_markup=start_inline_keyboard({'Подписки': '', 'Меню': 'menu'}, 1))
    else:
        bot.send_message(user_id, 'Я вас не понимаю. Пожалуйте, используйте вариант ответа из списка внизу 👇',
                         reply_markup=start_keyboard(['Да', "Нет"], one_time_keyboard=True))


def add_friend(call):
    data = call.data.split("_")
    friend_id = data[3]
    user_id = call.message.chat.id
    added = User(user_id).add_friend(friend_id)
    print('added =', added)
    friend_name = User(friend_id).get_name()
    if added == 'userNotRegistered':
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text='Чтобы пользоваться функциями бота нужно зарегистрироваться!\n Жми /registration')
    elif added == 'friendNotRegistered':
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text='Этот пользователь мне более не знаком',
                              reply_markup=start_modified_inline_keyboard(({'Подписчики': 'friends_subscribers'},
                                                                           {"Меню": 'menu'})))
    elif added == 'friendNotInSubscribers':
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text='Что-то пошло не так',
                              reply_markup=start_modified_inline_keyboard(({'Подписчики': 'friends_subscribers'},
                                                                           {"Меню": 'menu'}))
                              )
    elif added == 'userNotInFriendSubscribers':
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text='Что-то пошло не так',
                              reply_markup=start_modified_inline_keyboard(({'Подписчики': 'friends_subscribers'},
                                                                           {"Меню": 'menu'}))
                              )
    elif added == 'addingHimself':
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text='Вы пытаетесь добавить самого себя',
                              reply_markup=start_modified_inline_keyboard(({'Подписчики': 'friends_subscribers'},
                                                                           {"Меню": 'menu'}))
                              )
    elif added == 'alreadyInFriendList':
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text='Пользователь уже находится в вашем списке друзей',
                              reply_markup=start_modified_inline_keyboard(
                                  ({'Список друзей': 'friends_friends', 'Подписчики': 'friends_friends'},
                                   {"Меню": 'menu'}))
                              )
    else:
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=f'{friend_name} был успешно добавлен в друзья!',
                              reply_markup=start_modified_inline_keyboard(
                                  ({'Список друзей': 'friends_friends', 'Назад': 'friends_subscribers'},
                                   {'Меню': 'menu'},)))

# -------УДАЛИТЬ ДРУГА-----------------------------------
def delete_friend(call, deleting: bool = False):
    friend_id = call.data.split('_')[3]
    if deleting:
        user = User(call.message.chat.id)
        deleted = user.delete_friend(friend_id=friend_id)
        if deleted:
            friendlist = telebot.types.InlineKeyboardButton('Назад', callback_data=f'friend_friends_id_{friend_id}')
            menu = telebot.types.InlineKeyboardButton('Меню', callback_data='menu')
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2).add(friendlist, menu)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text='Человек успешно удалён из вашего списка Отслеживаемых',
                                  reply_markup=keyboard)
        else:
            menu = telebot.types.InlineKeyboardButton('Меню', callback_data='menu')
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=1).add(menu)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text='Ошибка при удалении из списка Отслеживаемых',
                                  reply_markup=keyboard)
    else:
        keyboard = start_inline_keyboard({'Да': f"friend_friends_delete_{friend_id}_yes",
                                          "Нет": f"friend_friends_delete_{friend_id}_no"})
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f'Действительно хотите удалить {User(friend_id).get_info()["name"]} из вашего '
                                   f'списка отслеживаемых?',
                              reply_markup=keyboard)


# -------НАСТРОКИ АККАУНТА-----------------------------------
def account_settings(call):
    keyboard = start_modified_inline_keyboard(
        ({'Обновить данные': 'account_update', 'Удалить аккаунт': 'account_delete'},
         {'Ваши подписки': 'friends_subscribes'},
         {'Подписчики': 'friends_subscribers'},
         {'Премиум функции': 'premium'},
         {'Назад': 'menu'}),
        buttons_in_row=2)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f'Выберите интересующий вас пункт.',
                          reply_markup=keyboard)


# -------ОБНОВИТЬ ДАННЫЕ АККАУНТА-----------------------------------
def account_update(call):
    keyboard = start_inline_keyboard({'Продолжить': 'account_update_yes',
                                      'Отменить': 'account_update_no'})
    if call.data == 'account_update':
        bot.edit_message_text(chat_id=ID(call.message),
                              message_id=call.message.message_id,
                              text='Для чего нужно обновлять данные аккаунта?\n\n'
                                   'Вы наверняка замечали, что в списке Отслеживаемых используются данные,'
                                   'введённые пользователем в самом приложении Телеграм.\n'
                                   'Такие как "Имя" и "Имя пользователя".\n'
                                   'Если вы сменили что-то из перечисленного мною выше списка и хотите, чтобы я '
                                   'запомнил их заново, то нажмите продолжить 👇',
                              reply_markup=keyboard)
    elif call.data == 'account_update_yes':
        sent = bot.edit_message_text(text='Чтобы продолжить, решите простую задачу:\nСколько будет 5 + 4?',
                                     chat_id=ID(call.message),
                                     message_id=call.message.message_id,
                                     reply_markup=None)
        bot.register_next_step_handler(sent, done_account_update)
    else:
        menu(call.message, True)


def done_account_update(message):
    if User(ID(message)).update_info(name=message.from_user.first_name,
                                     username=f'@{message.from_user.username}'):
        bot.send_message(ID(message), 'Я не знаю! Наверное, правильно :)\nВ общем, данные я обновил!')
    else:
        keyboard = start_inline_keyboard({'Меню': 'menu'})
        bot.send_message(ID(message),
                         'Что-то пошло не так. Приходите позже! Скоро всё наладится',
                         reply_markup=keyboard)


# -------УДАЛИТЬ АККАУНТ-----------------------------------
def delete_account(call, deleting_mode: bool = False):
    print(deleting_mode)
    if not deleting_mode:
        keyboard = start_inline_keyboard({'Да': 'account_delete_yes',
                                          'Нет': 'account_delete_no'})
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Вы уверены, что хотите удалить свой аккаунт?\nДанные не сохранятся',
                              reply_markup=keyboard)
    else:
        user = User(call.message.chat.id)
        if user.unregister():
            bot.send_message(call.message.chat.id, 'Аккаунт успешно удалён')
            try:
                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id)
            except Exception as e:
                print('ошибка при удалении сообщения. Вероятно, оно старше 48 часов\n\n', e)
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text='Удалено')
        else:
            bot.send_message(call.message.chat.id, 'Ошибка при удалении аккаунта')
        bot.answer_callback_query(callback_query_id=call.id)


# -------МЕНЮ ПОДПИСКИ --------------------------------
def unsubscribe(call, deleting_mode: bool = False):
    user_id = ID(call.message)
    friend_id = call.data.split('_')[3]
    user = User(user_id)
    friend_name = User(friend_id).get_name()
    if deleting_mode:
        deleted = user.unsubscribe(sub_id=friend_id)
        print(deleted.__str__(), Errors('alreadyNotInSubscribes'))
        print(type(str(deleted.__str__())), type(Errors('alreadyNotInSubscribes')))
        if deleted is True:
            msg_text = f'Вы успешно отписались от {friend_name}.'
        elif deleted.__str__() == 'userNotRegistered':
            msg_text = 'Пользователь мне более не знаком.'
        elif deleted.__str__() == 'alreadyNotInSubscribes':
            msg_text = 'Пользователь итак не находится в вашем списке подписок.'
        else:
            msg_text = f'Что-то пошло не так'
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=msg_text,
                              reply_markup=start_inline_keyboard({'Подписки': 'friends_subscribes',
                                                                  'Меню': 'menu'}))
    else:
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=f'Вы действительно хотите отписаться от {friend_name}?',
                              reply_markup=start_inline_keyboard({'Да': f'friend_subscribes_delete_{friend_id}_yes',
                                                                  'Нет': f'friend_subscribes_delete_{friend_id}_no'}))


def unsubscribe_all(call, deleting_mode: bool = False):
    user_id = ID(call.message)
    if deleting_mode:
        not_registered = False
        deleted = User(user_id).unsubscribe_all()
        if deleted is True:
            msg_text = f'Вы успешно очистили ваши подписки.'
        elif deleted.__str__() == 'userNotRegistered':
            not_registered = True
            msg_text = 'Чтобы пользоваться функциями бота нужно зарегистрироваться\n/registration'
        elif deleted.__str__() == 'subscribesAlreadyClean':
            msg_text = 'Список итак пуст.'
        else:
            msg_text = 'Что-то пошло не так'
        if not_registered:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.message_id,
                                  text=msg_text)
        else:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.message_id,
                                  text=msg_text,
                                  reply_markup=start_inline_keyboard({'Подписки': 'friends_subscribes',
                                                                      'Меню': 'menu'}))
    else:
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=f'Вы действительно хотите отписаться от всех?',
                              reply_markup=start_inline_keyboard({'Да': f'friends_subscribes_deleteAll_yes',
                                                                  'Нет': f'friends_subscribes_deleteAll_no'}))


# -------МЕНЮ ПОДПИСЧИКА--------------------------------
def subscriber(call, subscriber_id):
    user_id = ID(call.message)
    subscriber = User(subscriber_id)
    subscriber_name = subscriber.get_name()
    keyboard = start_modified_inline_keyboard(({'Добавить в друзья': f'friend_subscribers_add_{subscriber_id}',
                                                'Удалить': f'friend_subscribers_delete_{subscriber_id}'},
                                               {'Назад': 'friends_subscribers'}), 2)
    bot.edit_message_text(chat_id=user_id,
                          message_id=call.message.message_id,
                          text=f'{subscriber_name} подписан на вас.\n\nВот, что вы можете сделать:',
                          reply_markup=keyboard)


def subscriber_delete(call, deleting_mode: bool = False):
    user_id = ID(call.message)
    friend_id = call.data.split('_')[3]
    friend = User(friend_id)
    friend_name = friend.get_name()
    if deleting_mode:
        deleted = friend.unsubscribe(sub_id=user_id)
        if deleted is True:
            msg_text = f'{friend_name} больше не является вашим подписчиком.'
        elif deleted.__str__() == 'userNotRegistered':
            msg_text = 'Пользователь мне более не знаком.'
        elif deleted.__str__() == 'alreadyNotInSubscribes':
            msg_text = 'Пользователь итак не являлся вашим подписчиком'
        else:
            msg_text = 'Что-то пошло не так'
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=msg_text,
                              reply_markup=start_inline_keyboard({'Подписчики': 'friends_subscribers',
                                                                  'Меню': 'menu'}))
    else:
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=f'Вы действительно хотите удалить {friend_name}?',
                              reply_markup=start_inline_keyboard({'Да': f'friend_subscribers_delete_{friend_id}_yes',
                                                                  'Нет': f'friend_subscribers_delete_{friend_id}_no'}))


def subscriber_deleteAll(call, deleting_mode: bool = False):
    user_id = ID(call.message)
    if deleting_mode:
        not_registered = False
        deleted = User(user_id).unsubscribe_all()
        if deleted is True:
            msg_text = f'Вы успешно очистили ваш список подписчиков.'
        elif deleted.__str__() == 'userNotRegistered':
            not_registered = True
            msg_text = 'Чтобы пользоваться функциями бота нужно зарегистрироваться\n/registration'
        elif deleted.__str__() == 'subscribersAlreadyClean':
            msg_text = 'Список итак пуст.'
        else:
            msg_text = 'Что-то пошло не так'
        if not_registered:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.message_id,
                                  text=msg_text)
        else:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=call.message.message_id,
                                  text=msg_text,
                                  reply_markup=start_inline_keyboard({'Подписчики': 'friends_subscribers',
                                                                      'Меню': 'menu'}))
    else:
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=f'Вы действительно хотите удалить всех?',
                              reply_markup=start_inline_keyboard({'Да': f'friends_subscribers_deleteAll_yes',
                                                                  'Нет': f'friends_subscribers_deleteAll_no'}))


# -------СПИСОК ДРУЗЕЙ---И ПОДПИСЧИКОВ--И ПОДПИСОК------------------------------
def friend_list(call, page_number: int):
    page_index = page_number - 1
    user_id = ID(call.message)
    user = User(user_id)
    subscribers = False
    subscribes = False
    if call.data.split('_')[1] == 'friends':
        list_friends = user.get_friend_list()
    elif call.data.split('_')[1] == 'subscribers':
        subscribers = True
        list_friends = user.get_subscribers()
        if list_friends is None:
            list_friends = []
    else:
        subscribes = True
        list_friends = user.get_subscribes()
        if list_friends is None:
            list_friends = []
    if len(list_friends) == 0:
        bot.answer_callback_query(callback_query_id=call.id)  # то сообщаем об этом
        # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
        if subscribers:
            keyboard = start_inline_keyboard({'Назад': 'account'}, 1)
        # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
        elif subscribes:
            keyboard = start_modified_inline_keyboard(({'Назад': 'account'},), 1)
        # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
        else:
            keyboard = start_inline_keyboard({'Пригласительная ссылка': 'createRequest',
                                              'Назад': 'menu'}, 1)
        # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
        if subscribers:
            message_text = f'Подписчики.\n\nЗдесь никого нет!'
        # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
        elif subscribes:
            message_text = f'Подписки.\n\nЗдесь никого нет!'
        # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
        else:
            message_text = f'Список друзей.\n\n' \
                           f'Здесь никого нет!\n' \
                           f'Чтобы добавить пользователя в друзьям нужно, чтобы он перешёл по вашей пригласительной ссылке и принял заявку\n' \
                           f'Ваша ссылка находится здесь 👇'
        bot.edit_message_text(chat_id=user_id,  # меняем и текст
                              message_id=call.message.message_id,
                              reply_markup=keyboard,
                              text=message_text)
    elif list_friends is None:
        bot.answer_callback_query(callback_query_id=call.id, text='Ошибка')  # то сообщаем об этом
    else:
        couples = get_friends_couples(list_of_friends=list_friends,
                                      friends_on_page=5)  # разбиваем друзей по кучкам (в нашем случае, по 5 человек на страницу)
        couple = couples[page_index]
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)  # создаём клавиатуру с 2 людьми в строке
        buttons = []  # пустой массив кнопок с друзьями
        print("friend_couples -> ", couples)
        print('couple -> ', couple)
        for i in range(len(couple)):  # идём по каждому другу в кучке
            deleted_friends = 0
            friend = User(couple[i]).get_info()  # собираем информацию о друге
            name = User(couple[i]).get_name()
            if friend is None:
                deleted_friends += 1
                continue
            print(f'friend {i} -> ', friend)
            # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
            if subscribers:
                data = f'friend_subscribers_id_{friend["id"]}'
            # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
            elif subscribes:
                data = f'friend_subscribes_id_{friend["id"]}'
            # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
            else:
                data = f'friend_friends_id_{friend["id"]}'
            buttons.append(
                telebot.types.InlineKeyboardButton(  # заполняем массив кнопок с друзьями
                    name,
                    callback_data=data
                )
            )
        for button in buttons:
            keyboard.row(button)  # добавляем друзей в клавиатуру
        if len(couples) != 1:
            # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
            if subscribers:
                prev = telebot.types.InlineKeyboardButton('« Назад',
                                                          callback_data=f'friends_subscribers_prev_{page_number - 1}_{len(couples)}')  # кнопка назад
                next = telebot.types.InlineKeyboardButton('Дальше »',
                                                          callback_data=f'friends_subscribers_next_{page_number + 1}_{len(couples)}')
            # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
            elif subscribes:
                prev = telebot.types.InlineKeyboardButton('« Назад',
                                                          callback_data=f'friends_subscribes_prev_{page_number - 1}_{len(couples)}')  # кнопка назад
                next = telebot.types.InlineKeyboardButton('Дальше »',
                                                          callback_data=f'friends_subscribes_next_{page_number + 1}_{len(couples)}')
            # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
            else:
                prev = telebot.types.InlineKeyboardButton('« Назад',
                                                          callback_data=f'friends_friends_prev_{page_number - 1}_{len(couples)}')  # кнопка назад
                next = telebot.types.InlineKeyboardButton('Дальше »',
                                                          callback_data=f'friends_friends_next_{page_number + 1}_{len(couples)}')
            keyboard.add(prev, next)
        # -----СПИСОК ОТСЛЕЖИВАЮЩИХ------------СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------
        if subscribers or subscribes:
            if subscribers:
                title = 'Подписчики.'
                keyboard.row(telebot.types.InlineKeyboardButton('Добавить всех в друзья',
                                                                callback_data='friends_subscribers_acceptAll'))
                keyboard.row(
                    telebot.types.InlineKeyboardButton('Удалить всех', callback_data='friends_subscribers_deleteAll'))
            else:
                title = 'Ваши подписки.'
                keyboard.row(
                    telebot.types.InlineKeyboardButton('Удалить всех', callback_data='friends_subscribes_deleteAll'))
            message_text = f'{title}\nСтраница {page_number} из {len(couples)}\nКого хотите ' \
                           f'посмотреть?'
            keyboard.row(telebot.types.InlineKeyboardButton('Назад', callback_data='account'))
        # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
        else:
            message_text = f'Список друзей.\nСтраница {page_number} из {len(couples)}\nКого хотите ' \
                           f'посмотреть?'
            add = telebot.types.InlineKeyboardButton('Пригласительная ссылка', callback_data='createRequest')
            menu = telebot.types.InlineKeyboardButton('Вернуться в меню', callback_data='menu')
            keyboard.row(add).row(menu)
        bot.edit_message_text(chat_id=user_id,  # меняем и текст
                              message_id=call.message.message_id,
                              reply_markup=keyboard,
                              text=message_text)


# -------МЕНЮ-----------------------------------
@bot.message_handler(commands=['menu'])
def menu(message, from_callback: bool = False):
    id = ID(message)
    if registered(id):
        buttons = {'Друзья': 'friends_friends',
                   'Список желаний': 'wishlist',
                   'Аккаунт': 'account'}
        keyboard = start_inline_keyboard(buttons)
        if from_callback:
            bot.edit_message_text(chat_id=id,
                                  message_id=message.message_id,
                                  text='Главное меню.\nВыберите интересующий вас раздел',
                                  reply_markup=keyboard,
                                  disable_web_page_preview=True)
        else:
            bot.send_message(id,
                             'Главное меню.\nВыберите интересующий вас раздел',
                             reply_markup=keyboard,
                             disable_web_page_preview=True)


# -------ЖЕЛАНИЯ ГЛАВНАЯ-----------------------------------
@bot.message_handler(commands=['wishlist'])  # меню желаний
def wishlist(call, friend_id: int = 0, new_window: bool = False):
    try:
        """""""""""""""""""""PREMIUM"""""""""""""""""""""""""""""
        premium_text = ''
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""
        user_id = call.message.chat.id
        print('call: ', call.data.split('_'), 'user_id: ', user_id, 'friend_id: ', 'new_window: ', new_window)
        # получаем список желаний
        # ----НАШ СПИСОК-----------------------------------------------------------------------------------------------
        if friend_id == 0:  # если нужен наш список
            wishlist = User(user_id).get_wishlist()
            name = ''
        # ----СПИСОК ДРУГА---------------------------------------------------------------------------------------------
        else:  # если нужен список друга
            friend = User(friend_id)
            friend_info = friend.get_info()
            subscribes = False
            if 'subscribes' in call.data.split('_'):
                subscribes = True
            """""""""""""""""""""PREMIUM"""""""""""""""""""""""""""""
            friend_premium = Premium(friend_id)
            user_premium = Premium(user_id)
            if user_premium.belong():
                if friend_premium.belong():
                    premium_text = '\n\nТариф пользователя: Премиум'
                else:
                    premium_text = '\n\nТариф пользователя: Стандартный'
            if friend_premium.belong():
                print('friend has premium')
                friend_premium.make_view(user_id)
                if subscribes:
                    # ----------------------------------- wishlist = friend.get_wishlist()
                    wishlist = friend.get_wishlist(with_reserved=True)
                else:
                    # --------------------------------------- wishlist = friend_premium.get_total_wishlist(friend_id=user_id)
                    wishlist = friend_premium.get_total_wishlist(friend_id=user_id, with_reserved=True)
                print(wishlist)
            else:
                # --------------------------- wishlist = friend.get_wishlist()
                wishlist = friend.get_wishlist(with_reserved=True)
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""
            name = ' ' + friend.get_name(friend_info)
        print(wishlist)
        # обрабатываем список желаний
        # ----СПИСОК ПУСТ----------------------------------------------------------------------------------------------
        if wishlist == -1:  # список пуст
            print("empty")
            # ----НАШ СПИСОК-------------------------------------------------------------------------------------------
            if friend_id == 0:  # список пользователя
                keyboard = start_inline_keyboard({'Добавить': 'wishlist_add',
                                                  'Корзина': 'wishlist_crossed'})
                add_back(keyboard, {'Назад': 'menu'})
                # ----ИЗМЕНИТЬ СООБЩЕНИЕ-------------------------------------------------------------------------------
                if not new_window:
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=call.message.message_id,
                                          text=f'Список желаний пуст! Хотите заполнить?',
                                          reply_markup=keyboard,
                                          disable_web_page_preview=True)
                # ----НОВОЕ СООБЩЕНИЕ----------------------------------------------------------------------------------
                else:
                    bot.send_message(chat_id=user_id,
                                     text=f'Список желаний пуст! Хотите заполнить?',
                                     reply_markup=keyboard,
                                     disable_web_page_preview=True)
            # ----СПИСОК ДРУГА (или подписки)-----------------------------------------------------------------------------------------
            else:  # список друга
                # bot.answer_callback_query(callback_query_id=call.id, text='Список пуст')  # отвечаем на вызов
                # ans(call)
                if 'friends' in call.data.split('_'):
                    keyboard = start_inline_keyboard({'Удалить из друзей': f'friend_friends_delete_{friend_id}',
                                                      'Назад': 'friends_friends'}, 1)
                else:
                    keyboard = start_inline_keyboard({'Удалить пользователя': f'friend_subscribers_delete_{friend_id}',
                                                      'Назад': 'friends_subscribers'}, 1)
                if new_window:
                    bot.send_message(chat_id=user_id,
                                     text=f'Список желаний {name} пуст!{premium_text}',
                                     reply_markup=keyboard,
                                     disable_web_page_preview=True)
                else:
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=call.message.message_id,
                                          text=f'Список желаний {name} пуст!{premium_text}',
                                          reply_markup=keyboard,
                                          disable_web_page_preview=True)
        # ----СПИСОК НЕ ПУСТ-------------------------------------------------------------------------------------------
        else:  # список не пуст
            print("not empty")
            sorted_wishes = sorted_wishlist(wishlist, reserver_id=user_id)
            print(sorted_wishes)
            # ----НАШ СПИСОК-------------------------------------------------------------------------------------------
            if friend_id == 0:  # список пользователя
                reserve_text = ''
                keyboard = start_inline_keyboard({'Изменить': 'wishlist_edit',
                                                  'Добавить желания': 'wishlist_add',
                                                  'Корзина': 'wishlist_crossed'})
                add_back(keyboard, {'Назад': 'menu'})  # добавить кнопку назад
                name = ''
            # ----СПИСОК ДРУГА----И СПИСОК ПОДПИСЧИКА-------------------------------------------------------------------------------------
            else:  # список друга
                reserve_text = '\n\n🤙 — зарезервированные вами желания\n🤌 — зарезервированные кем-то другим'
                if subscribes:
                    keyboard = start_modified_inline_keyboard(
                        ({"Отписаться": f'friend_subscribes_delete_{friend_id}'},
                         {"Назад": 'friends_subscribes'}), 1)
                else:
                    keyboard = start_inline_keyboard({'Удалить пользователя': f'friend_friends_delete_{friend_id}',
                                                      'Забронировать': f'friend_friends_reserve_id_{friend_id}',
                                                      'Назад': 'friends_friends'}, 1)
            # ----ИЗМЕНИТЬ СООБЩЕНИЕ-----------------------------------------------------------------------------------
            if not new_window:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      text=f'Список желаний{name}.{premium_text}\n\n{sorted_wishes}{reserve_text}',
                                      reply_markup=keyboard,
                                      disable_web_page_preview=True)  # сообщение с желаниями
            # ----НОВОЕ СООБЩЕНИЕ--------------------------------------------------------------------------------------
            else:
                bot.send_message(chat_id=user_id,
                                 text=f'Список желаний{name}.{premium_text}\n\n{sorted_wishes}{reserve_text}',
                                 reply_markup=keyboard,
                                 disable_web_page_preview=True)
            # ans(call)
    except Exception as e:
        print(e)


# -------ЗАРЕЗЕРВИРОВАТЬ ЖЕЛАНИЯ-------------------------------
def reserve_wishlist(call):
    user_id = call.message.chat.id
    owner_id = int(call.data.split('_')[4])
    if registered(owner_id):
        friend = User(owner_id)
        bot.edit_message_reply_markup(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      reply_markup=None)
        if Premium(owner_id).belong():
            count = len(Premium(owner_id).get_total_wishlist(friend_id=user_id))
        else:
            count = friend.count_of_wishes()
        keyboard = start_keyboard(names=[str(i + 1) for i in range(count)],
                                  one_time_keyboard=True).row('Отмена')
        sent = bot.send_message(user_id,
                                'Выберите пункт с желанием, которое хотите забронировать, либо у которого хотите снять бронь:',
                                reply_markup=keyboard)
        bot.register_next_step_handler(sent, poll_wishlist, call)
    else:
        bot.edit_message_text(chat_id=user_id,
                              text='Что-то пошло не так! Пожалуйста, попробуйте ещё раз.',
                              reply_markup=start_inline_keyboard({'Меню': 'menu'}))


def done_reserve_wishlist(call, index):
    user_id = call.message.chat.id
    owner_id = int(call.data.split('_')[4])
    owner = User(owner_id)
    reserved_wishes = owner.get_reserved_wishes(reserver_id=user_id)
    print(f'owner id = {owner_id}\nreserved_wishes = {reserved_wishes}')
    if reserved_wishes is not None:
        print(
            f'index = {index}, owner_id = {owner_id}, reserved_wishes = {reserved_wishes}, ({(user_id in reserved_wishes.keys())}, {(int(index) in reserved_wishes[user_id]["indexes"])})')
        if user_id in reserved_wishes.keys():
            print(f"index of wish = {index}\nreserved wishes = {reserved_wishes}")
            if int(index) not in reserved_wishes[user_id]['indexes']:
                reserve = owner.reserve_wish(int(index), user_id)
                if isinstance(reserve, Errors):
                    print(reserve)
                    if reserve.__str__() == 'individual wish with this index doesnt exist':
                        bot.send_message(chat_id=user_id,
                                         text='Кажется, автор удалил данное желание!',
                                         reply_markup=types.ReplyKeyboardRemove())
                    elif any(reserve.__str__() == i for i in ['wrong index of individual wish', 'wrong index']):
                        bot.send_message(chat_id=user_id,
                                         text='Пожалуйста, убедитесь, что вы ввели верное значение',
                                         reply_markup=types.ReplyKeyboardRemove())
                    elif any(reserve.__str__() == i for i in
                             ['already reserved', 'individual wish with this index is already reserved']):
                        bot.send_message(chat_id=user_id,
                                         text='Кто-то уже забронировал данное желание!',
                                         reply_markup=types.ReplyKeyboardRemove())
                    elif reserve.__str__() == 'wishlist is empty':
                        bot.send_message(chat_id=user_id,
                                         text='Кажется, автор очистил свой список желаний!',
                                         reply_markup=types.ReplyKeyboardRemove())
                    else:
                        bot.send_message(chat_id=user_id,
                                         text='Что-то пошло не так!',
                                         reply_markup=types.ReplyKeyboardRemove())
                    bot.send_message(chat_id=user_id,
                                     text='Воспользуйтесь кнопками ниже, чтобы вернуться назад',
                                     reply_markup=start_inline_keyboard({'Список друзей': 'friends_friends',
                                                                         'Меню': 'menu'}, 1))
                else:
                    bot.send_message(chat_id=user_id,
                                     text=f'Отлично, вы забронировали пункт под номером {index + 1}!',
                                     reply_markup=types.ReplyKeyboardRemove())
                    wishlist(call=call, friend_id=owner_id, new_window=True)
            else:
                unreserve = owner.unreserve_wish(int(index), user_id)
                if isinstance(unreserve, Errors):
                    print(unreserve)
                    bot.send_message(chat_id=user_id,
                                     text='Что-то пошло не так!',
                                     reply_markup=types.ReplyKeyboardRemove())
                else:
                    bot.send_message(chat_id=user_id,
                                     text=f'Отлично, снял бронь с пункта номер {index + 1}.',
                                     reply_markup=types.ReplyKeyboardRemove())
                    wishlist(call=call, friend_id=owner_id, new_window=True)
        else:
            bot.send_message(chat_id=user_id,
                             text='Данный пункт кто-то уже забронировал!',
                             reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(chat_id=user_id,
                             text='Хотите изменить номер?',
                             reply_markup=start_inline_keyboard(
                                 {'Да': 'friend_friends_reserve_id_533840147', 'Нет': 'friend_friends_id_533840147'}))
    else:
        reserve = owner.reserve_wish(int(index), user_id)
        if isinstance(reserve, Errors):
            print(reserve)
            if reserve.__str__() == 'individual wish with this index doesnt exist':
                bot.send_message(chat_id=user_id,
                                 text='Кажется, автор удалил данное желание!',
                                 reply_markup=types.ReplyKeyboardRemove())
            elif any(reserve.__str__() == i for i in ['wrong index of individual wish', 'wrong index']):
                bot.send_message(chat_id=user_id,
                                 text='Пожалуйста, убедитесь, что вы ввели верное значение',
                                 reply_markup=types.ReplyKeyboardRemove())
            elif any(reserve.__str__() == i for i in
                     ['already reserved', 'individual wish with this index is already reserved']):
                bot.send_message(chat_id=user_id,
                                 text='Кто-то уже забронировал данное желание!',
                                 reply_markup=types.ReplyKeyboardRemove())
            elif reserve.__str__() == 'wishlist is empty':
                bot.send_message(chat_id=user_id,
                                 text='Кажется, автор очистил свой список желаний!',
                                 reply_markup=types.ReplyKeyboardRemove())
            else:
                bot.send_message(chat_id=user_id,
                                 text='Что-то пошло не так!',
                                 reply_markup=types.ReplyKeyboardRemove())
            bot.send_message(chat_id=user_id,
                             text='Воспользуйтесь кнопками ниже, чтобы вернуться назад',
                             reply_markup=start_inline_keyboard({'Список друзей': 'friends_friends',
                                                                 'Меню': 'menu'}, 1))
        else:
            bot.send_message(chat_id=user_id,
                             text=f'Отлично, вы забронировали пункт под номером {index + 1}!',
                             reply_markup=types.ReplyKeyboardRemove())
            wishlist(call=call, friend_id=owner_id, new_window=True)


# -------ЖЕЛАНИЯ ВЫЧЕРКНУТЫЕ-----------------------------------
def crossed_wishlist(call):
    user_id = ID(call.message)
    user = User(user_id)
    # ---ПОЛУЧАЕМ СПИСОК ВЫЧЕРКНУТЫХ ЖЕЛАНИЙ------------------------------------------------
    wishlist = user.get_wishlist(True)
    print(call.data.split('_'), user_id, wishlist)
    # ---ЕСЛИ СПИСОК ПУСТ------------------------------------------------
    if wishlist == -1:
        print("empty")
        bot.answer_callback_query(callback_query_id=call.id, text='Список пуст')
    else:
        print('not empty')
        keyboard = start_inline_keyboard({'Восстановить': 'wishlist_crossed_return',
                                          'Удалить': 'wishlist_crossed_delete'})
        add_back(keyboard=keyboard, back_button={'Назад': 'wishlist'})
        sorted_wishes = sorted_wishlist(wishlist=wishlist)  # сортируем желания, нумеруем
        bot.edit_message_text(chat_id=user_id,
                              message_id=call.message.message_id,
                              text=f'Корзина.\n{sorted_wishes}',
                              reply_markup=keyboard)


# -------ВЕРНУТЬ ЖЕЛАНИЯ ВЫЧЕРКНУТЫЕ-----------------------------------
def crossed_wishlist_return(call):
    id = ID(call.message)
    user = User(id)
    crossed_wishlist = user.get_wishlist(True)
    if crossed_wishlist == -1:
        print('невозможная ошибка в crossed_wishlist_return. список пуст')
    else:
        bot.edit_message_reply_markup(chat_id=id,
                                      message_id=call.message.message_id,
                                      reply_markup=None)
        keyboard = start_keyboard(names=[str(i + 1) for i in range(user.count_of_wishes(True))],
                                  first='Готово',
                                  last='Все',
                                  one_time_keyboard=False).row('Отмена')
        sent = bot.send_message(id, 'Какие пункты следует вернуть?', reply_markup=keyboard)
        bot.register_next_step_handler(sent, poll_wishlist, call)


def done_crossed_wishlist_return(call, message, wish_indexes):
    user = User(message.chat.id)
    print(user.get_wishlist(True))
    print('--------------------------------------\n'
          'starting adding wishes to wishlist')
    try:
        print('wish_indexes -> ', wish_indexes)
        added = user.add_wishes(
            wishes=user.get_wishlist_by_indexes(
                indexes=[int(i) for i in wish_indexes],
                crossed=True
            ),
            crossed=False
        )
        if added:
            print('successfully added')
        else:
            print('adding failed')
    except Exception as e:
        print(e, '\n\ntry error in done_crossed_wishlist_return. adding failed')
        bot.send_message(ID(message), 'Что-то пошло не так. В скором времени всё исправится!',
                         reply_markup=None)
        return
    print('adding wishes to wishlist ended\n'
          '--------------------------------------')
    print('--------------------------------------\n'
          'starting deleting wishes to wishlist')
    try:
        deleted = User(message.chat.id).delete_wishlist(
            wishes_to_delete=user.get_wishlist_by_indexes(
                indexes=[i for i in wish_indexes],
                crossed=True),
            crossed=True
        )
        if deleted:
            print('successfully deleted')
        else:
            print('deleting failed')
    except Exception as e:
        print(e, '\n\ntry error in done_crossed_wishlist_return. deleting failed')
        bot.send_message(ID(message), 'Что-то пошло не так. В скором времени всё исправится!',
                         reply_markup=types.ReplyKeyboardRemove())
        return
    print('deleting wishes to wishlist ended\n'
          '--------------------------------------')
    print(user.get_wishlist(True))
    bot.send_message(message.chat.id, 'Успешно!', reply_markup=types.ReplyKeyboardRemove())
    wishlist(call, 0, True)


# -------ДОБАВЛЕНИЕ-----------------------------------
def add_wishes(call):
    ans(call)
    user_id = call.message.chat.id
    cancel_keyboard = start_inline_keyboard({'Назад': 'cancel'}, 1)
    sent = bot.edit_message_text(chat_id=user_id,
                                 message_id=call.message.message_id,
                                 text='Можете перечислить новые пожелания!\n'
                                      'Пункты отделяйте переносом строки, нумерация проставляется автоматически',
                                 reply_markup=cancel_keyboard)
    bot.register_next_step_handler(sent, add_wishlist, call)


def add_wishlist(message, call):
    user_id = message.chat.id
    if User(user_id).add_wishes(message.text.split('\n')):  # если успешно добавилось
        print('add_wishlist. wishes to add -> ', message.text.split('\n'))
        keyboard = start_inline_keyboard({'Просмотреть': 'wishlist',
                                          'Меню': 'menu'}, 1)
        bot.edit_message_text(chat_id=message.chat.id,
                              message_id=call.message.message_id,
                              text='Добавляю')
        bot.send_message(user_id, 'Успешно добавил', reply_markup=types.ReplyKeyboardRemove())
        wishlist(call, 0, True)
    else:
        print('Что-то пошло не так в add_wishlist')


# -------МЕНЮ ИЗМЕНЕНИЙ-----------------------------------
def wishlist_editor(call):  # call = wishlist_edit
    if User(call.message.chat.id).get_wishlist() == -1:  # если список пуст
        bot.answer_callback_query(callback_query_id=call.id, text='Список пуст')
    else:  # если не пуст
        id = call.message.chat.id
        keyboard = start_inline_keyboard({'Отредактировать': 'wishlist_reedit',
                                          'Удалить': 'wishlist_delete',
                                          'В корзину': 'wishlist_cross'})
        add_back(keyboard, {'Назад': 'wishlist'})  # добавляет кнопку назад
        bot.edit_message_reply_markup(chat_id=id,  # изменить кнопки сообщения со списком желаний
                                      message_id=call.message.message_id,
                                      reply_markup=keyboard)


# -------РЕДАКТИРОВАНИЕ-----------------------------------
def reedit_wishlist(call):  # call = wishlist_reedit
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=None)
    keyboard = start_keyboard(names=[str(i + 1) for i in range(User(call.message.chat.id).count_of_wishes())],
                              # добавить в клавиатуру пункты желаний
                              one_time_keyboard=False, first='Готово', last='Все').row('Отмена')
    sent = bot.send_message(call.message.chat.id,
                            'Выберите пункты, которые следует отредактировать:',
                            reply_markup=keyboard)
    bot.register_next_step_handler(sent, poll_wishlist, call,
                                   None)  # переходим в poll_wishlist(sent, call, numb)


def done_reedit_wishlist(message, wish_indexes):
    user = User(message.chat.id)
    # -------ПОЛУЧИТЬ ТЕКСТ ЖЕЛАНИЯ ИЗ ТЕКСТА СООБЩЕНИЯ, НА КОТОРОЕ ОТВЕТИЛ ПОЛЬЗОВАТЕЛЬ-------------------------------
    keyboard = start_inline_keyboard({'Закончить': 'cancel'})
    try:
        wish = get_wish_from_msg(message_text=message.reply_to_message.text, wishlist=user.get_wishlist())
        print('wish -> ', wish)
        # -------ЕСЛИ ПОЛУЧИЛИ-----------------------------------------------------------------------------------------
        if wish is not None:
            # -------ПОЛУЧАЕМ ТЕКСТ НОВОГО ЖЕЛАНИЯ ИЗ СООБЩЕНИЯ, КОТОРОЕ ПРИСЛАЛ ПОЛЬЗОВАТЕЛЬ--------------------------
            # new_wish =
            new_wish = get_word_from_msg(message.text)
            if new_wish is None:
                new_wish = message.text
            print('new_Wish -> ', new_wish)
            # -------ДЛЯ РАБОТЫ С ПОЛЬЗОВАТЕЛЕМ------------------------------------------------------------------------
            usr = User(ID(message))
            wish_index = get_index_from_msg(message.reply_to_message.text)
            if wish_index is None:
                print('error after get_index_from_msg in done_reedit_wishlist')
                keyboard = start_inline_keyboard({'Список желаний': 'wishlist',
                                                  "Меню": "menu"})
                bot.send_message(ID(message), 'Что-то пошло не так! Пожалуйста, не используйте перенос строки.\n'
                                              'Придётся начать сначала :)',
                                 reply_markup=keyboard)
                return
            print('index - > ', wish_index)
            if usr.change_wish(index=wish_index, edited_wish=new_wish):
                sent = bot.send_message(ID(message), f'Заменил "{wish}"\nна\n"{new_wish}"', reply_markup=keyboard)
            else:
                sent = bot.send_message(ID(message), f'Что-то пошло не так', reply_markup=keyboard)
        else:
            sent = bot.send_message(ID(message), 'Что-то пошло не так. Убедитесь, что ответили на верное сообщение',
                                    reply_markup=keyboard)
    except AttributeError as e:
        print(e, 'user did not answer to message')
        sent = bot.send_message(ID(message), 'Пожалуйста, ответьте на сообщение с текстом желания, которое хотите '
                                             'заменить', reply_markup=keyboard)
    bot.register_next_step_handler(sent, done_reedit_wishlist, wish_indexes)


# -------ВЫЧЕРКНУТЬ-----------------------------------
def cross_wishlist(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=None)
    id = ID(call.message)
    keyboard = start_keyboard(names=[str(i + 1) for i in range(User(id).count_of_wishes())],
                              one_time_keyboard=False, first='Готово', last='Все').row('Отмена')
    sent = bot.send_message(call.message.chat.id,
                            'Выберите пункты, которые следует вычеркнуть:',
                            reply_markup=keyboard)
    bot.register_next_step_handler(sent, poll_wishlist, call,
                                   None)  # переходим в poll_wishlist(sent, call, sent.message_id)


def done_cross_wishlist(message, call, wish_indexes):
    wishes_to_cross = User(message.chat.id).get_wishlist_by_indexes(indexes=[i for i in wish_indexes])
    print('wishes to cross', wishes_to_cross)
    add = User(message.chat.id).add_wishes(wishes=wishes_to_cross, crossed=True)
    delete = User(message.chat.id).delete_wishlist(wishes_to_delete=wishes_to_cross)
    print('ADD and DELETE = ', add, delete)
    if delete and add:
        bot.edit_message_text(text='Вычеркиваю',
                              chat_id=message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=None)
        bot.send_message(ID(message), 'Успешно добавил в корзину', reply_markup=types.ReplyKeyboardRemove())
        wishlist(call=call, friend_id=0, new_window=True)
    else:
        print('ошибка в done_cross_wishlist. при попытке заменить пожелания')
        bot.send_message(message.chat.id, 'Что-то пошло не так...', reply_markup=types.ReplyKeyboardRemove())


# -------УДАЛИТЬ-----------------------------------
def delete_wishlist(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=None)
    id = ID(call.message)
    crossed = False
    if 'crossed' in call.data.split('_'):
        crossed = True
    keyboard = start_keyboard(names=[str(i + 1) for i in range(User(id).count_of_wishes(crossed=crossed))],
                              one_time_keyboard=False, first='Готово', last='Все').row('Отмена')
    sent = bot.send_message(call.message.chat.id,
                            'Выберите пункты, которые следует удалить:',
                            reply_markup=keyboard)
    bot.register_next_step_handler(sent, poll_wishlist, call,
                                   None)  # переходим в poll_wishlist(sent, call, sent.message_id)


def done_delete_wishlist(message, call, wish_indexes):
    crossed = False
    if 'crossed' in call.data.split('_'):
        crossed = True
    wishes_to_delete = User(message.chat.id).get_wishlist_by_indexes(indexes=[i for i in wish_indexes], crossed=crossed)
    print('wishes to delete', wishes_to_delete)
    deleted = User(message.chat.id).delete_wishlist(wishes_to_delete=wishes_to_delete, crossed=crossed)
    print('DELETE = ', deleted)
    if deleted:
        bot.edit_message_text(text='Удаляю', chat_id=message.chat.id, message_id=call.message.message_id)
        bot.send_message(ID(message), 'Удаление прошло успешно!', reply_markup=types.ReplyKeyboardRemove())
        wishlist(call, 0, True)
    else:
        print('ошибка в done_delete_wishlist. при попытке delete пожелания')
        bot.send_message(message.chat.id, 'Что-то пошло не так...', reply_markup=types.ReplyKeyboardRemove())


# -------ОПРОС-----------------------------------
def poll_wishlist(message, call, numb=None):
    if numb is None:
        numb = []
    wish_indexes = numb
    data = call.data.split('_')
    """""""""""""""PREMIUM"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    if 'premium' in data:
        user_prem = True
    else:
        user_prem = False
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # --------NOT CROSSED---
    crossed = False
    # --------CROSSED--------
    if 'crossed' in data:
        crossed = True
    user = User(call.message.chat.id)
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    # --------ГОТОВО---------------------------------------------------------------------------------------------------
    if message.text == 'Готово':  # закончить ввод желаний
        print(wish_indexes)
        # ---------СВОЕВРЕМЕННОЕ ГОТОВО--------------------------------------------------------------------------------
        if len(wish_indexes) != 0:
            # --------ReEDIT-------------------------------------------------------------------------------------------
            if 'reedit' in data:
                print('reedit ready')
                sent = bot.send_message(message.chat.id,
                                        f'Изменить желания под номерами {", ".join([str(index + 1) for index in wish_indexes])}?',
                                        reply_markup=start_keyboard(['Да', 'Нет'],
                                                                    True))
            # --------RETURN-------------------------------------------------------------------------------------------
            elif 'return' in data:
                print('return ready')
                sent = bot.send_message(message.chat.id,
                                        f'Вернуть желания под номерами {", ".join([str(index + 1) for index in wish_indexes])}?',
                                        reply_markup=start_keyboard(['Да', 'Нет'],
                                                                    True))
            # --------CROSS--------------------------------------------------------------------------------------------
            elif 'cross' in data:
                print('cross ready')
                sent = bot.send_message(message.chat.id,
                                        f'Вычеркнуть желания под номерами {", ".join([str(index + 1) for index in wish_indexes])}?',
                                        reply_markup=start_keyboard(['Да', 'Нет'],
                                                                    True))
            # --------DELETE-----IND WISHLIST DELETE--------------------------------------------------------------------
            elif 'delete' in data:
                print('delete ready', wish_indexes)
                sent = bot.send_message(message.chat.id,
                                        f'Удалить желания под номерами {", ".join([str(index + 1) for index in wish_indexes])}?',
                                        reply_markup=start_keyboard(['Да', 'Нет'],
                                                                    True))
            else:
                ans(call, 'Ошибка')
                return
            bot.register_next_step_handler(sent, poll_wishlist, call,
                                           wish_indexes)  # Ждём следующий пункт. Либо кнопки Готово или Отмена
        # -----НЕСВОЕВРЕМЕННОЕ ГОТОВО----------------------------------------------------------------------------------
        else:
            # --------ДОБАВЛЯЕМ ПУНКТЫ---------------------------------------------------------------------------------
            keyboard = start_keyboard(
                names=[str(i + 1) for i in range(user.count_of_wishes(crossed=crossed))],
                # добавить в клавиатуру пункты желаний
                one_time_keyboard=False, first='Готово', last='Все').row('Отмена')
            sent = bot.send_message(message.chat.id, 'Не выбран ни один из пунктов', reply_markup=keyboard)
            bot.register_next_step_handler(sent, poll_wishlist, call,
                                           wish_indexes)  # ждём следующий пункт. Либо кнопки Готово или Отмена
    # --------ГОТОВО->ДА-----------------------------------------------------------------------------------------------
    elif message.text == 'Да':  # перепроверяем намеренность закончить выбор -> да
        # --------СВОЕВРЕМЕННОЕ ДА-------------------------------------------------------------------------------------
        print(wish_indexes, len(wish_indexes))
        if len(wish_indexes) != 0:  # если всё идёт по плану
            # --------ReEDIT-------------------------------------------------------------------------------------------
            if 'reedit' in data:
                print('reedit yes')
                keyboard = start_inline_keyboard({'Отмена': 'cancel'})
                """"""""
                bot.send_message(message.chat.id,
                                 "Желания, которые нужно отредактировать:", reply_markup=types.ReplyKeyboardRemove())
                for msg in range(len(wish_indexes)):
                    wishes_to_reedit = User(message.chat.id).get_wishlist_by_indexes([int(i) for i in wish_indexes])
                    bot.send_message(message.chat.id, f'{str(wish_indexes[msg] + 1)}. {wishes_to_reedit[msg]}')
                sent = bot.send_message(message.chat.id,
                                        f'Ответьте на сообщение с текстом желания, чтобы его изменить',
                                        reply_markup=keyboard)
                """"Работает"""

                bot.register_next_step_handler(sent, done_reedit_wishlist, wish_indexes)
            # --------RETURN-------------------------------------------------------------------------------------------
            elif 'return' in data:
                print('return yes')
                done_crossed_wishlist_return(call=call,
                                             message=message,
                                             wish_indexes=wish_indexes)
            # --------CROSS-------------------------------------------------------------------------------------------
            elif 'cross' in data:
                print('cross yes')
                done_cross_wishlist(message=message,
                                    call=call,
                                    wish_indexes=wish_indexes)
            # --------DELETE-------------------------------------------------------------------------------------------
            elif 'delete' in data and not user_prem:
                print('delete yes')
                done_delete_wishlist(message=message,
                                     call=call,
                                     wish_indexes=wish_indexes)
            # --------DELETE IND WISHLIST------------------------------------------------------------------------------
            elif 'delete' in data and user_prem:
                """""""""""""""PREMIUM"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                print('delete ind yes')
                done_premium_individualWishlist_delete(message=message,
                                                       call=call,
                                                       wish_indexes=wish_indexes)
                """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            else:
                print('ошибка в CВОЕВРЕМЕННОЕ ДА')
                pass
        # --------НЕСВОЕВРЕМЕННОЕ ДА (ХУЕВО, ЧТО ВООБЩЕ ТАК. НАДО БУДЕТ ИСПРАВИТЬ) UPD исправлено----------------------
        else:  # если кто-то сказал да заблаговременно
            """""""""""""""PREMIUM"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            if not user_prem:
                rng = user.count_of_wishes(crossed=crossed)
            else:
                try:
                    rng = Premium(call.message.chat.id).count_of_individualWishes(int(data[3]))
                except Exception as e:
                    print('ошибка в poll_wishlist. individual', e)
                    return
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            keyboard = start_keyboard(
                names=[str(i + 1) for i in range(rng)],
                # добавить в клавиатуру пункты желаний
                one_time_keyboard=False,
                first='Готово',
                last='Все').row('Отмена')
            sent = bot.send_message(message.chat.id, 'Не выбран ни один из пунктов', reply_markup=keyboard)
            bot.register_next_step_handler(sent, poll_wishlist, call,
                                           wish_indexes)  # Ждём следующий пункт. Либо кнопки Готово или Отмена
    # --------ГОТОВО->НЕТ----------------------------------------------------------------------------------------------
    elif message.text == 'Нет':  # перепроверяем намеренность закончить выбор -> нет
        """""""""""""""PREMIUM"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        if not user_prem:
            rng = user.count_of_wishes(crossed=crossed)
        else:
            try:
                rng = Premium(call.message.chat.id).count_of_individualWishes(int(data[3]))
            except Exception as e:
                print('ошибка в poll_wishlist. individual', e)
                return
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        keyboard = start_keyboard(
            names=[str(i + 1) for i in range(rng)],
            # добавить в клавиатуру пункты желаний
            one_time_keyboard=False, first='Готово', last='Все').row('Отмена')
        if len(wish_indexes) != 0:
            sent = bot.send_message(message.chat.id, 'Жду дополнений',
                                    reply_markup=keyboard)
        else:
            sent = bot.send_message(message.chat.id, 'Не выбран ни один из пунктов',
                                    reply_markup=keyboard)
        bot.register_next_step_handler(sent, poll_wishlist, call,
                                       wish_indexes)  # ждём следующий пункт. Либо кнопки Готово или Отмена
    # --------ВСЕ------------------------------------------------------------------------------------------------------
    elif message.text == 'Все':  # выбрать все
        """""""""""""""PREMIUM"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        if not user_prem:
            wish_indexes = [numb for numb in range(user.count_of_wishes(crossed=crossed))]
        else:
            wish_indexes = [numb for numb in
                            range(Premium(call.message.chat.id).count_of_individualWishes(int(data[3])))]
        """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        # --------ВСЁ НОМАРЛЬНО----------------------------------------------------------------------------------------
        if len(wish_indexes) != 0:
            # --------REEDIT-------------------------------------------------------------------------------------------
            if 'reedit' in data:
                print('reedit all')
                sent = bot.send_message(message.chat.id,
                                        f'Отредактировать все желания?',
                                        reply_markup=start_keyboard(['Да', 'Нет'],
                                                                    True))
            # --------RETURN-------------------------------------------------------------------------------------------
            elif 'return' in data:
                print('return all')
                sent = bot.send_message(message.chat.id,
                                        f'Вернуть все желания?',
                                        reply_markup=start_keyboard(['Да', 'Нет'],
                                                                    True))
            # --------CROSS-------------------------------------------------------------------------------------------
            elif 'cross' in data:
                print('cross all')
                print(wish_indexes)
                sent = bot.send_message(message.chat.id,
                                        f'Вычеркнуть все желания?',
                                        reply_markup=start_keyboard(['Да', 'Нет'],
                                                                    True))
            # --------DELETE----DELETE IND WISHLIST--------------------------------------------------------------------
            elif 'delete' in data:
                print('delete all')
                sent = bot.send_message(message.chat.id,
                                        f'Удалить все желания?',
                                        reply_markup=start_keyboard(['Да', 'Нет'],
                                                                    True))
            else:
                print('all error. passed')
                sent = bot.send_message(message.chat.id,
                                        f'Что-то пошло не так',
                                        reply_markup=None)
                pass
            bot.register_next_step_handler(sent, poll_wishlist, call,
                                           wish_indexes)  # ждём следующий пункт. Либо кнопки Готово или Отмена
        # --------ВСЁ НЕ НОРМАЛЬНО-------------------------------------------------------------------------------------
        else:
            sent = bot.send_message(message.chat.id,
                                    'Что-то пошло не так.\n\nОтчёт об ошибке уже отправлен разработчику, а вы пока попробуйте выбрать пункты по одному')
    # --------ОТМЕНА---------------------------------------------------------------------------------------------------
    elif message.text == 'Отмена':  # отменить ввод желаний
        bot.send_message(message.chat.id, 'Отмена прошла успешно', reply_markup=types.ReplyKeyboardRemove())
        # --------ReEDIT-------------------------------------------------------------------------------------------
        if 'reedit' in data:
            print('reedit cancel')
            bot.send_message(message.chat.id, f'Что делаем дальше?', reply_markup=start_inline_keyboard({
                'Повторить': 'wishlist_reedit',
                'Назад': 'wishlist'
            }))
        # --------RETURN-------------------------------------------------------------------------------------------
        elif 'return' in data:
            print('return cancel')
            bot.send_message(message.chat.id, f'Что делаем дальше?', reply_markup=start_inline_keyboard({
                'Повторить': 'wishlist_crossed_return',
                'Назад': 'wishlist'
            }))
        # --------CROSS-------------------------------------------------------------------------------------------
        elif 'cross' in data:
            print('cross cancel')
            bot.send_message(message.chat.id, f'Что делаем дальше?', reply_markup=start_inline_keyboard({
                'Повторить': 'wishlist_cross',
                'Назад': 'wishlist'
            }))
        # --------DELETE-------------------------------------------------------------------------------------------
        if 'delete' in data and not user_prem:
            print('delete cancel')
            bot.send_message(message.chat.id, f'Что делаем дальше?', reply_markup=start_inline_keyboard({
                'Повторить': 'wishlist_delete',
                'Назад': 'wishlist'
            }))
        if 'delete' in data and user_prem:
            """""""""""""""PREMIUM"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            print('delete ind wishlist cancel')
            bot.send_message(message.chat.id, f'Что делаем дальше?', reply_markup=start_inline_keyboard({
                'Повторить': call.data,
                'Назад': f'premium_individualWishlists_id_{data[3]}'
            }))
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
        elif 'reserve' in data:
            wishlist(call=call, friend_id=int(data[4]), new_window=True)
        else:
            print('ошибка в ОТМЕНА')
            pass
    # --------ЧИСЛО----------------------------------------------------------------------------------------------------
    else:
        # print([i for i in message.text.split()], all([i for i in message.text.split()]))
        for msg in [i for i in message.text.split()]:  # проверка на то, что введённое значение является числом
            try:
                int(msg)
            except Exception as e:  # если что-то не так
                print(e, '|number. for else error|')
                sent = bot.send_message(message.chat.id, 'Введённое значение не является числом', reply_markup=None)
                break
        # --------НОРМАЛЬНОЕ ЧИСЛО-------------------------------------------------------------------------------------
        else:  # если всё хорошо
            print(data)
            # --------RESERVE--------------------------------------------------------------------
            if 'reserve' in data:
                # rng = user.get_reserved_wishes(int(data[4]))[int(data[4])]['indexes']
                rng = User(int(data[4])).count_of_wishes()
                if Premium(int(data[4])).belong():
                    rng += Premium(int(data[4])).count_of_individualWishes(message.chat.id)
                print(f'count wishes = {rng}')
                if int(message.text) in [int(i + 1) for i in
                                         range(rng)]:  # проверка на наличие числа среди пунктов желаний
                    index = int(message.text) - 1
                    # print(f'msg text = {message.text}, index = {index}')
                    # bot.send_message(message.chat.id, 'Записал')
                    done_reserve_wishlist(call=call, index=index)
                    return
                # --------НЕВЕРНОЕ ЧИСЛО-----------------------------------------------------------------------------------
                else:
                    bot.send_message(message.chat.id, 'Неверное число')
            else:
                # --------NOT RESERVE--------------------------------------------------------------------
                if not user_prem:
                    rng = user.count_of_wishes(crossed=crossed)
                else:
                    rng = Premium(call.message.chat.id).count_of_individualWishes(int(data[3]))
                # --------ПРОВЕРКА ЧИСЛА НА СООТВТСТВИЕ--------------------------------------------------------------------
                if int(message.text) in [int(i + 1) for i in
                                         range(rng)]:  # проверка на наличие числа среди пунктов желаний
                    if int(message.text) - 1 in wish_indexes:
                        sent = bot.send_message(message.chat.id, 'Уже записано')
                    else:
                        wish_indexes.append(int(message.text) - 1)
                        wish_indexes = list(set(wish_indexes))
                        # print(message.text, wish_indexes)
                        sent = bot.send_message(message.chat.id, 'Записал')
                # --------НЕВЕРНОЕ ЧИСЛО-----------------------------------------------------------------------------------
                else:
                    sent = bot.send_message(message.chat.id, 'Введено неверное число')
        bot.register_next_step_handler(sent,
                                       poll_wishlist,
                                       call,
                                       wish_indexes)  # Ждём следующий пункт. Либо кнопки Готово или Отмена


def premium(call):
    ans(call)
    if Premium(call.message.chat.id).belong():
        bot.edit_message_text(
            text='Премиум  функции.\n\n'
                 'Статистика: вы можете увидеть количество человек, просмотревших ваш список желаний за нынешнюю неделю\n\n'
                 'Индивидуальные списки позволят вам добавить уникальные желания для каждого из отслеживающих!\n'
                 'Режим "Дополнить" покажет индивидуальные желания сразу после основных, которые вы добавили во вкладке "Список желаний".\n'
                 'Режим "Перезаписать" оставить лишь те желания, которые вы добавили во вкладке "Индивидуальные списки".\n\n'
                 'Помимо тех активных функций, что описаны выше, вам также предоставлены и пассивные:\n'
                 'Вам виден тарифный план пользователя (Стандартный, Премиум);\n'
                 'Максимальное количество пунктов в списке желаний увеличено с 32 до 1000;\n'
                 'Максимальное количество отслеживаемых пользователей увеличено с 16 до 48;\n',
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=start_inline_keyboard({'Статистика': 'premium_stats',
                                                'Индивидуальные списки': 'premium_individualWishlists',
                                                'Назад': 'account'}, buttons_in_row=1))
    else:
        bot.edit_message_text(text='Что даёт премиум доступ?\n\n'
                                   'Статистика покажет вам количество человек, просмотревших ваш список желаний за нынешнюю неделю.\n\n'
                                   'Индивидуальные списки позволят вам добавить уникальные желания для каждого из отслеживающих!\n\n'
                                   'Сможете видеть тарифный план пользователя (Стандартный, Премиум).\n\n'
                                   'Максимальное количество пунктов в списке желаний будет увеличено с 128 до 1000.\n\n'
                                   'Максимальное количество отслеживаемых пользователей будет увеличено с 16 до 48.\n\n'
                              # 'Система категорий желаний\n'
                              # 'Экспортировать в разные форматы (Excel, png, csv)'
                              ,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=start_inline_keyboard({'Оформить': 'premium_get',
                                                                  'Назад': 'account'}))


def got_premium(chat_id: int, product_name: str, message_id: int = None):
    if message_id is not None:
        try:
            bot.delete_message(chat_id=chat_id,
                               message_id=message_id)
        except Exception as e:
            print('ошибка при удалении сообщения. Вероятно, оно старше 48 часов\n\n', e)
            bot.edit_message_text(chat_id=chat_id,
                                  message_id=message_id,
                                  text='Удалено')
    bot.send_message(chat_id, 'Отлично! Вы только что приобрели премиум доступ.\nЧтобы '
                              'воспользоваться новыми функциями, перейдите в соответствующее '
                              'меню.\nОно находится во вкладке Аккаунт » Премиум функции; либо по '
                              'кнопке ниже!',
                     reply_markup=start_inline_keyboard({'Премиум функции': 'premium'}))


def notify_premium(chat_id: int, days: int):
    if days != 1:
        bot.send_message(chat_id, f'Через {days} дня кончится премиум доступ!', disable_notification=True)
    else:
        bot.send_message(chat_id,
                         f'Завтра вы потеряете доступ к премиум функциям! Напоминаю, чтобы это не стало для вас неожиданностью',
                         disable_notification=True)


def lost_premium(chat_id: int):
    bot.send_message(chat_id,
                     'Премиум доступ закончился!\n\nБольшое спасибо, что оформили премиум доступ, но, к сожалению, подошла дата окончания подписки. Надеюсь, я был вам полезен!\n\nЕщё увидимся 👋',
                     disable_notification=True)


def premium_get(call, new_window: bool = False):
    positions = {'Ежемесячная подписка — 25₽': 0,
                 'Годовая подписка — 250₽': 1,
                 'Пожизненный доступ — 475₽': 2}
    names = {}
    for position in positions.keys():
        names.update({position: f'premium_get_{positions.get(position)}'})
    names.update({'Отмена': 'account'})
    keyboard = start_inline_keyboard(names, 1)
    if not new_window:
        bot.edit_message_text(text='Пожалуйста, выберите тарифный план',
                              chat_id=ID(call.message),
                              message_id=call.message.message_id,
                              reply_markup=keyboard)
    else:
        try:
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
        except Exception as e:
            print('ошибка при удалении сообщения. Вероятно, оно старше 48 часов\n\n', e)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text='Удалено')
        bot.send_message(text='Пожалуйста, выберите тарифный план',
                         chat_id=ID(call.message),
                         reply_markup=keyboard)


def premium_get_pay(call):
    product_index = int(call.data.split('_')[2])
    prices = [[types.LabeledPrice(label='Ежемесячная подписка', amount=25), 'Отличный вариант, если отмечаете лишь '
                                                                            'основные праздники',
               'https://sun9-85.userapi.com/impg/Cn8o5M1S-cxFPcplYmZJtZciLx_r6oNO5Iv5Bw/cfZq3tbLfdE.jpg?size=300x300&quality=95&sign=82f0b64375f75cc16e26a93c880fd5bb&type=album'],
              [types.LabeledPrice(label='Годовая подписка', amount=250), 'Прекрасно подойдёт, если каждый праздник '
                                                                         'для вас событие!',
               'https://sun9-8.userapi.com/impg/0C-Ca6jCfn6bxGQyQtyQMfEQ3iiC5Jxp3ymW7g/CDWRJMqyzE4.jpg?size=300x300&quality=95&sign=a1906137fb45a1bfd8d559b20c588964&type=album'],
              [types.LabeledPrice(label='Пожизненный доступ', amount=475), 'Если вы не представляете жизни без меня '
                                                                           'и не хотите запариваться по поводу '
                                                                           'подписки!\nКупил её один раз и забыл '
                                                                           'навсегда!',
               'https://sun9-52.userapi.com/impg/OeOXzU4v-sAMhha8-0lrEOsSlHhOY_uctuRLmA/zTIz021Em0k.jpg?size=300x300&quality=95&sign=16bc7594a44041504601d77436d96629&type=album']]
    from payments.kassa import create_payment, create_text
    try:
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
    except Exception as e:
        print('ошибка при удалении сообщения. Вероятно, оно старше 48 часов\n\n', e)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Удалено')
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1).add(
        *[telebot.types.InlineKeyboardButton(text='Формирую...',
                                             url='https://t.me/wishnya_wish_bot')],
        telebot.types.InlineKeyboardButton(text='Назад', callback_data='premium_get'))
    sent = bot.send_photo(chat_id=call.message.chat.id,
                          photo=f'{prices[product_index][2]}',
                          caption=create_text(prices[product_index][0].amount,
                                              prices[product_index][0].label,
                                              prices[product_index][1]),
                          # reply_markup=start_inline_keyboard({'Формирую ссылку...': 'pass', 'Отмена': 'premium_get'}, 1),
                          reply_markup=keyboard,
                          )
    link = create_payment(
        amount=prices[product_index][0].amount,
        name=prices[product_index][0].label,
        message_id=sent.message_id,
        user_id=sent.chat.id
    )
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1).add(*[telebot.types.InlineKeyboardButton(text='Купить',
                                                                                                        url=f'{link}')],
                                                                   telebot.types.InlineKeyboardButton(text='Назад',
                                                                                                      callback_data='premium_get'))
    bot.edit_message_reply_markup(chat_id=sent.chat.id,
                                  message_id=sent.message_id,
                                  reply_markup=keyboard)


def premium_individualWishlists(call, page_number: int):
    page_index = page_number - 1
    user_id = ID(call.message)
    if Premium(user_id).belong():
        user = User(user_id)
        list_friends = user.get_on_the_list()
        if len(list_friends) == 0:
            ans(call, 'Список отслеживающих пуст')
        elif list_friends is None:
            ans(call, 'Ошибка')
        else:
            couples = get_friends_couples(list_of_friends=list_friends,
                                          friends_on_page=8)  # разбиваем друзей по кучкам (в нашем случае, по 8 человек на страницу)
            couple = couples[page_index]
            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)  # создаём клавиатуру с 2 людьми в строке
            buttons = []  # пустой массив кнопок с друзьями
            print("friend_couples -> ", couples)
            print('couple -> ', couple)
            for i in range(len(couple)):  # идём по каждому другу в кучке
                deleted_friends = 0
                friend = User(couple[i]).get_info()  # собираем информацию о друге
                if friend is None:
                    deleted_friends += 1
                    continue
                print(f'friend {i} -> ', friend)
                data = f'premium_individualWishlists_id_{friend["id"]}'
                if friend['username'] is not None:  # если username есть
                    buttons.append(
                        telebot.types.InlineKeyboardButton(  # заполняем массив кнопок с друзьями
                            f'"{str(friend["name"])}" {str(friend["username"])}',
                            callback_data=data
                        )
                    )
                else:  # если username нет
                    buttons.append(
                        telebot.types.InlineKeyboardButton(  # заполняем массив кнопок с друзьями
                            f'{str(friend["name"])}',
                            callback_data=data
                        )
                    )
            for button in buttons:
                keyboard.row(button)  # добавляем друзей в клавиатуру
            if len(couples) != 1:
                prev = telebot.types.InlineKeyboardButton('« Назад',
                                                          callback_data=f'premium_individualWishlists_prev_{page_number - 1}_{len(couples)}')  # кнопка назад
                next = telebot.types.InlineKeyboardButton('Дальше »',
                                                          callback_data=f'premium_individualWishlists_next_{page_number + 1}_{len(couples)}')
                keyboard.add(prev, next)
            message_text = f'Индивидуальные списки желаний.\nСтраница {page_number} из {len(couples)}'
            menu = telebot.types.InlineKeyboardButton('Вернуться в меню', callback_data='menu')
            keyboard.row(menu)
            bot.edit_message_text(chat_id=user_id,  # меняем и текст
                                  message_id=call.message.message_id,
                                  reply_markup=keyboard,
                                  text=message_text)
    else:
        ans(call, 'У вас нет доступа к данной функции')


def premium_individualWishlist(call, friend_id, new_window: bool = False):
    user_id = ID(call.message)
    user_premium = Premium(user_id)
    if user_premium.belong():
        db_call = user_premium.get_individual_wishlist(friend_id=friend_id)
        ind_wishlist = db_call[0]
        mode = db_call[1]
        print('ind_wishlist = ', ind_wishlist, "mode = ", mode)
        if mode == 'add':
            mode = 'Дополнить'
            if ind_wishlist is not None:
                wsh = User(user_id).get_wishlist()
                print('wsh =', wsh)
                if wsh == -1:
                    wishes = sorted_wishlist(ind_wishlist)
                else:
                    wishes = sorted_wishlist(wsh + ind_wishlist)
            else:
                wsh = User(user_id).get_wishlist()
                print('wsh =', wsh)
                if wsh == -1:
                    wishes = None
                else:
                    wishes = sorted_wishlist(wsh)
            print(wishes)
        else:
            mode = 'Перезаписать'
            if ind_wishlist is not None:
                wishes = sorted_wishlist(ind_wishlist)
            else:
                wishes = None
        name = User(friend_id).get_name()
        if wishes is not None:
            if not new_window:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      text=f'Индивидуальный список желаний, созданный для пользователя под именем\n{name}\n\n'
                                           f'Режим отображения: {mode}\n\n'
                                           f'{wishes}',
                                      reply_markup=
                                      add_back(
                                          keyboard=add_back(
                                              keyboard=start_inline_keyboard(
                                                  {'Удалить': f'premium_individualWishlists_id_{friend_id}_delete',
                                                   'Добавить': f'premium_individualWishlists_id_{friend_id}_add'},
                                                  buttons_in_row=2),
                                              back_button={
                                                  'Сменить режим': f'premium_individualWishlists_id_{friend_id}_mode'}
                                          ),
                                          back_button={'Назад': 'premium_individualWishlists'}
                                      )
                                      )
            else:
                bot.send_message(chat_id=user_id,
                                 text=f'Индивидуальный список желаний, созданный для пользователя под именем\n{name}\n\n'
                                      f'Режим отображения: {mode}\n\n'
                                      f'{wishes}',
                                 reply_markup=
                                 add_back(
                                     keyboard=add_back(
                                         keyboard=start_inline_keyboard(
                                             {'Удалить': f'premium_individualWishlists_id_{friend_id}_delete',
                                              'Добавить': f'premium_individualWishlists_id_{friend_id}_add'},
                                             buttons_in_row=2),
                                         back_button={
                                             'Сменить режим': f'premium_individualWishlists_id_{friend_id}_mode'}
                                     ),
                                     back_button={'Назад': 'premium_individualWishlists'}
                                 )
                                 )
        else:
            if not new_window:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=call.message.message_id,
                                      text=f'Индивидуальный список желаний {name} пуст!\n\nОбратите внимание, что ваш друг на '
                                           f'данный момент не видит желания, которые вы добавили во вкладке "Список желаний". '
                                           f'Чтобы это изменить, поменяйте режим отображения с "Перезаписать" на "Дополнить" по кнопке внизу 👇\n\n'
                                           f'Режим отображения: {mode}',
                                      reply_markup=start_inline_keyboard(
                                          {'Добавить': f'premium_individualWishlists_id_{friend_id}_add',
                                           'Сменить режим': f'premium_individualWishlists_id_{friend_id}_mode',
                                           'Назад': 'premium_individualWishlists'
                                           },
                                          buttons_in_row=2)
                                      )
            else:
                bot.send_message(chat_id=user_id,
                                 text=f'Индивидуальный список желаний {name} пуст!\n\nОбратите внимание, что ваш друг на '
                                      f'данный момент не видит желания, которые вы добавили во вкладке "Список желаний". '
                                      f'Чтобы это изменить, поменяйте режим отображения с "Перезаписать" на "Дополнить" по кнопке внизу 👇\n\n'
                                      f'Режим отображения: {mode}',
                                 reply_markup=start_inline_keyboard(
                                     {'Добавить': f'premium_individualWishlists_id_{friend_id}_add',
                                      'Сменить режим': f'premium_individualWishlists_id_{friend_id}_mode',
                                      'Назад': 'premium_individualWishlists'
                                      },
                                     buttons_in_row=2)
                                 )
    else:
        ans(call, 'У вас нет доступа к данной функции')


def premium_individualWishlist_add(call, friend_id):
    ans(call)
    user_id = call.message.chat.id
    cancel_keyboard = start_inline_keyboard({'Назад': f'cancel_prem_{friend_id}'}, 1)
    sent = bot.edit_message_text(chat_id=user_id,
                                 message_id=call.message.message_id,
                                 text='Можете перечислить новые пожелания!\n'
                                      'Пункты отделяйте переносом строки, нумерация проставляется автоматически',
                                 reply_markup=cancel_keyboard)
    bot.register_next_step_handler(sent, done_premium_individualWishlist_add, call, friend_id)


def done_premium_individualWishlist_add(message, call, friend_id):
    user_id = message.chat.id
    user_premium = Premium(user_id)
    if user_premium.belong():
        if user_premium.add_individual_wishes(friend_id, message.text.split('\n')):  # если успешно добавилось
            print('premium_individualWishlist_added. wishes to add -> ', message.text.split('\n'))
            bot.edit_message_text(chat_id=message.chat.id,
                                  message_id=call.message.message_id,
                                  text='Добавляю')
            bot.send_message(user_id, 'Успешно добавил', reply_markup=types.ReplyKeyboardRemove())
            premium_individualWishlist(call=call,
                                       friend_id=friend_id,
                                       new_window=True)
        else:
            print('Что-то пошло не так в add_wishlist')
    else:
        ans(call, 'У вас нет доступа к данной функции')


# -------УДАЛИТЬ-----------------------------------
def premium_individualWishlist_delete(call, friend_id):
    id = ID(call.message)
    user_prem = Premium(id)
    if user_prem.belong():
        count = user_prem.count_of_individualWishes(friend_id=friend_id)
        if count is not None:

            bot.edit_message_reply_markup(chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=None)
            keyboard = start_keyboard(names=[str(i + 1) for i in range(count)],
                                      one_time_keyboard=False, first='Готово', last='Все').row('Отмена')
            sent = bot.send_message(call.message.chat.id,
                                    'Выберите пункты, которые следует удалить:',
                                    reply_markup=keyboard)
            bot.register_next_step_handler(sent, poll_wishlist, call,
                                           None)  # переходим в poll_wishlist(sent, call, sent.message_id)
        else:
            ans(call, 'Индивидуальный список пуст')
    else:
        ans(call, 'У вас нет доступа к данной функции')


def done_premium_individualWishlist_delete(message, call, wish_indexes):
    user_prem = Premium(message.chat.id)
    friend_id = int(call.data.split('_')[3])
    if user_prem.belong():
        wishes_to_delete = user_prem.get_individual_wishlist_by_indexes(indexes=[i for i in wish_indexes],
                                                                        friend_id=friend_id)
        print('wishes to delete', wishes_to_delete)
        deleted = user_prem.delete_individual_wishes(friend_id=friend_id,
                                                     wishes_to_delete=wishes_to_delete)
        print('DELETE = ', deleted)
        if deleted:
            bot.edit_message_text(text='Удаляю', chat_id=message.chat.id, message_id=call.message.message_id)
            bot.send_message(ID(message), 'Удаление прошло успешно!', reply_markup=types.ReplyKeyboardRemove())
            premium_individualWishlist(call, friend_id, True)
        else:
            print('ошибка в done_premium_individualWishlist_delete. при попытке delete пожелания')
            bot.send_message(message.chat.id, 'Что-то пошло не так...', reply_markup=types.ReplyKeyboardRemove())
    else:
        ans(call, 'У вас нет доступа к данной функции')


def premium_individualWishlist_mode(call, friend_id):
    user_id = ID(call.message)
    user_prem = Premium(user_id)
    if user_prem.belong():
        print('changed?', user_prem.change_mode(friend_id=friend_id))
        premium_individualWishlist(call=call, friend_id=friend_id)
    else:
        ans(call, 'У вас нет доступа к данной функции')


def premium_stats(call):
    ans(call)
    prem = Premium(call.message.chat.id)
    if prem.belong():
        view_count = len(Premium(ID(call.message)).get_views())
        if view_count != 0:
            bot.edit_message_text(chat_id=ID(call.message),
                                  text=f'За нынешнюю неделю твой список желаний просмотрели {view_count} человек!',
                                  message_id=call.message.message_id,
                                  reply_markup=start_inline_keyboard({'Назад': 'premium'}))
        else:
            bot.edit_message_text(chat_id=ID(call.message),
                                  text=f'За нынешнюю неделю твой список желаний никто не просмотрел :(',
                                  message_id=call.message.message_id,
                                  reply_markup=start_inline_keyboard({'Назад': 'premium'}))
    else:
        ans(call, text='Чтобы пользоваться премиум возможностями нужен Премиум')


def ans(call, text: str = ''):
    bot.answer_callback_query(callback_query_id=call.id, text=text)


@bot.message_handler(content_types=['text'])
def text(message):
    print(message.text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    id = call.message.chat.id
    try:
        if call.message:
            if registered(id):
                data = call.data.split('_')
                print(data)
                if data[0] == 'createRequest':  # добавления друзей при регистрации
                    create_request(call)
                    # bot.edit_message_text(
                    #     text=f'Держи бессрочную ссылку с заявкой на добавление в список отслеживаемы:\n\n{create_request_link(id)}\n\nПросто перешли её своим друзьям',
                    #     chat_id=id,
                    #     message_id=call.message.message_id,
                    #     reply_markup=start_inline_keyboard({'Назад': 'friends'}))
                    ans(call)
                elif data[0] == 'account':
                    if len(data) == 1:
                        ans(call)
                        account_settings(call)
                    elif data[1] == 'update':
                        ans(call)
                        account_update(call)
                    elif data[1] == 'delete':
                        ans(call)
                        if len(data) == 2:
                            delete_account(call=call,
                                           deleting_mode=False)
                        else:
                            if data[2] == 'yes':
                                delete_account(call=call,
                                               deleting_mode=True)
                            else:
                                account_settings(call)
                elif data[0] == 'friends':
                    # -----СПИСОК ОТСЛЕЖИВАЕМЫХ------СПИСОК ОТСЛЕЖИВАЮЩИХ-----СПИСОК ДРУЗЕЙ-----------------------------------------
                    if len(data) == 2:
                        friend_list(call, 1)
                    elif (len(data) == 3) or (len(data) == 4):
                        if data[2] == 'deleteAll':
                            # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
                            if data[1] == 'subscribers':
                                if len(data) == 3:
                                    subscriber_deleteAll(call)
                                elif len(data) == 4:
                                    if data[3] == 'yes':
                                        subscriber_deleteAll(call, True)
                                    else:
                                        friend_list(call, 1)
                            # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
                            elif data[1] == 'subscribes':
                                if len(data) == 3:
                                    unsubscribe_all(call)
                                elif len(data) == 4:
                                    if data[3] == 'yes':
                                        unsubscribe_all(call, True)
                                    else:
                                        friend_list(call, 1)
                            # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
                            else:
                                pass
                        elif data[2] == 'acceptAll':
                            # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
                            if data[1] == 'subscribers':
                                pass
                    elif any(i == data[2] for i in ['prev', 'next']):
                        page_number = int(data[3])
                        pages = int(data[4])
                        if page_number < 1 or page_number > pages:
                            ans(call, 'Конец списка')
                        else:
                            friend_list(call, page_number)
                elif data[0] == 'friend':
                    # -----МЕНЮ ПОЛЬЗОВАТЕЛЯ-----------------------------------------------------------------------------------------------
                    if data[2] == 'id':
                        id = int(data[3])
                        # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
                        if data[1] == 'subscribers':
                            subscriber(call, id)
                        # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
                        elif data[1] == 'subscribes':
                            wishlist(call=call, friend_id=id, new_window=False)
                        # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
                        else:
                            wishlist(call=call, friend_id=id, new_window=False)
                    # -----ЗАРЕЗЕРВИРОРОТЬ-----------------------------------------------------------------------------------------------
                    elif data[2] == 'reserve':
                        reserve_wishlist(call)
                    # -----УДАЛИТЬ ПОЛЬЗОВАТЕЛЯ-----------------------------------------------------------------------------------------------
                    elif data[2] == 'delete':
                        id = int(data[3])
                        if len(data) == 5:
                            if data[4] == 'yes':
                                # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
                                if data[1] == 'subscribers':
                                    subscriber_delete(call, True)
                                # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
                                elif data[1] == 'subscribes':
                                    unsubscribe(call, True)
                                # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
                                else:
                                    delete_friend(call, True)
                            elif data[4] == 'no':
                                # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
                                if data[1] == 'subscribers':
                                    subscriber(call, id)
                                # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
                                elif data[1] == 'subscribes':
                                    wishlist(call=call, friend_id=id, new_window=False)
                                # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
                                else:
                                    wishlist(call=call, friend_id=id, new_window=False)
                        else:
                            # -----СПИСОК ОТСЛЕЖИВАЮЩИХ-----------------------------------------------------------------------------------------------
                            if data[1] == 'subscribers':
                                subscriber_delete(call, False)
                            # -----СПИСОК ОТСЛЕЖИВАЕМЫХ-----------------------------------------------------------------------------------------------
                            elif data[1] == 'subscribes':
                                unsubscribe(call, False)
                            # -----СПИСОК ДРУЗЕЙ-----------------------------------------------------------------------------------------------
                            else:
                                delete_friend(call, False)
                    elif data[2] == 'add':
                        if data[1] == 'subscribers':
                            add_friend(call)
                # ---------МЕНЮ-----------------------------------------------------------------------------
                elif call.data == 'menu':
                    menu(call.message, True)
                    ans(call)
                elif data[0] == 'premium':
                    if len(data) == 1:
                        premium(call)
                    elif len(data) > 1:
                        if data[1] == 'stats':
                            premium_stats(call)
                        elif data[1] == 'individualWishlists':
                            print(data)
                            if len(data) == 2:
                                premium_individualWishlists(call, 1)
                            elif any(i == data[2] for i in ['prev', 'next']):
                                page_number = int(data[3])
                                pages = int(data[4])
                                # -----------СПИСОК ОТСЛЕЖИВАЮЩИХ--------------------------------------------------------------
                                if page_number < 1 or page_number > pages:
                                    ans(call, 'Конец списка')
                                else:
                                    premium_individualWishlists(call, page_number)
                            elif data[2] == 'id':
                                if data[3].isdigit():
                                    friend_id = int(data[3])
                                    if len(data) == 5:
                                        if data[4] == 'mode':
                                            premium_individualWishlist_mode(call, friend_id)
                                        elif data[4] == 'add':
                                            premium_individualWishlist_add(call, friend_id)
                                        elif data[4] == 'delete':
                                            if Premium(ID(call.message)).get_individual_wishlist(friend_id)[1] == 'add':
                                                premium_individualWishlist_mode(call=call, friend_id=friend_id)
                                            premium_individualWishlist_delete(call, friend_id)
                                    else:
                                        premium_individualWishlist(call, friend_id)
                                else:
                                    ans(call, 'Ошибка')
                                # premium_individualWishlists_id_
                        elif data[1] == 'get':
                            if len(data) == 3:
                                if data[2].isdigit():
                                    premium_get_pay(call)
                            else:
                                print('+++++++++++++++++++++++++++++++++++++')
                                print(call.message.content_type)
                                print('+++++++++++++++++++++++++++++++++++++')
                                ans(call)
                                # if call.message.invoice is None:
                                if call.message.content_type == 'text':
                                    premium_get(call)
                                else:
                                    premium_get(call, True)
                # ---------СПИСОК ЖЕЛАНИЙ-----------------------------------------------------------------------------
                elif data[0] == 'wishlist':  # работаем со списком желаний
                    # ---------НАЧАЛЬНАЯ СТРАНИЦА WISHLIST()----------------------------------------------------------
                    if len(data) == 1:  # первый запуск (меню "показать" "изменить")
                        wishlist(call)
                    # ---------ДОБАВИТЬ ЖЕЛАНИЯ-----------------------------------------------------------------------
                    elif data[1] == 'add':
                        add_wishes(call)
                    # ---------ИЗМЕНИТЬ СПИСОК ЖЕЛАНИЙ (РЕДАКТИРОВАТЬ ИЛИ УДАЛИТЬ)------------------------------------
                    elif data[1] == 'edit':  # изменить список
                        wishlist_editor(call)
                    # ---------РЕДАКТИРОВАТЬ---------------------------------------------------------------------------
                    elif data[1] == 'reedit':  # изменить список
                        # ---------ПЕРВЫЙ ЗАПУСК МЕНЮ------------------------------------------------------------------
                        reedit_wishlist(call)
                    elif data[1] == 'delete':  # удалить пункты
                        delete_wishlist(call)
                    # ---------ВЫЧЕРКНУТЬ------------------------------------------------------------------------------
                    elif data[1] == 'cross':
                        cross_wishlist(call)
                    # ---------ВЫЧЕРКНУТЫЕ-----------------------------------------------------------------------------
                    elif data[1] == 'crossed':
                        # ---------МЕНЮ ВЫЧЕРКНУТЫХ ЖЕЛАНИЙ------------------------------------------------------------
                        if len(data) == 2:
                            crossed_wishlist(call)
                        # ---------ВЕРНУТЬ ЖЕЛАНИЯ---------------------------------------------------------------------
                        elif data[2] == 'return':
                            crossed_wishlist_return(call)
                        # ---------УДАЛИТЬ ВЫЧЕРКНУТЫЕ ЖЕЛАНИЯ---------------------------------------------------------
                        elif data[2] == 'delete':
                            delete_wishlist(call)
                    elif data[1] == 'reserve':
                        reserve_wishlist(call)
                    else:
                        print('Что-то не так с wishlist')
                    ans(call)
                elif data[0] == 'admin':
                    ids = select_call("SELECT id FROM users;")
                elif data[0] == 'cancel':
                    if len(data) == 3:
                        if data[1] == 'prem':
                            ans(call)
                            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
                            premium_individualWishlist(call=call,
                                                       friend_id=data[2])
                    else:
                        ans(call)
                        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
                        wishlist(call)
                elif call.data == 'skip':  # ничего не делать
                    ans(call)
                    pass
                else:
                    print('callback error')
            else:
                bot.send_message(id,
                                 'Чтобы пользоваться функциями бота нужно зарегистрироваться!\nЖми /registration')
                ans(call)
        ans(call)
    except Exception as e:
        print(repr(e))


def bot_polling():
    # print('bot is running')
    bot.polling(
        none_stop=True
    )
