from pymongo import MongoClient

class DB:
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p-chat']

    def is_account_exist(self, username):
        return self.db.accounts.count_documents({'username': username}) > 0

    def register(self, username, password):
        account = {
            "username": username,
            "password": password
        }
        self.db.accounts.insert_one(account)

    def get_password(self, username):
        user_data = self.db.accounts.find_one({"username": username})
        return user_data["password"] if user_data else None

    def is_account_online(self, username):
        return self.db.online_peers.count_documents({"username": username}) > 0

    def user_login(self, username, ip, port):
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port
        }
        self.db.online_peers.insert_one(online_peer)

    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})

    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return (res["ip"], res["port"]) if res else (None, None)


    def get_online_users(self, room_name):
        # Retrieve the list of online users in the chat room
        chat_room = self.db.chat_rooms.find_one({'name': room_name})
        online_users = chat_room.get('online_users', [])

        # Format the list of online users as a string
        online_users_str = ', '.join(str(user) for user in online_users)
        return online_users_str

    def send_message(self, room_name, sender, message):
        # Assuming you have a collection for storing chat messages in the database
        chat_messages = self.db.chat_messages
        message_data = {
            'room_name': room_name,
            'sender': sender,
            'message': message
        }
        chat_messages.insert_one(message_data)
