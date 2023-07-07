class Crypt:
    def __init__(self, user_id):
        self.USER_ID = user_id

    def encrypt(self):
        import random
        key = random.randint(0, 10000)
        result = ""
        for i in range(len(str(self.USER_ID))):
            char = str(self.USER_ID)[i]
            if char.isupper():
                result += chr((ord(char) + key - 64) % 26 + 65)
            else:
                result += chr((ord(char) + key - 96) % 26 + 97)
        return [result, key]

    def decrypt(self, key: int):
        result = ""
        for i in range(len(str(self.USER_ID))):
            char = str(self.USER_ID)[i]
            if char.isupper():
                result += chr(((ord(char) + 26 - key - 64) % 26 + 65) - 54)
            else:
                result += chr(((ord(char) + 26 - key - 96) % 26 + 97) - 54)
        return result
