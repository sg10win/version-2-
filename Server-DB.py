import socket
import sqlite3
import select
import datetime
import random
import time

import sqlite_utils
from cryptography.fernet import Fernet
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError

class Client(object):
    def __init__(self, username, socket, key):
        self._username = username
        self._socket = socket
        self._key = key

    # def send(self, message):
    #     self._socket.send(message.encode('utf-8'))
    #
    # def recv(self):
    #     return self._socket.recv(1024).decode('utf-8')

    def get_username(self):
        return self._username

    def set_username(self, username):
        self._username = username

    def is_username(self, username):
        return self._username == username

    def get_socket(self):
        return self._socket

    def get_key(self):
        return self._key

class ListClients(object):
    def __init__(self):
        self._clients = []

    def add_client(self, username, socket, key):
        self._clients.append(Client(username, socket, key))

    def get_sockets(self):
        sockets = []
        for client in self._clients:
            sockets.append(client.get_socket())
        return sockets

    def get_usernames(self):
        usernames = []
        for client in self._clients:
            usernames.append(client.get_username())
        return usernames

    def get_socket(self, username):
        for client in self._clients:
            if client.get_username() == username:
                return client.get_socket()
        raise Exception("username not found in client list")
        # return None

    def get_username(self, socket):
        for client in self._clients:
            if client.get_socket() == socket:
                return client.get_username()
        raise Exception("socket not found in client list")

    def _get_client_by_username(self, username):
        for client in self._clients:
            if client.get_username() == username:
                return client
        raise Exception("username not found in client list to return client")

    def _get_client_by_socket(self, socket):
        return self._get_client_by_username(self.get_username(socket))

    def set_username(self, socket, username):
        self._get_client_by_socket(socket).set_username(username)

    def remove_client(self, username):
        for client in self._clients:
            if client.get_username() == username:
                self._clients.remove(client)
                client.get_socket().close()
                # client = None
                return
        raise Exception('There was no client with the username: ', username)
        # new_client_list = []
        # for client in self._clients:
        #     if not client.get_username() == None:
        #         new_client_list.append(client)
        # self._clients = new_client_list
    def get_key_by_socket(self, socket):
        for client in self._clients:
            if client.get_socket() == socket:
                return client.get_key()
        raise Exception("socket not found in client list")
