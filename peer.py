from socket import *
import threading
import time
import select
import logging
import colorama
from colorama import *


# Server side of peer
colorama.init(autoreset=True)


class PeerServer(threading.Thread):

    # Peer server initialization
    def __init__(self, username, peerServerPort):
        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.username = username
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        # port number of the peer server
        self.peerServerPort = peerServerPort
        # if 1, then user is already chatting with someone
        # if 0, then user is not chatting with anyone
        self.isChatRequested = 0
        # keeps the socket for the peer that is connected to this peer
        self.connectedPeerSocket = None
        # keeps the ip of the peer that is connected to this peer's server
        self.connectedPeerIP = None
        # keeps the port number of the peer that is connected to this peer's server
        self.connectedPeerPort = None
        # online status of the peer
        self.isOnline = True
        # keeps the username of the peer that this peer is chatting with
        self.chattingClientName = None
        self.connectedPeers = []

    # main method of the peer server thread
    def run(self):

        print(f"{Fore.GREEN}Peer server started...{Fore.RESET}")

        # gets the ip address of this peer
        # first checks to get it for windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macos devices
        hostname = gethostname()
        try:
            self.peerServerHostname = gethostbyname(hostname)
        except gaierror:
            import netifaces as ni
            self.peerServerHostname = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

        # ip address of this peer
        # self.peerServerHostname = 'localhost'
        # socket initializations for the server of the peer
        self.tcpServerSocket.bind((self.peerServerHostname, self.peerServerPort))
        self.tcpServerSocket.listen(4)
        # inputs sockets that should be listened
        inputs = [self.tcpServerSocket]
        # server listens as long as there is a socket to listen in the inputs list and the user is online
        while inputs and self.isOnline:
            # monitors for the incoming connections
            try:
                readable, writable, exceptional = select.select(inputs + self.connectedPeers, [], [],1)
                # If a server waits to be connected enters here
                for s in readable:
                    # if the socket that is receiving the connection is
                    # the tcp socket of the peer's server, enters here
                    if s is self.tcpServerSocket:
                        # accepts the connection, and adds its connection socket to the inputs list
                        # so that we can monitor that socket as well
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        self.connectedPeers.append(connected)               # if the user is not chatting, then the ip and the socket of

                    else:
                        message = s.recv(1024).decode().split("\n")
                        if len(message) == 0:
                            s.close()
                            self.connectedPeers.remove(s)
                        elif message[0] == "chatroom-join":
                            print(message[1] + " has joined the chatroom.")
                            s.send("welcome".encode())
                        elif message[0] == "chatroom-leave":
                            print(message[1] + " has left the chatroom.")
                            s.close()
                            self.connectedPeers.remove(s)
                        elif message[0] == "chat-message":
                            username = message[1]
                            content = "\n".join(message[2:])
                            print(username + " -> " + content)

            # handles the exceptions, and logs them
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))


# Client side of peer
class PeerClient(threading.Thread):
    # variable initializations for the client side of the peer
    def __init__(self,username, chatroom, peerServer, peersToConnect=None):
        threading.Thread.__init__(self)
        # keeps the ip address of the peer that this will connect
        # keeps the username of the peer
        self.username = username
        # keeps the port number that this client should connect
        # client side tcp socket initialization
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        # keeps the server of this client
        self.peerServer = peerServer
        self.isEndingChat = False
        self.chatroom = chatroom
        if peersToConnect is not None:
            for peer in peersToConnect:
                peer = peer.split(",")
                peerHost = peer[0]
                peerPort = int(peer[1])
                sock = socket(AF_INET, SOCK_STREAM)
                sock.connect((peerHost, peerPort))
                message = "chatroom-join\n{}".format(self.username)
                sock.send(message.encode())
                self.peerServer.connectedPeers.append(sock)


    # main method of the peer client thread
    def run(self):
        print("Peer client started...")
        print('Chatroom joined Successfully. \nStart typing to send a message. Send "Exit" to leave the chatroom.')
        while self.chatroom is not None:
            content = input()

            if content == "Exit":
                message = "chatroom-leave\n" + self.username
            else:
                message = "chat-message\n{}\n{}".format(self.username, content)
            for sock in self.peerServer.connectedPeers:
                try:
                    sock.send(message.encode())
                except:
                    pass

            if content == "Exit":
                self.chatroom = None
                for sock in self.peerServer.connectedPeers:
                    sock.close()


