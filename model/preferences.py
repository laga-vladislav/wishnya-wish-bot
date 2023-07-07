import datetime

from database.dbase import *


def get_index_from_msg(message_text: str):
    words = message_text.split('. ', 1)
    answers = []
    print('words == ', words)
    for word in words:
        print('word == ', word)
        if word.isdigit():
            answers.append(word)
    if len(answers) == 0:
        print('error in "get_index_from_msg". msg has no indexes')
        return None
    elif len(answers) > 1:
        print('error in "get_index_from_msg". msg has too much indexes: ', len(answers))
        return None
    else:
        print('"get_index_from_msg" ok')
        return int(answers[0]) - 1


def get_word_from_msg(message_text: str):
    words = message_text.split('. ', 1)
    answers = []
    print('words == ', words)
    for word in words:
        print('word == ', word)
        if word.isdigit():
            pass
        else:
            answers.append(word)
    if len(answers) == 0:
        print('error in "get_word_from_msg". msg has no words')
        return None
    elif len(answers) > 1:
        print('error in "get_word_from_msg". msg has too much words: ', len(answers))
        return None
    else:
        print('"get_word_from_msg" ok')
        return answers[0]


def get_wish_from_msg(message_text: str, wishlist: list):
    words = message_text.split('. ', 1)
    # 1. 3. ГОВНО исправь
    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    for word in words:
        if compare(word, wishlist):
            return word
    return None


def compare(word: str, array: list):
    # word = word.lower()
    for i in array:
        k = 0
        if len(i) > len(word):
            for j in range(len(word)):
                if word[j] == i[j]:
                    pass
                else:
                    k += 1
        else:
            for j in range(len(i)):
                if word[j] == i[j]:
                    pass
                else:
                    k += 1
        k += abs(len(i) - len(word))
        if 7 > len(word) > 4 and k < 2:
            return i
        elif 7 <= len(word) < 12 and k < 3:
            return i
        elif len(word) > 11 and k < 3:
            return i
        elif len(word) <= 4 and k < 1:
            return i
    return False


def remove_forbidden_signs(words: list, signs: dict):
    new_words = []
    for word in words:
        for sign in signs:
            if sign in word:
                word = word.replace(sign, signs[sign])
        new_words.append(word)
    return new_words


def get_friends_couples(list_of_friends: list, friends_on_page: int):
    couples_of_friends = []
    count = 0
    couple = []
    for i in range(len(list_of_friends)):
        if (count / friends_on_page) == int(count / friends_on_page) and count != 0:
            # print(couple)
            couples_of_friends.append(couple)
            couple = [list_of_friends[i]]
        else:
            couple.append(list_of_friends[i])
        count += 1
        if count == len(list_of_friends):
            # print(couple)
            couples_of_friends.append(couple)
    return couples_of_friends


def decipher_request_link(new_id: str):
    try:
        links = select_call("SELECT invite_link, invite_key FROM users;")
        for link in links:
            if new_id == link[0]:
                from model.crypt import Crypt
                return Crypt(new_id).decrypt(int(link[1]))
        raise Errors('userNotFound')
    except Errors as e:
        return e


def registered(id: int):  # проверка на присутствие в базе данных
    try:
        if select_call(f"SELECT * FROM users WHERE id = {id}"):
            return True
        else:
            return False
    except:
        return False


def in_the_wishlist(id, crossed: bool = False):  # проверка на присутствие в базе данных
    if not crossed:
        if select_call(f"SELECT * FROM wishlist WHERE id = {id}"):
            return True
        else:
            return False
    else:
        if select_call(f"SELECT * FROM crossed_wishlist WHERE id = {id}"):
            return True
        else:
            return False


def add_to_wishlist(id, crossed: bool = False):  # регистрация в базе данных
    if not crossed:
        if not in_the_wishlist(id):
            print(id)
            insert_call(f"INSERT INTO wishlist (id, wishes) VALUES ({id}, '')")
            print('Успешно добавил')
            return True
        else:
            print('не успешно добавил')
            return False
    else:
        if not in_the_wishlist(id, crossed=True):
            print(id)
            insert_call(f"INSERT INTO crossed_wishlist (id, wishes) VALUES ({id}, '')")
            print('Успешно добавил')
            return True
        else:
            print('не успешно добавил')
            return False


def configure_list_to_str_wishes(wishlist: list):
    wishes_str = ';'.join([change_to_upper(wish) for wish in wishlist])
    return wishes_str


class Errors(Exception):  # надо переделать
    pass


def get_ids():
    ids = select_call("SELECT id FROM users")
    return ids