# you need to remember to colse the database connection
class Server(object):
    def __init__(self):
        self.ip = "0.0.0.0"
        self.port = 8080
        self.server_socket = socket.socket()
        self.server_socket.bind((self.ip, self.port))
        self.server_socket.listen(5)
        self.db = Database(sqlite3.connect("users_01.db"))
        print("opened database successfully")
        self.database_reset_temp()  # resets DB
        self.messages = []
        self.last_id = 1

        self.clients = ListClients()

    def database_reset_temp(self):
        try:
            #self.conn.execute('''DROP TABLE CHATS;''')

            self.db["chats"].drop()
        except:
            print("there is no table CHATS")
        try:
            #self.conn.execute('''DROP TABLE USERS;''')
            self.db["users"].drop()
        except:
            print("there is no table USERS")
        # self.conn.execute('''CREATE TABLE USERS
        # (
        # id                  INTEGER     PRIMARY KEY,
        # email               TEXT        NOT NULL,
        # username            TEXT        NOT NULL,
        # hashed_password     TEXT        NOT NULL);''')

        self.db['users'].create({
            "id": int,
            "email": str,
            "username": str,
            "hashed_password":str,
            },pk="id")
        print("table created successfully")
        users = self.db["users"]
        users.insert({"username": "segev10",
                      "id" : 1,
                      "email": "segevshalom86@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        users.insert({"username": "a",
                      "id": 2,
                      "email": "a@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        users.insert({"username": "b",
                      "id": 3,
                      "email": "b6@gmail.com",
                      "hashed_password": '0cc175b9c0f1b6a831c399e269772661'},
                     pk="id")
        print(users.get(1))
        print(users.get(2))
        print(users.get(3))
        # self.conn.execute(
        #     '''INSERT INTO USERS (email, username, hashed_password) VALUES('segevshalom86@gmail.com','segev10','0cc175b9c0f1b6a831c399e269772661');''')
        # self.conn.execute(
        #     '''INSERT INTO USERS (email, username, hashed_password) VALUES('a@gmail.com','a','0cc175b9c0f1b6a831c399e269772661');''')
        # self.conn.execute(
        #     '''INSERT INTO USERS (email, username, hashed_password) VALUES('b@gmail.com','b','0cc175b9c0f1b6a831c399e269772661');''')
        # self.conn.execute('''CREATE TABLE CHATS
        #         (
        #         id                  INTEGER     PRIMARY KEY,
        #         name                TEXT        NOT NULL,
        #         contacts            TEXT        NOT NULL,
        #         msgs                TEXT        NOT NULL,
        #         user_id             INTEGER        NOT NULL,
        #         external_id         INTEGER     NOT NULL,
        #         FOREIGN KEY(user_id)  REFERENCES  USERS(id));''')
        self.db["chats"].create({
            "id": int,
            "name": str,
            "contacts": str,
            "msgs": str,
            "user_id": int,
            "external_id": int,
            "new_msgs": int},
            pk="id"
            )
        # self.conn.close

    def msg_maker(self, data, list_of_sockets_to_send):  # the type is 's'-signup, 'l'-login, 'm'-msg, **'f'-file**
        #print(data)
        msg = data, list_of_sockets_to_send
        self.messages.append(msg)


    def get_list_of_contacts(self, external_id):
        i = 1
        contacts = None
        while True:
            try:
                chat = self.db["chats"].get(i)
                temp_external_id = chat["external_id"]
                if str(temp_external_id) == str(external_id) :
                    contacts = chat["contacts"]
                    break
                i +=1
            except NotFoundError:
                 break

        list_of_contacts = contacts.split(",")
        return list_of_contacts

        # this method adds a msg to send about whats wrong with the params if it is and return true if the process done and false if not
    def save_new_user_to_database(self, socket, email, username, hashed_password):
        cursor1 = []
        cursor2 = []
        for row in self.db["users"].rows_where("username = ?", [username]):
            cursor1.append(row)
        for row in self.db["users"].rows_where("email = ?", [email]):
            cursor2.append(row)
        #cursor = self.conn.execute('''SELECT email,username FROM USERS;''')
        list = []
        list.append(socket)

        if cursor1 and cursor2:
            self.msg_maker("This email and username are\n currently in use", list)
            return False
        elif cursor2:
            self.msg_maker("This email is currently in use", list)
            return False
        elif cursor1:
            self.msg_maker("This username is currently in use", list)
            return False

        #email = "'" + email + "'"
        #username = "'" + username + "'"
        #hashed_password = "'" + hashed_password + "'"
        #self.conn.execute(
        #    "INSERT INTO USERS (email, username, hashed_password) VALUES (" + email + ',' + username + ',' + hashed_password + ");")
        self.db["users"].insert({"email": email, "username":username, "hashed_password": hashed_password}, pk='id')
        #cursor = self.conn.execute('''SELECT email,username,hashed_password FROM USERS;''')
        self.msg_maker("signed in successfully", list)
        return True

    def get_column_from_db(self, column, table):
        list = []
        i = 1
        while True:
            try:
                dict = table.get(i)[column]
                list.append(dict)
                i = i+1
            except NotFoundError:
                return list

    def shared_list(self, list1, list2):
        list3 = []
        for i in list1:
            if i in list2 and i not in list3:
                list3.append(i)
        return list3

    def convert_list_str(self, list):

        return "".join(list)


    def create_new_chat(self, chat_name, contacts):

        new_chat_msg = 'IChat Server: you were added to this chat'
        # list of right contacts only
        all_usernames = self.get_column_from_db("username",self.db["users"])#list of all the usernames in the db
        usernames = self.shared_list(all_usernames, contacts)#list of the usernames we need to make a chat for them
        contacts = ','.join(usernames)
        random_external_id = random.randint(1, 10000)
        while random_external_id in self.get_column_from_db("external_id", self.db["chats"]):
            random_external_id = random.randint(1, 10000)
        user_ids = self.get_column_from_db("id", self.db["users"])
        #print(user_ids)
        for user_id in user_ids:
            print(f"user_id={user_id}")
            username = self.db["users"].get(user_id)["username"]
            if username in usernames:
                self.db["chats"].insert({"id": self.last_id, "name": chat_name, "msgs": new_chat_msg, "contacts": contacts
                                            , "user_id": user_id, "external_id": random_external_id, "new_msgs": 1})
                print(f"created this chat now=>{self.db['chats'].get(self.last_id)}")
                if username in self.clients.get_usernames():
                    list_client = [self.clients.get_socket(username)]
                    self.msg_maker("new chat%%%" + str(self.last_id) + "%%%" + str(random_external_id) + "%%%" + chat_name + "%%%" + contacts + "%%%" + "1", list_client)
                    #print("sent after it=>"+"new chat%%%" + str(self.last_id) + "%%%" + str(random_external_id) + "%%%" + chat_name + "%%%" + contacts + "%%%" + new_chat_msg)
                self.last_id = self.last_id + 1


    def print_table (self, table ):
        for i in self.get_column_from_db("id", table):
            print(table.get(i))



    def save_msg_in_db1 (self,msg):
        self.print_table(self.db["chats"])
        msg = msg.split("%%%")
        username = msg[1]
        sender_chat_id = msg[2]
        external_id = msg[3]
        msg = msg[4]
        for chat_id in self.get_column_from_db("id",self.db["chats"]):
            if self.db["chats"].get(chat_id)["external_id"] == int(external_id):
                print("in if 1")
                if str(chat_id) != sender_chat_id:
                    print("in if 2")
                    previous_msgs = self.db["chats"].get(chat_id)["msgs"]
                    msgs = f"{previous_msgs}\n{username}: {msg}"
                    self.db["chats"].update(chat_id, {"msgs": msgs})
                    username_that_want_the_msg = self.db["users"].get(self.db["chats"].get(chat_id)["user_id"])["username"]
                    if username_that_want_the_msg not in self.clients.get_usernames(): # the client isn't online
                        new_msgs = self.db["chats"].get(chat_id)["new_msgs"]
                        self.db["chats"].update(chat_id, {"new_msgs": new_msgs+1})
                        print(f"did it and new_msgs = {self.db['chats'].get(chat_id)['new_msgs']}")
                else:
                    print("in else")
                    previous_msgs = self.db["chats"].get(chat_id)["msgs"]
                    msgs = f"{previous_msgs}\nYou: {msg}"
                    self.db["chats"].update(chat_id, {"msgs": msgs})
                #print(f"updated = {self.db['chats'].get(chat_id)}")



    def run(self):
        print("server started")
        while True:
            rlist, wlist, xlist = select.select([self.server_socket] + self.clients.get_sockets(), self.clients.get_sockets(), [], 0.01)
            # print(self.messages)
            for current_socket in rlist:
                if current_socket is self.server_socket:
                    (new_socket, address) = self.server_socket.accept()
                    # self.open_client_sockets[
                    #     new_socket] = ""  # now if new socket is signing in, his name will be "" and then it is easy to get him
                    key = Fernet.generate_key()
                    self.clients.add_client('', new_socket,key)
                    print("new client")
                    new_socket.send(key.decode().encode('utf-8'))
                    print("sent key")
                else:
                    data = current_socket.recv(1024)
                    if not data.decode('utf-8') == '':
                        #print("189" + data.decode())

                        #key, data = data.split(b"%%%")
                        #print(type(key), "= ", key)
                        key = self.clients.get_key_by_socket(current_socket)
                        data = self.do_decrypt(key, data)
                        #print(str(data.decode('utf-8')))
                    # if self.open_client_sockets[current_socket] == "":  # this is the sign of new singing in user
                    if self.clients.get_username(current_socket) == '':  # this is the sign of new singing in user
                        if self.check_client_exit(data):
                            temp_d = data.split(b'%%%')
                            if len(temp_d) == 3:
                                self.signup_process(data, current_socket, wlist)
                            if len(temp_d) == 2:
                                self.login_process(data, current_socket, wlist)
                    else:
                        self.decifer(data, current_socket)
            time.sleep(0.05)
            self.send_waiting_messages(wlist)

    def send_waiting_messages(self, wlist):
        for message in self.messages:
            (data, current_sockets) = message
            # for client_socket in list(self.open_client_sockets.keys()):
            for i, client_socket in enumerate(self.clients.get_sockets()):
                if client_socket in current_sockets and client_socket in wlist:
                    #print(f'\n\nsend waiting messages in loop{i} {client_socket}\n\n')
                    #key = Fernet.generate_key()  # generates new key (bytes object) randomly
                    #lol = data
                    key = self.clients.get_key_by_socket(client_socket)
                    # me = key.decode() + "%%%" + self.do_encrypt(key, data.encode()).decode()
                    me = self.do_encrypt(key, data.encode()).decode()

                    #print("the data in line 336: " + str(data))
                    start_msg = "Start_Seg".encode('utf-8')
                    close_msg = "End_Seg".encode('utf-8')
                    msg_to_send = me.encode('utf-8')

                    # time.sleep(0.25)
                    msg_to_send = start_msg + msg_to_send + close_msg
                    client_socket.send(msg_to_send)

                    print("384 msg_to_send = "+str(msg_to_send))
                    #print(self.clients.get_username(client_socket))
                    current_sockets.remove(client_socket)
                    message = (data, current_sockets)
            if len(current_sockets) == 0:
                try:
                    self.messages.remove(message)
                except:
                    continue
                break

    def login_process(self, data, current_socket, wlist):
        arr = data.split(b'%%%')
        username = arr[0].decode()
        hashed_pass = arr[1].decode()
        #print("username= ", username, "hashed_pass= ", hashed_pass)
        boolean = self.is_user_in_database(current_socket, username, hashed_pass)
        self.send_waiting_messages(wlist)
        #print(self.messages)
        self.send_waiting_messages(wlist)
        if boolean == True:
            #print("dict before :", self.open_client_sockets)
            self.clients.set_username(current_socket, username)

            for i in self.get_column_from_db("id", self.db["users"]):
                if self.db["users"].get(i)["username"] == username:
                    current_id = i
                    break
            for chat_id in self.get_column_from_db("id", self.db["chats"]):
                if self.db["chats"].get(chat_id)["user_id"] == current_id:
                    print("BROOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
                    chat_id = self.db["chats"].get(chat_id)["id"]
                    chat_external_id = self.db["chats"].get(chat_id)["external_id"]
                    chat_name = self.db["chats"].get(chat_id)["name"]
                    contacts = self.db["chats"].get(chat_id)["contacts"]
                    new_msgs = self.db["chats"].get(chat_id)["new_msgs"]
                    msg_to_send = f"new chat%%%{chat_id}%%%{chat_external_id}%%%{chat_name}%%%{contacts}%%%{new_msgs}"
                    self.msg_maker(msg_to_send, [current_socket])
            #print(self.clients.get_usernames(), self.clients)
            #print("dict after :", self.open_client_sockets)
            # current_socket.send()

    def is_user_in_database(self, current_socket, username, hashed_pass):
        list = []
        list.append(current_socket)
        current_id = 1
        while True:
            try:
                dict = self.db['users'].get(current_id)
                if dict["username"] == username and dict["hashed_password"] == hashed_pass:
                    # here the server needs send key to client and to send the chats msgs  "new chat msgs"
                    self.msg_maker("loged-in", list)
                    ###########################################
                    rlist, wlist, xlist = select.select([self.server_socket] + self.clients.get_sockets(), self.clients.get_sockets(), [], 0.01)
                    self.send_waiting_messages(wlist)
                    for chat_id in self.get_column_from_db("id", self.db["chats"]):
                        chat = self.db["chats"].get(chat_id)
                        if chat["user_id"] == current_id:
                            print("hello")
                            print (str(current_id))
                            chat_id = chat_id
                            external_id = chat["external_id"]
                            chat_name = chat["name"]
                            contacts = chat["contacts"]
                            self.msg_maker(f"new chat%%%{chat_id}%%%{external_id}%%%{chat_name}%%%{contacts}", list)
                    ##########################################

                    return True
                current_id = current_id + 1
            except NotFoundError:
                self.msg_maker("try again", list)
                return False





    def check_client_exit(self, data):
        if len(data.split(b'%%%')) == 2:
            tmp = data.split(b'%%%')
            if tmp[1] == b'NAK':
                #print(tmp[0].decode("utf-8") + " has logedout")
                self.clients.remove_client(tmp[0].decode('utf-8'))
                #print('exit client: ', tmp[0].decode('utf-8'))
                return False
        return True

    def do_decrypt(self, key, data):  # the params are byte object. return byte object
        f = Fernet(key)
        return f.decrypt(data)

    def do_encrypt(self, key, data):  # the params are byte object. return byte object
        f = Fernet(key)
        return f.encrypt(data)
    def update_db_after_client_NAK(self, data):
        if len(data) > 2:
            data = data[2:]
            for i, dt in enumerate(data):
                if i % 2 == 0:
                    chat_id = int(dt)
                    new_msgs = int(data[i + 1])
                    self.db["chats"].update(chat_id, {"new_msgs": new_msgs})
    def decifer(self, data, current_socket):
        '''___TODO___'''
        #print('enter decifer')
        if data.split(b'%%%')[0].decode('utf-8') == 'NAK':
            data = data.decode('utf-8').split("%%%")
            print(f"NAK data: {data}")
            username = data[1]
            self.update_db_after_client_NAK(data)
            self.clients.remove_client(username)

#        if len(data.split(b'%%%')) == 2:
 #           tmp = data.split(b'%%%')
  #          if tmp[1] == b'NAK':
   #             #print(tmp[0].decode("utf-8") + " has logedout")
    #            self.clients.remove_client(tmp[0].decode('utf-8'))
                #print('exit client: ', tmp[0].decode('utf-8'))

        elif len(data.split(b'%%%')) == 3:
            #print("322"+data.decode('utf-8'))
            temp = data.decode('utf-8').split("%%%")
            command = temp[0]
            if command == "public":
                username = temp[1]
                socket_sender = self.clients.get_socket(username)
                msg = command + '%%%' + username + '%%%' + temp[2]
                self.send_messages_without_sender(msg, socket_sender)
            if command == "create chat":
                chat_name = temp[1]
                #print("332 temp[2] = "+temp[2])
                contacts = temp[2].split(",")#the self username
                #print(str(contacts))
                #print("contacts = "+str(contacts))
                self.create_new_chat(chat_name, contacts)
            if command == "chat request":
                chat_id = temp[1]
                external_id = temp[2]
            #sends all the msgs in this chat
                msgs = self.db["chats"].get(chat_id)["msgs"]
                self.db["chats"].update(chat_id, {"new_msgs": 0})
                #user_id = self.db["chats"].get(chat_id)["user_id"]
                #username = self.db["users"].get(user_id)["username"]
                #print(f"user_id: {user_id}\nusername{username}\nself.clients.get_usernames(){self.clients.get_usernames()}")
                msg_to_send = f"private%%%%%%{chat_id}%%%{msgs}"
                sockets_list_to_send = []
                sockets_list_to_send.append(current_socket)
                self.msg_maker(msg_to_send, sockets_list_to_send)


        elif len(data.split(b'%%%')) == 5:# this is a private msg condition
            data = data.decode('utf-8')
            # save the new msgs in db---
            self.save_msg_in_db1(data)
            #---------------------------
            data = data.split("%%%")
            command = data[0]
            sender_username = data[1]
            sender_chat_id = data[2]
            external_id = data[3]
            msg = data[4]


            #SENDS THE MSG TO THE CHAT CONTACTS AND TO SAVE IT IN THE DB
            list_of_sockets_to_send = []
            #list_of_contacts = self.get_list_of_contacts(external_id)
            list_of_contacts = self.db["chats"].get(sender_chat_id)["contacts"].split(',')
            all_ids_in_users = self.get_column_from_db("id", self.db["users"])
            ids_to_send = []
            usernames_to_send = []
            for contact in list_of_contacts:
                if contact in self.clients.get_usernames():
                    for current_id in all_ids_in_users:
                        if self.db["users"].get(current_id)["username"] == contact:
                            ids_to_send.append(current_id)
                            usernames_to_send.append(contact)
                            break
            #now the usernames and the ids orgenized
            for i in range(len(usernames_to_send)):
                username = usernames_to_send[i]
                id_of_username = ids_to_send[i]
                if username != sender_username:
                    socket = self.clients.get_socket(username)
                    sockets = [socket]
                    print("self.get_column_from_db('id',self.db['chats']) = "+str(self.get_column_from_db("id",self.db["chats"])))
                    c = None
                    for id in self.get_column_from_db("id",self.db["chats"]):
                        if str(self.db["chats"].get(id)["user_id"]) == str(id_of_username) and str(self.db["chats"].get(id)["external_id"]) == str(external_id):
                            c = id
                            break


                    self.msg_maker(f"private%%%{sender_username}%%%{c}%%%{msg}", sockets)


    def send_messages_without_sender(self, message, sender):
        orgi_msg = message
        for client_socket in self.clients.get_sockets():
            if not client_socket == sender:
                #key = Fernet.generate_key()  # generates new key (bytes object) randomly
                # message = key.decode() + "%%%" + self.do_encrypt(key, orgi_msg.encode()).decode()
                key = self.clients.get_key_by_socket(client_socket)
                message = self.do_encrypt(key, orgi_msg.encode()).decode()
                message = "Start_Seg" + message + "End_Seg"
                client_socket.send(message.encode('utf-8'))
                #print(f"id{client_socket} :" + message)
                #print(self.clients.get_username(client_socket))

    def send_message_clients(self, message, clients):
        for client in self.clients.get_sockets():
            if client in clients:
                client.send(message.encode('utf-8'))

    def signup_process(self, data, curret_socket, wlist):
        '''__TODO__ SEND THIS PARAMS TO THE DATABASE'''
        '''THE PROTOCLOL IS SIMPLE <EMAIL>%%%<USERNAME>%%%<HASHED PASSWORD>'''
        arr = data.split(b'%%%')
        email = arr[0].decode()
        username = arr[1].decode()
        hashed_pass = arr[2].decode()
        #print("username= ", username, 'email= ', email, "hashed_pass= ", hashed_pass)
        boolean = self.save_new_user_to_database(curret_socket, email, username, hashed_pass)
        if boolean == True:
            self.send_waiting_messages(wlist)
            #print("dict before :", self.open_client_sockets)
            # self.open_client_sockets.__delitem__(curret_socket)
            #print("dict after :", self.open_client_sockets)


Server().run()