# main process of the peer
class peerMain:

    # peer initializations
    def __init__(self,username=None):
        # ip address of the registry
        self.username = username
        self.registryName = input(f"{Fore.BLUE}Enter IP address of registry: {Fore.RESET} ")
        # self.registryName = 'localhost'
        # port number of the registry
        self.registryPort = 1500
        # tcp socket connection to registry
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.registryName, self.registryPort))
        # initializes udp socket which is used to send hello messages
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the registry
        self.registryUDPPort = 1200
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.isOnline = False
        # server port number of this peer
        self.peerServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
        # timer initialization
        self.timer = None

        choice = "0"
        # log file initialization
        logging.basicConfig(filename="peer.log", level=logging.INFO)
        # as long as the user is not logged out, asks to select an option in the menu
        while choice != "3":
            # menu selection prompt
            if not self.isOnline:
                choice = input(
                    f"{Fore.BLUE}Choose: \nCreate account: 1\nLogin: 2\n{Fore.RESET}")
                # if choice is 1, creates an account with the username
                # and password entered by the user
                if choice == "1":
                    username = input(f"{Fore.LIGHTRED_EX}username: {Fore.RESET}")
                    password = input(f"{Fore.LIGHTRED_EX}password: {Fore.RESET}")
                    self.createAccount(username, password)
                # if choice is 2 and user is not logged in, asks for the username
                # and the password to login
                elif choice == "2" and not self.isOnline:
                    username = input(f"{Fore.LIGHTRED_EX}username: {Fore.RESET}")
                    password = input(f"{Fore.LIGHTRED_EX}password: {Fore.RESET}")
                    # asks for the port number for server's tcp socket
                    peerServerPort = int(input(f"{Fore.YELLOW}Enter a port number for peer server: {Fore.RESET}"))
                    status = self.login(username, password, peerServerPort)
                    # is user logs in successfully, peer variables are set

                    if status == 1:

                        self.isOnline = True
                        self.loginCredentials = (username, password)
                        self.username=username
                        self.peerServerPort = peerServerPort
                        # creates the server thread for this peer, and runs it
                        self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort)
                        self.peerServer.start()
                        # hello message is sent to registry
                        self.sendHelloMessage()
                # if choice is 3 and user is logged in, then user is logged out
                # and peer variables are set, and server and client sockets are closed
            elif self.isOnline:
                choice = input(
                    f"{Fore.LIGHTBLUE_EX}Choose: Logout: 1\nSearch Online Users: 2\nStart Chat: 3\nCreate Chatroom: 4\n"
                    f"Join Chatroom: 5\nList Chatrooms: 6\nList Online Users:7\n{Fore.RESET}")
                if choice == "1" and self.isOnline:
                    self.logout(1)
                    self.isOnline = False
                    self.loginCredentials = (None, None)
                    self.peerServer.isOnline = False
                    self.peerServer.tcpServerSocket.close()
                    if self.peerClient is not None:
                        self.peerClient.tcpClientSocket.close()
                    print("Logged out successfully")
                # is peer is not logged in and exits the program
                elif choice == "1":
                    self.logout(2)
                # if choice is 4 and user is online, then user is asked
                # for a username that is wanted to be searched
                elif choice == "2" and self.isOnline:
                    username = input("Username to be searched: ")
                    searchStatus = self.searchUser(username)
                    # if user is found its ip address is shown to user
                    if searchStatus is not None and searchStatus != 0:
                        print("IP address of " + username + " is " + searchStatus)
                # if choice is 5 and user is online, then user is asked
                # to enter the username of the user that is wanted to be chatted
                elif choice == "3" and self.isOnline:
                    username = input("Enter the username of user to start chat: ")
                    searchStatus = self.searchUser(username)
                    # if searched user is found, then its ip address and port number is retrieved
                    # and a client thread is created
                    # main process waits for the client thread to finish its chat
                    if searchStatus is not None and searchStatus != 0:
                        searchStatus = searchStatus.split(":")
                        self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]), self.loginCredentials[0],
                                                     self.peerServer, None)
                        self.peerClient.start()
                        self.peerClient.join()
                elif choice=="4" and self.isOnline:
                    name = input("Enter the name of Chatroom to start chat: ")
                    message = "chatroom-Create\n{}".format(name)
                    self.tcpClientSocket.send(message.encode())
                    response = self.tcpClientSocket.recv(1024).decode()

                    if response == "chatroom-name-exists":
                        print("There already exists a chatroom with this name.")
                    elif response == "chatroom-creation-success":
                        print("Chatroom created successfully")
                        self.chatroomJoin(name)
                    else:
                        # Handle other cases if needed
                        print("Unknown response:", response)

                    if response[0] == "chatroom-not-found":
                        print("No chatroom exists with this name.")
                    elif response[0] == "chatroom-join-success":
                        if len(response) == 1:
                            self.peerClient = PeerClient(self.username, name, self.peerServer)
                        else:
                            self.peerClient = PeerClient(self.username, name, self.peerServer, response[1:])
                        self.peerClient.start()
                        self.peerClient.join()

                        # This section will only run after the user quits the chatroom
                        self.tcpClientSocket.send("chatroom-leave-request".encode())
                    else:
                        # Handle other cases if needed
                        print("Unknown response:", response[0])


                elif choice == "5" and self.isOnline:
                   self.chatroomJoin(input("Enter your Chat Name : "))
                elif choice=="6" and self.isOnline:
                    message = "chatroom-list-request"
                    self.tcpClientSocket.send(message.encode())
                    response = self.tcpClientSocket.recv(1024).decode().split("\n")

                    if response[0] == "chatroom-list":
                        print("Available Chatrooms:")
                        for chatroom in response[1:]:
                            print("\n\t" + chatroom + " users connected")
                elif choice == "7" and self.isOnline:
                    message = "online-users"
                    self.tcpClientSocket.send(message.encode())
                    response = self.tcpClientSocket.recv(1024).decode().split("\n")

                    if response[0] == "online-users":
                        print("Online Users:")
                        for user in response[1:]:
                            print("\n\t" + user)



            elif choice == "OK" and self.isOnline:
                okMessage = "OK " + self.loginCredentials[0]
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)
                self.peerServer.connectedPeerSocket.send(okMessage.encode())
                self.peerClient = PeerClient(self.peerServer.connectedPeerIP, self.peerServer.connectedPeerPort,
                                             self.loginCredentials[0], self.peerServer, "OK")
                self.peerClient.start()
                self.peerClient.join()
            # if user rejects the chat request then reject message is sent to the requester side
            elif choice == "REJECT" and self.isOnline:
                self.peerServer.connectedPeerSocket.send("REJECT".encode())
                self.peerServer.isChatRequested = 0
                logging.info("Send to " + self.peerServer.connectedPeerIP + " -> REJECT")
            # if choice is cancel timer for hello message is cancelled
            elif choice == "CANCEL":
                self.timer.cancel()
                break
        # if main process is not ended with cancel selection
        # socket of the client is closed
        if choice != "CANCEL":
            self.tcpClientSocket.close()

    # account creation function
    def createAccount(self, username, password):
        # join message to create an account is composed and sent to registry
        # if response is success then informs the user for account creation
        # if response is exist then informs the user for account existence
        message = "JOIN " + username + " " + password
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print(f"{Fore.LIGHTYELLOW_EX}Account created...{Fore.RESET}")
        elif response == "join-exist":
            print(f"{Fore.LIGHTRED_EX}choose another username or login...{Fore.RESET}")

    # login function
    def login(self, username, password, peerServerPort):
        # a login message is composed and sent to registry
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " + str(peerServerPort)
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "login-success":
            print(f"{Fore.GREEN}Logged in successfully...{Fore.RESET}")
            return 1
        elif response == "login-account-not-exist":
            print(f"{Fore.RED}Account does not exist...{Fore.RESET}")
            return 0
        elif response == "login-online":
            print(f"{Fore.GREEN}Account is already online...{Fore.RESET}")
            return 2
        elif response == "login-wrong-password":
            print(f"{Fore.RED}Wrong password...{Fore.RESET}")
            return 3

    # logout function
    def logout(self, option):
        # a logout message is composed and sent to registry
        # timer is stopped
        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        else:
            message = "LOGOUT"
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())

    # function for searching an online user
    def searchUser(self, username):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "SEARCH " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        if response[0] == "search-success":
            print(username + " is found successfully...")
            return response[1]
        elif response[0] == "search-user-not-online":
            print(username + " is not online...")
            return 0
        elif response[0] == "search-user-not-found":
            print(username + " is not found")
            return None

    def chatroomJoin(self, name):
        message = "chatroom-join-request\n{}".format(name)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split("\n")
        if response[0] == "chatroom-not-found":
            print("No chatroom exists with this name.")
        elif response[0] == "chatroom-join-success":
            if len(response) == 1:
                self.peerClient = PeerClient(self.username, name, self.peerServer)
            else:
                self.peerClient = PeerClient(self.username, name, self.peerServer, response[1:])
            self.peerClient.start()
            self.peerClient.join()

            # This section will only run after the user quits the chatroom
            self.tcpClientSocket.send("chatroom-leave-request".encode())
        else:
            # Handle other cases if needed
            print("Unknown response:", response[0])


    def broadcast_message(self, room_name, sender, message):
        # Iterate through the list of online users in the chat room
        for peer in self.online_users[room_name]:
            # Send the message to each online peer in the chat room
            peer.send_message(room_name, sender, message)

    def send_message(self, room_name, sender, message):
        for username, peer_socket in self.online_users[room_name]:
            # Assuming peer_socket is an actual socket
            try:
                # Create a message format that includes room_name, sender, and the actual message
                formatted_message = f"{sender}: {message}"

                # Send the formatted message to each online peer's socket
                peer_socket.send(formatted_message.encode())
            except Exception as e:
                if username is not None:
                    print(f"Error sending message to {username}: {e}")
                else:
                    print(f"Error sending message: {e}")

    def get_current_username(self):
        # Return the current username
        return self.current_username

    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of registry
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        logging.info("Send to " + self.registryName + ":" + str(self.registryUDPPort) + " -> " + message)
        self.udpClientSocket.sendto(message.encode(), (self.registryName, self.registryUDPPort))
        self.timer = threading.Timer(1, self.sendHelloMessage)
        self.timer.start()


# peer is started
peerMain()