class User:
    def __init__(self, id: int):
        self.ID = id

    def register(self, name, username):  # регистрация в базе данных
        id = self.ID
        if not registered(id):
            add_to_wishlist(id)
            add_to_wishlist(id, crossed=True)
            print(id, name)
            if username is not None:
                insert_call(f"INSERT INTO users (id, name, username) VALUES ({id}, '{name}', '@{username}')")
            else:
                insert_call(f"INSERT INTO users (id, name) VALUES ({id}, '{name}')")
            print('Успешная регистрация')
            return True
        else:
            print('не успешная регистрация')
            return False

    def get_key(self):
        return select_call(f"SELECT invite_key FROM users WHERE id = {self.ID};")[0][0]

    def get_link(self):
        link = select_call(f"SELECT invite_link FROM users WHERE id = {self.ID};")[0][0]
        if link is None:
            self.create_request_link()
            return None
        else:
            # return f"https://t.me/Lismus_bot?start={link}"
            return f"https://t.me/wishnya_wish_bot?start={link}"

    def create_request_link(self):
        try:
            if registered(self.ID):
                from model.crypt import Crypt
                result = Crypt(self.ID).encrypt()
                new_id = result[0]
                key = result[1]
                print(f'new_id: {str(new_id)}\n'
                      f'key: {str(key)}')
                update_call("UPDATE users SET invite_key = %s, invite_link = %s WHERE id = %s",
                            (str(key), str(new_id), self.ID))
                # insert_call(
                #     f"INSERT INTO users SET (invite_key, invite_link) VALUES ({str(key)}, {str(new_id)}) WHERE id = {self.ID}")
                # братья радченко скажите вы мне женат на подруге, а ходит ко мне
                return True
            else:
                raise 'userNotRegistered'
        except Errors as e:
            return e

    def unregister(self):
        if registered(self.ID):
            delete_call(f"DELETE FROM users WHERE id = {self.ID}")
            delete_call(f"DELETE FROM wishlist WHERE id = {self.ID}")
            # delete_call(f"DELETE FROM deleted_wishlist WHERE id = {self.ID}")
            return True
        else:
            print('ошибка в unregister. Человек уже не зарегистрирован')
            return False

    def get_info(self):
        if registered(self.ID):
            our_user = select_call(f"SELECT * FROM users WHERE id = {self.ID}")[0]
            user_info = {
                'id': our_user[0],
                'name': our_user[1],
                'username': our_user[3]
            }
            return user_info
        return None

    def get_name(self, info: any = None):
        try:
            if registered(self.ID):
                if info is None:
                    info = self.get_info()
                if info['username'] is not None:
                    name = f'"{info["username"]}" {info["name"]}'
                else:
                    name = info["name"]
                return name
            else:
                raise 'userNotRegistered'
        except Errors as e:
            return e

    def update_info(self, name: str = None, username: str = None):
        loc = locals()
        print(loc)
        """""""""link"""""""""""""""""
        old_key = self.get_key()
        self.create_request_link()
        while self.get_key() == old_key:
            self.create_request_link()
        """"""""""""""""""""""""""
        for key in loc.copy().keys():
            print(key)
            if loc.get(key) is None or key == 'self' or key == 'loc':
                loc.pop(key)
        if loc != {}:
            update_call(f"UPDATE users SET {f' = %s, '.join([i for i in loc.keys()])} = %s WHERE id = %s",
                        (*[i for i in loc.values()], self.ID))
            print('successfully updated')
            return True
        else:
            print('update failed')
            return False

    def subscribe(self, sub_id):
        try:
            if str(sub_id) == str(self.ID):
                raise Errors('subscribesHimself')
            subs_subscribes = User(self.ID).get_subscribes()
            if subs_subscribes == 'userNotRegistered':
                raise Errors(subs_subscribes)
            else:
                if subs_subscribes is not None:
                    if str(sub_id) not in subs_subscribes:
                        subs_subscribes.append(str(sub_id))
                        update_call("UPDATE users SET subscribes = %s WHERE id = %s",
                                    (';'.join(subs_subscribes), self.ID))
                        return True
                    else:
                        raise Errors('alreadySubscribed')
                else:
                    subscribes = [(str(sub_id))]
                    update_call("UPDATE users SET subscribes = %s WHERE id = %s", (';'.join(subscribes), self.ID))
                    return True
        except Errors as e:
            return e

    def unsubscribe(self, sub_id):
        try:
            subscribes = self.get_subscribes()
            if subscribes is not list and subscribes.__str__() == 'userNotRegistered':
                raise Errors(subscribes)
            else:
                if (subscribes is None) or (str(sub_id) not in subscribes):
                    print(subscribes,
                          sub_id)
                    print(type(subscribes),
                          type(sub_id))
                    raise Errors('alreadyNotInSubscribes')
                else:
                    subscribes.remove(str(sub_id))
                    update_call("UPDATE users SET subscribes = %s WHERE id = %s", (';'.join(subscribes), self.ID))
                    return True
        except Errors as e:
            return e

    def unsubscribe_all(self):
        try:
            subscribes = self.get_subscribes()
            if subscribes == 'userNotRegistered':
                raise Errors(subscribes)
            else:
                if subscribes is None:
                    raise Errors('subscribesAlreadyClean')
                else:
                    update_call("UPDATE users SET subscribes = %s WHERE id = %s", ('', self.ID))
                    return True
        except Errors as e:
            return e

    def delete_subscriber(self, sub_id):
        try:
            if registered(self.ID):
                subscribers = self.get_subscribers()
                print('->', subscribers)
                if (subscribers is None) or (str(sub_id) not in subscribers):
                    raise Errors('alreadyNotInSubscribers')
                else:
                    subscribers.remove(str(sub_id))
                    update_call("UPDATE users SET subscribes = %s WHERE id = %s", (';'.join(subscribers), self.ID))
                    return True
            else:
                raise Errors('userNotRegistered')
        except Errors as e:
            return e

    def deleteAll_subscribers(self):
        try:
            subscribers = self.get_subscribers()
            if subscribers == 'userNotRegistered':
                raise Errors(subscribers)
            else:
                if subscribers is None:
                    raise Errors('subscribersAlreadyClean')
                else:
                    update_call("UPDATE users SET subscribes = %s WHERE id = %s", ('', self.ID))
                    return True
        except Errors as e:
            return e

    def get_subscribes(self):
        try:
            if registered(self.ID):
                subscribes = select_call(f"SELECT subscribes FROM users WHERE id = {self.ID}")[0][0].split(';')
                print(subscribes)
                for sub in subscribes:
                    if sub == '':
                        subscribes.remove(sub)
                if len(subscribes) == 0:
                    return None
                return subscribes
            else:
                raise Errors('userNotRegistered')
        except Errors as e:
            return e

    def get_subscribers(self):
        try:
            if registered(self.ID):
                subscribers = select_call(f"SELECT id FROM users WHERE subscribes LIKE '%{self.ID}%';")
                if len(subscribers) == 0:
                    return None
                new_subs = [str(sub[0]) for sub in subscribers]
                return new_subs
            else:
                raise Errors('userNotRegistered')
        except Errors as e:
            return e

    def add_friend(self, friend_id):  # добавление в Отслеживаемые
        try:
            user_subscribers = self.get_subscribers()
            print(user_subscribers)
            friend = User(friend_id)
            friend_subscribes = friend.get_subscribes()
            print(friend_subscribes)
            if user_subscribers == 'userNotRegistered':
                return user_subscribers
            elif friend_subscribes == 'userNotRegistered':
                raise Errors('friendNotRegistered')
            elif str(friend_id) not in user_subscribers:
                raise Errors('friendNotInSubscribers')
            elif str(self.ID) not in friend_subscribes:
                print('?!?!??!', friend_subscribes)
                if str(friend_id) in user_subscribers:
                    self.delete_subscriber(friend_id)
                raise Errors('userNotInFriendSubscribers')
            elif str(self.ID) == str(friend_id):
                raise Errors('addingHimself')
            else:
                user_friend_list = self.get_friend_list()  # получение списка друзей
                print('Список друзей', user_friend_list)
                if str(friend_id) in user_friend_list:
                    raise Errors('alreadyInFriendList')  # уже есть в друзьях
                else:
                    user_friend_list.append(str(friend_id))
                    print('Список друзей после добавления', user_friend_list)
                    user_friend_string = ';'.join(user_friend_list)
                    print('Список друзей в виде строки', user_friend_string)
                    update_call(f"UPDATE users SET friend_list = %s WHERE id = %s", (user_friend_string, self.ID))
                    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    friendsFriendList = friend.get_friend_list()
                    if friendsFriendList is None:
                        friendsFriendList = [str(self.ID)]
                    else:
                        if str(self.ID) not in friendsFriendList:
                            friendsFriendList.append(str(self.ID))
                        else:
                            friend.unsubscribe(self.ID)
                            return True
                    friendsString = ';'.join(friendsFriendList)
                    update_call(f"UPDATE users SET friend_list = %s WHERE id = %s",
                                (friendsString, friend_id))
                    removed_from_subscribes = friend.unsubscribe(self.ID)
                    print(removed_from_subscribes, friend_subscribes)
                    return True
        except Errors as e:
            return e

    def delete_friend(self, friend_id):
        try:
            user_friend_list = self.get_friend_list()
            if user_friend_list == 'userNotRegistered':
                raise Errors(user_friend_list)
            else:
                if str(friend_id) not in user_friend_list:
                    raise Errors('alreadyNotInFriendList')
                else:
                    user_friend_list.remove(str(friend_id))
                    friend_list_str = ';'.join(user_friend_list)
                    update_call(f"UPDATE users SET friend_list = %s WHERE id = %s", (friend_list_str, self.ID))
                    """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                    friends_friend_list = User(friend_id).get_friend_list()
                    if str(friend_id) not in friends_friend_list:
                        raise Errors('alreadyNotInFriendsFriendList')
                    else:
                        friends_friend_list.remove(str(friend_id))
                        friend_list_str = ';'.join(friends_friend_list)
                        update_call(f"UPDATE users SET friend_list = %s WHERE id = %s", (friend_list_str, friend_id))
                    return True
        except Errors as e:
            return e

    def get_friend_list(self):
        try:
            if registered(self.ID):
                user_friend_list = select_call(f"SELECT friend_list FROM users WHERE id = {self.ID}")[0][0].split(
                    ';')  # получение списка друзей
                if '' in user_friend_list:
                    user_friend_list.remove('')
                return user_friend_list
            else:
                raise Errors('userNotRegistered')
        except Errors as e:
            return e

    def get_on_the_list(self):
        try:
            friends = select_call(f"SELECT id FROM users WHERE friend_list LIKE '%{self.ID}%'")
            return [str(friend[0]) for friend in friends]
        except Exception as e:
            print('ошибка при получении списка друзей, у которых ты в списке\n\n', e)
            return None

    def get_wishlist(self, crossed: bool = False, with_reserved: bool = False):
        if registered(self.ID):
            if not crossed:
                if in_the_wishlist(self.ID):
                    pass
                else:
                    add_to_wishlist(self.ID)
                sign = ';'
                user_wishlist = select_call(f"SELECT wishes FROM wishlist WHERE id = {self.ID}")[0][0].split(f'{sign}')
                if user_wishlist[0] == '':
                    print('Список пуст')
                    return -1
                else:
                    # user_wishlist = list(set(user_wishlist))
                    setted_user_wishlist = []
                    for wish in user_wishlist:
                        """"""""""""""""""""""""
                        if not with_reserved:
                            if '|||' in wish:
                                wish = wish.split('|||')[0]
                        """"""""""""""""""""""""
                        if wish not in setted_user_wishlist:
                            setted_user_wishlist.append(wish)
                    return setted_user_wishlist
            else:
                if in_the_wishlist(self.ID, crossed=True):
                    pass
                else:
                    add_to_wishlist(self.ID, crossed=True)
                sign = ';'
                user_wishlist = select_call(f"SELECT wishes FROM crossed_wishlist WHERE id = {self.ID}")[0][0].split(
                    f'{sign}')
                if user_wishlist[0] == '':
                    print('Список пуст')
                    return -1
                else:
                    return user_wishlist
        else:
            print('Ошибка в User.get_wishlist. Не зарегистрирован')
            return 0

    def get_wishlist_by_indexes(self, indexes: list, crossed: bool = False):
        if not crossed:
            user_wishlist = self.get_wishlist()
        else:
            user_wishlist = self.get_wishlist(crossed=True)
        if user_wishlist == -1:
            print('Список пуст')
            return -1
        else:
            wishes_with_indexes = []
            for index in indexes:
                wishes_with_indexes.append(user_wishlist[int(index)])
            print('get_wishlist_by_indexes.\ncurrent wishlist -> ', user_wishlist,
                  'indexes -> ', indexes,
                  'wishes_with_indexes -> ', wishes_with_indexes)
            return wishes_with_indexes

    def get_indexes_by_wishes(self, wishes: list):
        indexes = []
        current_wishes = self.get_wishlist()
        index = 0
        for wish in wishes:
            if wish in current_wishes:
                for cur in current_wishes:
                    if cur != wish:
                        index += 1
                    else:
                        indexes.append(indexes)
                        index = 0
                        break
        if indexes:
            return indexes
        else:
            return None

    def set_wishlist(self, new_wishlist: list, crossed: bool = False):
        if registered(self.ID):
            sign = ';'
            wishes_str = configure_list_to_str_wishes(new_wishlist)
            if not crossed:
                update_call(f"UPDATE wishlist SET wishes = %s WHERE id = %s", (f'{wishes_str}', self.ID))
            else:
                update_call(f"UPDATE crossed_wishlist SET wishes = %s WHERE id = %s", (f'{wishes_str}', self.ID))
            print('Успешно изменён список пожеланий')
            return 1
        else:
            print('Ошибка в User.set_wishlist. Не зарегистрирован')
            return 0

    def change_wish(self, index: int, edited_wish: str, crossed: bool = False):
        if not crossed:
            current_wishes = self.get_wishlist(with_reserved=True)
        else:
            current_wishes = self.get_wishlist(crossed=True)
        # убираем лишнее;
        print('edited wish before removing --> ', edited_wish)
        edited_wish = remove_forbidden_signs([edited_wish], {';': ',', '|||': ',,,'})[0]
        print('edited wish after removing --> ', edited_wish)
        wish = current_wishes[index]
        if '|||' in wish:
            # wish_text = wish.split('|||')[0]  # заменяем изначальное изменённым
            wish = f'{edited_wish}|||{wish.split("|||")[1]}'
        else:
            wish = edited_wish  # заменяем изначальное изменённым
        current_wishes[index] = wish
        if not crossed:
            had_set = self.set_wishlist(new_wishlist=current_wishes)
        else:
            had_set = self.set_wishlist(new_wishlist=current_wishes, crossed=True)
        if had_set:
            return 1
        else:
            return 0

    def unreserve_wish(self, index, reserver_id: int = None):
        try:
            wishes = self.get_wishlist(with_reserved=True)
            if wishes == -1:
                raise Errors('wishlist is empty')
            if index >= len(wishes):
                premium = Premium(self.ID)
                if premium.belong():
                    ind_wishes = premium.get_individual_wishlist(reserver_id, True)
                    if ind_wishes[0] is None:
                        raise Errors(f'individual wish with this index doesnt exist')
                    count = len(ind_wishes[0])
                    print(f'ind wishes count = {count}\ntotal count = {len(wishes) + count}')
                    if ind_wishes[1] == 'add':
                        if index >= (len(wishes) + count):
                            raise Errors('wrong index. ind')
                        index = index - len(wishes)
                        print(f'index changed = {index}')
                    else:
                        index = index - len(wishes)
                        print(f'index changed = {index}')
                        if index >= count:
                            raise Errors('wrong index. ind')
                    if '|||' not in ind_wishes[0][index]:
                        raise Errors(f'individual wish with this index is already unreserved')
                    else:
                        wishlist = ind_wishes[0]
                        wish = wishlist[index].split("|||")[0]
                        wishlist[index] = wish
                        premium.set_individual_wishlist(reserver_id, wishlist)
                        print('individual wish unreserved successfully')
                        return True
                else:
                    raise Errors('wrong index')
            if '|||' in wishes[int(index)]:
                wish = wishes[int(index)].split('|||')
                wish_text = wish[0]
                reserver_id_from_wish = wish[1]
                try:
                    if (reserver_id == int(reserver_id_from_wish)) or (reserver_id is None):
                        wishes[int(index)] = wish_text
                        self.set_wishlist(wishes)
                        return True
                    else:
                        raise Errors('not a reserver')
                except ValueError as e:
                    print(e)
                    raise Errors("reserver id is empty")
        except Errors as e:
            return e

    def reserve_wish(self, index, reserver_id: int):
        try:
            index = int(index)
            wishes = self.get_wishlist(with_reserved=True)
            print(f"index = {index}, wishes count = {len(wishes)}")
            if wishes == -1:
                raise Errors('wishlist is empty')
            if index >= len(wishes):
                premium = Premium(self.ID)
                if premium.belong():
                    ind_wishes = premium.get_individual_wishlist(reserver_id, True)
                    if ind_wishes[0] is None:
                        raise Errors(f'individual wish with this index doesnt exist')
                    count = len(ind_wishes[0])
                    print(f'ind wishes count = {count}\ntotal count = {len(wishes) + count}')
                    if ind_wishes[1] == 'add':
                        if index >= (len(wishes) + count):
                            raise Errors('wrong index of individual wish')
                        index = index - len(wishes)
                        print(f'index changed = {index}')
                    else:
                        index = index - len(wishes)
                        print(f'index changed = {index}')
                        if index >= count:
                            raise Errors('wrong index of individual wish')
                    if '|||' in ind_wishes[0][index]:
                        raise Errors(f'individual wish with this index is already reserved')
                    else:
                        wishlist = ind_wishes[0]
                        wish = f'{wishlist[index]}|||{str(reserver_id)}'
                        wishlist[index] = wish
                        premium.set_individual_wishlist(reserver_id, wishlist)
                        print('individual wish reserved successfully')
                        return True
                else:
                    raise Errors('wrong index')
            if index < 0:
                raise Errors('wrong index')
            if '|||' in wishes[index]:
                raise Errors('already reserved')
            reserved_wish = f'{wishes[index]}|||{str(reserver_id)}'
            wishes[index] = reserved_wish
            self.set_wishlist(wishes)
            return True
        except Errors as e:
            return e

    def get_total_count_reserved_wishes(self, reserver_id: int = None):
        wishes = self.get_wishlist(with_reserved=True)
        count = 0
        for wish in wishes:
            if '|||' in wish:
                if reserver_id is not None:
                    print(reserver_id)
                    current_id = int(wish.split('|||')[1])
                    if reserver_id == current_id:
                        count += 1
                else:
                    count += 1
        if reserver_id is not None and Premium(self.ID).belong():
            Premium(self.ID).get_individual_wishlist(friend_id=reserver_id, with_reserved=True)
            for wish in wishes:
                if '|||' in wish:
                    count += 1
        return count

    def get_reserved_wishes(self, reserver_id: int = None):
        # reservations = {554361: {'indexes': [1]}}
        reservations = {}
        if Premium(self.ID).belong() and reserver_id is not None:
            wishes = Premium(self.ID).get_total_wishlist(friend_id=reserver_id, with_reserved=True)
        else:
            wishes = self.get_wishlist(with_reserved=True)
        index = 0
        for wish in wishes:
            if '|||' in wish:
                if reserver_id is not None:
                    # print(reserver_id)
                    current_id = int(wish.split('|||')[1])
                    if reserver_id == current_id:
                        if reserver_id not in reservations.keys():
                            reservations[reserver_id] = {"indexes": [index]}
                        else:
                            reservations[reserver_id] = {"indexes": reservations[reserver_id]['indexes'] + [index]}
                else:
                    current_id = int(wish.split('|||')[1])
                    if current_id not in reservations.keys():
                        current_indexes = []
                    else:
                        current_indexes = reservations[current_id]['indexes']
                    reservations[current_id] = {"indexes": current_indexes + [index]}
            index += 1
        if len(reservations) == 0:
            return None
        return reservations

    def change_wishes(self, indexes: list, list_of_edited_wishes: list, crossed: bool = False):
        if not crossed:
            current_wishes = self.get_wishlist(with_reserved=True)
        else:
            current_wishes = self.get_wishlist(crossed=True)
        # убираем лишнее;
        list_of_edited_wishes = remove_forbidden_signs(list_of_edited_wishes, {';': ',', "|||": ','})
        for index in range(len(indexes)):
            wish = current_wishes[int(indexes[index])]
            if '|||' in wish:
                wish_text = list_of_edited_wishes[index]  # заменяем изначальное изменённым
                wish = f'{wish_text}|||{wish.split("|||")[1]}'
                current_wishes[index] = wish
            else:
                current_wishes[index] = list_of_edited_wishes[index]  # заменяем изначальное изменённым
        if not crossed:
            had_set = self.set_wishlist(new_wishlist=current_wishes)
        else:
            had_set = self.set_wishlist(new_wishlist=current_wishes, crossed=True)
        if had_set:
            return 1
        else:
            return 0

    def add_wishes(self, wishes: list, crossed: bool = False):
        if not crossed:
            current_wishlist = self.get_wishlist()
        else:
            current_wishlist = self.get_wishlist(crossed=True)
        if current_wishlist != -1:
            print(wishes)
            print(current_wishlist, wishes)
            wishlist = []
            for wish in [i for i in current_wishlist]:
                wishlist.append(change_to_upper(wish))
            for wish in [i for i in wishes]:
                wish = remove_forbidden_signs([wish], {';': ',', "|||": ','})[0]
                # if any(i in wish for i in [';', '|||']):
                #     for forbidden in [';', '|||']:
                #         wish = wish.replace(forbidden, ',')
                #     print('replaced ; or ||| from wish -> ', wish)
                if wish.lower() in [ww.lower() for ww in wishlist]:
                    print('copy wish detected. passed')
                    pass
                else:
                    wishlist.append(change_to_upper(wish))
            if not crossed:
                setted = self.set_wishlist(wishlist)
            else:
                setted = self.set_wishlist(wishlist, crossed=True)
            if setted:
                print('Успешно добавил')
                return 1
            else:
                print('ошибка в add_wishes')
                return 0
        else:
            print(wishes)
            wishlist = []
            copy = 0
            for wish in wishes:
                print('wish -> ', wish)
                wish = remove_forbidden_signs([wish], {';': ',', "|||": ','})[0]
                # if any(i in wish for i in [';', '|||']):
                #     for forbidden in [';', '|||']:
                #         wish = wish.replace(forbidden, ',')
                #     print('replaced ; or ||| from wish -> ', wish)
                if wish.lower() not in [i.lower() for i in wishlist]:
                    wishlist.append(change_to_upper(wish))
                else:
                    print('caught a copy wish. passed')
                    copy += 1
            print('copy wishes = ', copy, '(if zero -> good)')
            if not crossed:
                had_set = self.set_wishlist(wishlist)
            else:
                had_set = self.set_wishlist(wishlist, crossed=True)
            if had_set:
                print('Успешно добавил')
                return 1
            else:
                print('ошибка в add_wishes')
                return 0

    def delete_wishlist(self, wishes_to_delete: list, crossed: bool = False):
        if not crossed:
            wishlist = self.get_wishlist()
        else:
            wishlist = self.get_wishlist(crossed=True)
        print('current wishlist -> ', wishlist)
        print('wishes to delete -> ', wishes_to_delete)
        # wishes_to_delete = set(wishes_to_delete)
        new_wishes_to_delete = []
        for ww in wishes_to_delete:
            if ww not in new_wishes_to_delete:
                new_wishes_to_delete.append(ww)
        print('wishes to delete after setting -> ', wishes_to_delete)
        for wish in new_wishes_to_delete:
            print('wish -> ', wish)
            print(f'|{wish}|')
            if wish in wishlist:
                wishlist.remove(wish)
            else:
                print('caught an error. wish is not in wishlist')
        if not crossed:
            setting_wishlist = self.set_wishlist(wishlist)
        else:
            setting_wishlist = self.set_wishlist(wishlist, crossed=True)
        if setting_wishlist:
            print('Пункты были удалены')
            return 1
        else:
            print('Пункты не были удалены. Ошибка в delete_wishlist')
            return 0

    def delete_all_wishes(self, crossed: bool = False):
        if not crossed:
            update_call(f"UPDATE wishlist SET wishes = %s WHERE id = %s", ('', self.ID))
        else:
            update_call(f"UPDATE crossed_wishlist SET wishes = %s WHERE id = %s", ('', self.ID))
        print('Успешно очищен весь список')
        return 1

    def count_of_wishes(self, crossed: bool = False, total: bool = False):
        if not crossed:
            return len(self.get_wishlist())
        else:
            return len(self.get_wishlist(True))

# -----------------------------

def numbers_to_indexes(numbers: list):
    indexes = []
    for number in numbers:
        indexes.append(int(number) - 1)
    return indexes


def change_to_upper(string: str):
    return f'{string[:1:].upper()}{string[1::]}'


def get_str_numbers(numbers: list, length_of_wishes: int):
    try:  # проверка на то, что пользователь отправил число
        for number in numbers:  # проверка на то, верные ли номера указал пользователь
            if int(number) - 1 not in [i for i in range(length_of_wishes)]:
                print('Неверный номер')
                return 0
        else:  # если всё верно
            print(numbers)
            str_numbers = ', '.join([str(i) for i in numbers])  # строим строку с номерами пунктов (не индексами)
            return str_numbers
    except ValueError as e:  # если не число, сообщаем ему об этом
        print(e, 'Кажется, это не число')
        return -1


def sorted_wishlist(wishlist: list, sign='—', reserver_id: int = None):
    wishes = ''
    print(wishlist)
    if wishlist == '':
        pass
    print(wishlist)
    if len(wishlist) != 0:
        if sign == str:
            for wish in wishlist:
                wish = f'{change_to_upper(wish)}'
                if '|||' in wish:
                    if int(wish.split("|||")[1]) == reserver_id:
                        wish = f'🤙 {wish.split("|||")[0]}'
                    else:
                        wish = f'🤌 {wish.split("|||")[0]}'
                wishes += f'{sign} {wish}\n'
            return wishes[:-1:]
        else:
            wishes = ''  # будущее сообщение со списком
            for i in range(len(wishlist)):  # длина списка пожеланий
                wish = change_to_upper(wishlist[i])  # каждому желанию делаем большую букву
                if '|||' in wish:
                    if int(wish.split("|||")[1]) == reserver_id:
                        wish = f'🤙 {wish.split("|||")[0]}'
                    else:
                        wish = f'🤌 {wish.split("|||")[0]}'
                wishes += f'{i + 1}. {wish}\n'  # постепенно строим наше будущее сообщение
            return wishes[:-1:]


def choose(message: str):
    numbers_to_return = []
    ints = [str(i) for i in range(0, 10)]
    number = ''
    print(ints)
    if len(message) != 0:
        for i in range(len(message)):
            if message[i] in ints:
                number += message[i]
            else:
                if number != '':
                    numbers_to_return.append(int(number))
                number = ''
        if number.isdigit():
            numbers_to_return.append(int(number))
        return numbers_to_return
    else:
        return 0


class Premium:

    def __init__(self, id: int):
        self.ID = id

    def belong(self):
        if select_call(f"SELECT * FROM premium WHERE id = {self.ID}"):
            return True
        else:
            return False

    def lost_premium(self):
        if self.belong():
            delete_call("DELETE FROM premium WHERE id={}".format(self.ID))
            from bot.main import lost_premium
            lost_premium(self.ID)
            return True
        else:
            return False

    def get_premium(self, product_name: str):
        if self.belong():
            print('already belong')
            return False
        else:
            print('getting premium')
            leaving_date = {'Ежемесячная подписка': (datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d') + datetime.timedelta(days=30)).date(),
                            'Годовая подписка': (datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d') + datetime.timedelta(days=365)).date(),
                            'Пожизненный доступ': None}
            for key in leaving_date.keys():
                if product_name == key:
                    print(key, str(leaving_date[key]))
                    if key != 'Пожизненный доступ':
                        insert_call(
                            f"INSERT INTO premium (id, leaving_date) VALUES ({self.ID}, '{str(leaving_date[key])}')")
                        break
                    else:
                        insert_call(
                            f"INSERT INTO premium (id) VALUES ({self.ID})")
                        break
            else:
                print('some troubles with getting premium. wrong product_name')
                return False
            print('got premium')
            return True

    def get_views(self):
        try:
            viewers = select_call(f"SELECT viewers FROM premium WHERE id={self.ID}")[0][0].split(
                ';')  # получение списка друзей
            if '' in viewers:
                viewers.remove('')
            return viewers
        except Exception as e:
            print(e)
            return None

    def make_view(self, viewer_id: int):
        if self.belong():
            if viewer_id in [int(view) for view in self.get_views()]:
                print('you already checked this user. passed')
                return False
            else:
                print('making a view')
                views = self.get_views()
                views.append(viewer_id)
                print(views)
                views_str = ';'.join([str(view) for view in views])
                update_call(f"UPDATE premium SET viewers = %s WHERE id = %s", (views_str, self.ID))
                return True
        else:
            print('not in premium')
            return False

    def get_total_wishlist(self, friend_id, with_reserved: bool = False):
        if self.belong():
            db_call = self.get_individual_wishlist(friend_id, with_reserved=with_reserved)
            ind_wishlist = db_call[0]
            mode = db_call[1]
            # print('ind_wishlist = ', ind_wishlist)
            wsh = User(self.ID).get_wishlist(with_reserved=with_reserved)
            if ind_wishlist is not None:
                if mode == 'add':
                    if wsh == -1:
                        wsh = []
                    return wsh + ind_wishlist
                else:
                    return ind_wishlist
            else:
                if mode == 'add':
                    return User(self.ID).get_wishlist(with_reserved=with_reserved)
                else:
                    return -1
        else:
            print('not registered')
            return False

    # def get_total_count_reserved_wishes(self, reserver_id: int = None):

    def get_indexes_reserved_individual_wishes(self, reserver_id: int = None):
        reservations = {}
        wishes = self.get_individual_wishlist(friend_id=reserver_id, with_reserved=True)
        print(f'wishes = {wishes}')
        if wishes[0] is None:
            return wishes
        index = User(self.ID).count_of_wishes()
        for wish in wishes[0]:
            if '|||' in wish:
                if reserver_id is not None:
                    print(reserver_id)
                    current_id = int(wish.split('|||')[1])
                    if reserver_id == current_id:
                        if reserver_id not in reservations.keys():
                            reservations[reserver_id] = {"indexes": [index]}
                        else:
                            reservations[reserver_id] = {"indexes": reservations[reserver_id]['indexes'] + [index]}
                else:
                    current_id = int(wish.split('|||')[1])
                    if current_id not in reservations.keys():
                        current_indexes = []
                    else:
                        current_indexes = reservations[current_id]['indexes']
                    reservations[current_id] = {"indexes": current_indexes + [index]}
            index += 1
        if len(reservations) == 0:
            return None
        return reservations

    def get_individual_wishlist(self, friend_id: int, with_reserved: bool = False):
        call = select_call(
            f"select * from premium_individual_wishlists WHERE id = {self.ID} AND friend_id = {friend_id};")
        # print(call)
        if len(call) == 0:
            insert_call(
                f"INSERT INTO premium_individual_wishlists (id, friend_id, wishes) VALUES ({self.ID}, {friend_id}, '');")
            call = select_call(
                f"select * from premium_individual_wishlists WHERE id = {self.ID} AND friend_id = {friend_id};")[0]
        else:
            call = call[0]
        # print(call)
        mode = call['mode']
        """"""""""""""""""""""""
        wishlist = call["wishes"]
        """"""""""""""""""""""""
        if wishlist == '':
            return None, mode
        # """"""""""""""""""""""""
        if with_reserved:
            return wishlist.split(';'), mode
        # """"""""""""""""""""""""
        else:
            wishlist = wishlist.split(';')
            for i in range(len(wishlist)):
                if '|||' in wishlist[i]:
                    wishlist[i] = wishlist[i].split('|||')[0]
            return wishlist, mode

    def get_individual_wishlist_by_indexes(self, indexes: list, friend_id):
        user_wishlist = self.get_individual_wishlist(friend_id=friend_id)[0]
        if user_wishlist is None:
            print('Список пуст')
            return -1
        else:
            wishes_with_indexes = []
            for index in indexes:
                wishes_with_indexes.append(user_wishlist[int(index)])
            print('get_individual_wishlist_by_indexes.\ncurrent wishlist -> ', user_wishlist,
                  'indexes -> ', indexes,
                  'wishes_with_indexes -> ', wishes_with_indexes)
            return wishes_with_indexes

    def count_of_individualWishes(self, friend_id):
        wishlist = self.get_individual_wishlist(friend_id)[0]
        if wishlist is None:
            return 0
        return len(wishlist)

    def change_mode(self, friend_id):
        if self.belong():
            if self.get_individual_wishlist(friend_id)[1] == 'add':
                mode = 'overwrite'
            else:
                mode = 'add'
            update_call(f"UPDATE premium_individual_wishlists SET mode = %s WHERE id = %s AND friend_id = %s;",
                        (mode, self.ID, friend_id))
            return True
        else:
            print('не зарегистрирован')
            return False

    def set_individual_wishlist(self, friend_id: int, wishes: list):
        if self.belong():
            wishes_str = configure_list_to_str_wishes(wishes)
            print(wishes_str)
            self.get_individual_wishlist(friend_id)
            update_call(f"UPDATE premium_individual_wishlists SET wishes = %s WHERE id = %s AND friend_id = %s",
                        (f'{wishes_str}', self.ID, friend_id))
            print('Успешно изменён список пожеланий')
            return True
        else:
            print('Ошибка в premium.set_individual_wishlist. нет доступа')
            return False

    def add_individual_wishes(self, friend_id, wishes):
        current_wishlist = self.get_individual_wishlist(friend_id=friend_id)[0]
        if current_wishlist is not None:
            print(wishes)
            print(current_wishlist, wishes)
            wishlist = []
            for wish in [i for i in current_wishlist]:
                wishlist.append(change_to_upper(wish))
            for wish in wishes:
                if any(i in wish for i in [';', '|||']):
                    for forbidden in [';', '|||']:
                        wish = wish.replace(forbidden, ',')
                    print('replaced ; or from wish -> ', wish)
                if wish.lower() in [ww.lower() for ww in wishlist]:
                    print('copy wish detected. passed')
                    pass
                else:
                    wishlist.append(change_to_upper(wish))
            setted = self.set_individual_wishlist(friend_id=friend_id,
                                                  wishes=wishlist)
            if setted:
                print('Успешно добавил')
                return 1
            else:
                print('ошибка в add_wishes')
                return 0
        else:
            print(wishes)
            wishlist = []
            copy = 0
            for wish in wishes:
                print('wish -> ', wish)
                if any(i in wish for i in [';', '|||']):
                    for forbidden in [';', '|||']:
                        wish = wish.replace(forbidden, ',')
                    print('replaced ; from wish -> ', wish)
                if wish.lower() not in [i.lower() for i in wishlist]:
                    wishlist.append(change_to_upper(wish))
                else:
                    print('caught a copy wish. passed')
                    copy += 1
            print('copy wishes = ', copy, '(if zero -> good)')
            setted = self.set_individual_wishlist(friend_id=friend_id,
                                                  wishes=wishlist)
            if setted:
                print('Успешно добавил')
                return 1
            else:
                print('ошибка в add_wishes')
                return 0

    def delete_individual_wishes(self, friend_id, wishes_to_delete: list):
        wishlist = self.get_individual_wishlist(friend_id)[0]
        if wishlist is None:
            print('Список пуст')
            return 0
        print('current wishlist -> ', wishlist)
        print('wishes to delete -> ', wishes_to_delete)
        # wishes_to_delete = set(wishes_to_delete)
        new_wishes_to_delete = []
        for ww in wishes_to_delete:
            if ww not in new_wishes_to_delete:
                new_wishes_to_delete.append(ww)
        print('wishes to delete after setting -> ', wishes_to_delete)
        for wish in new_wishes_to_delete:
            print('wish -> ', wish)
            print(f'|{wish}|')
            if wish in wishlist:
                wishlist.remove(wish)
            else:
                print('caught an error. wish is not in wishlist')
        setting_wishlist = self.set_individual_wishlist(friend_id, wishlist)
        if setting_wishlist:
            print('Пункты были удалены')
            return 1
        else:
            print('Пункты не были удалены. Ошибка в delete_wishlist')
            return 0


def ins(id, payment_id, product_name, date, status, idempotence_key, message_id: int):
    print(select_call("SELECT * FROM pending_payments"))
    insert_call(f"INSERT INTO pending_payments (id, payment_id, product_name, date, status, idempotence_key, "
                f"message_id) VALUES ({id}, '{payment_id}', '{product_name}', '{date}', '"
                f"{status}', '{idempotence_key}', {message_id})")
    print(select_call("SELECT * FROM pending_payments"))


def select_pending_payments():
    return select_call("SELECT * FROM pending_payments;")


def delete_pending_payments(chat_id, idempotence_key, message_id):
    delete_call(f"DELETE FROM pending_payments WHERE idempotence_key='{idempotence_key}'")


def succeeded_payment(id, payment_id, product_name, date, status, idempotence_key, message_id):
    premium = Premium(id)
    if premium.get_premium(product_name):
        insert_call(f"INSERT INTO succeeded_payments (id, payment_id, product_name, date, status, idempotence_key)"
                    f"VALUES ({id}, '{payment_id}', '{product_name}', '{date}', '"
                    f"{status}', '{idempotence_key}')")
        from bot.main import got_premium
        got_premium(chat_id=id,
                    product_name=product_name,
                    message_id=message_id)
    else:
        from listeners.notifications import show_notification
        show_notification(f'Проблема с получением премиум.\n'
                          f'({id}, {payment_id}, {product_name}, {date}, '
                          f'{status}, {idempotence_key}')


if __name__ == '__main__':
    #     import inspect
    User(277820721).get_key()
#     print(User(1).test())
#     print(type(User(1).test()))
#     print(inspect.isclass(User(1).test()))
#     print(inspect.)
# print(User(5521444521).subscribe(277820721))
# print(User(5521444521).delete_subscriber(277820721))
# print(User(277820721).unsubscribe(971386105))
