# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import pyotp
import datetime
import logging
import bcrypt


class DoormaticMongoAuth:
    client = None
    server_address = "localhost"
    server_database = "admin"
    server_port = 27017
    db = None
    posts = None
    salt = int(12)

    def __init__(self,  hostname="localhost", port=27017, database="admin", salt=None):
        self.server_address = hostname
        self.server_port = port
        self.server_database = database
        self.client = MongoClient(self.server_address, self.server_port)
        self.db = self.client[self.server_database]
        self.posts = self.db.posts
        if salt:
            self.salt = int(salt)

    def _get_user(self, user, search_by="chat_id"):
        if search_by is "id":
            search_match = {"user_id": user}
        elif search_by is "username":
            search_match = {"username": user}
        elif search_by is "chat_id":
            search_match = {"chat_id": user}
            logging.info("get_user: search_match: {}".format(search_match))
        else:
            return False

        user_data = None
        try:
            user_data = self.posts.find_one(search_match)
        except ServerSelectionTimeoutError:
            logging.error("Connection timeout to: {}:{}".format(self.server_address, self.server_port))
        finally:
            if user_data:
                return user_data

        return None

    def validate_user(self, user, password, search_by="chat_id"):
        user_data = self._get_user(user, search_by)
        if user_data and password:
            if "password" in user_data:
                password = password.encode("utf-8")
                if bcrypt.hashpw(
                        password,
                        user_data['password'],
                ) == user_data['password']:
                    return True
                else:
                    print("got\t\t {}\nexpected\t {}".format(bcrypt.hashpw(password,user_data['password']), user_data['password']) )
        return False

    def get_user_totp(self, user, search_by="chat_id"):
        current_token = None
        user_data = self._get_user(user, search_by)
        if user_data:
            if "totp_key" in user_data:
                try:
                    totp = pyotp.TOTP(user_data['totp_key'])
                    current_token = totp.now()
                finally:
                    if current_token:
                        return int(current_token)

        return None

    def validate_user_totp(self, user, totp, search_by="chat_id"):
        current_token = self.get_user_totp(user,search_by)
        if current_token:
            if current_token == totp:
                return True
        return False

    def user_exists(self, user, search_by="chat_id"):
        existent = self._get_user(user, search_by)
        if existent:
            return True
        return False

    # TODO: Create user deletion
    def delete_user(self, user, search_by="chat_id"):
        pass

    def set_password(self, user, new_password, search_by="chat_id"):
        if not new_password:
            logging.error("Empty password requested for update")
            return False
        new_password = new_password.encode("utf-8")
        users_new_password = bcrypt.hashpw(new_password, bcrypt.gensalt(self.salt))
        if self._update_user(user, update_key="password", update_value=users_new_password):
            return True
        return False

    # Mind what you update...
    def _update_user(self, user, update_key, update_value, search_by="chat_id"):
        selected_user = self._get_user(user, search_by)
        if selected_user:
            if self.posts.update_one(
                    {"_id": selected_user['_id']},
                    {"$set": {update_key: update_value}},
                    upsert=False,):
                return True
        return False

    def add_user(self, chat_id, username, name, totp_key, phone):
        if self.user_exists(chat_id):
            logging.info("Tried to create existing user {}".format(chat_id))
            return False

        new_user = {
            "chat_id": chat_id,
            "phone": phone,
            "name": name,
            "username": username,
            "totp_key": totp_key,
        }
        return self._add_entry(new_user)

    def _add_entry(self, entry):
        post_id = None
        try:
            post_id = self.posts.insert_one(entry).inserted_id
            if post_id:
                logging.debug("Added new entry: {}".format(post_id))
        except ServerSelectionTimeoutError:
            logging.error("Connection timeout to: {}:{}".format(self.server_address, self.server_port))
        finally:
            if post_id:
                return True

        return False


if __name__ == '__main__':
    print("Please, import me :)")
