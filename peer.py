import hashlib
from socket import *
import threading
import time
import select
import logging
import colorama
from colorama import *
colorama.init(convert=True)
# Server side of peer
colorama.init(autoreset=True)
class peerserver(threading.Thread):

    # Peer server initialization
    def __init__(self, username, peerserverPort):
        threading.Thread.__init__(self)
        # keeps the username of the peer
        self.username = username
        # tcp socket for peer server
        self.tcpServerSocket = socket(AF_INET, SOCK_STREAM)
        # port number of the peer server
        self.peerserverPort = peerserverPort
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

        print(f"{Fore.RED}Peer server started...{Fore.RESET}")

        # gets the ip address of this peer
        # first checks to get it for windows devices
        # if the device that runs this application is not windows
        # it checks to get it for macos devices
        hostname = gethostname()
        try:
            self.peerserverHostname = gethostbyname(hostname)
        except gaierror:
            import netifaces as ni
            self.peerserverHostname = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

        # ip address of this peer
        # self.peerServerHostname = 'localhost'
        # socket initializations for the server of the peer
        self.tcpServerSocket.bind((self.peerserverHostname, self.peerserverPort))
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
                        # this peer is assigned to server variables
                        # if self.isChatRequested == 0:
                        #     print(self.username + " is connected from " + str(addr))
                        #     self.connectedPeerSocket = connected
                        #     self.connectedPeerIP = addr[0]
                    # if the socket that receives the data is the one that
                    # is used to communicate with a connected peer, then enters here
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

            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))


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
                readable, writable, exceptional = select.select(inputs, [], [])
                # If a server waits to be connected enters here
                for s in readable:
                    # if the socket that is receiving the connection is
                    # the tcp socket of the peer's server, enters here
                    if s is self.tcpServerSocket:
                        # accepts the connection, and adds its connection socket to the inputs list
                        # so that we can monitor that socket as well
                        connected, addr = s.accept()
                        connected.setblocking(0)
                        inputs.append(connected)
                        # self.connectedPeers.append(connected)
                        # if the user is not chatting, then the ip and the socket of
                        # if the user is not chatting, then the ip and the socket of
                        # this peer is assigned to server variables
                        if self.isChatRequested == 0:
                            print(self.username + " is connected from " + str(addr))
                            self.connectedPeerSocket = connected
                            self.connectedPeerIP = addr[0]
                    else:
                        messageReceived = s.recv(1024).decode()
                        # logs the received message
                        logging.info("Received from " + str(self.connectedPeerIP) + " -> " + str(messageReceived))
                        # if message is a request message it means that this is the receiver side peer server
                        # so evaluate the chat request
                        if len(messageReceived) > 11 and messageReceived[:12] == "CHAT-REQUEST":
                            # text for proper input choices is printed however OK or REJECT is taken as input in main process of the peer
                            # if the socket that we received the data belongs to the peer that we are chatting with,
                            # enters here
                            if s is self.connectedPeerSocket:
                                # parses the message
                                messageReceived = messageReceived.split()
                                # gets the port of the peer that sends the chat request message
                                self.connectedPeerPort = int(messageReceived[1])
                                # gets the username of the peer sends the chat request message
                                self.chattingClientName = messageReceived[2]
                                # prints prompt for the incoming chat request
                                print("Incoming chat request from " + self.chattingClientName + " >> ")
                                print("Enter OK to accept or REJECT to reject:  ")
                                # makes isChatRequested = 1 which means that peer is chatting with someone
                                self.isChatRequested = 1
                            # if the socket that we received the data does not belong to the peer that we are chatting with
                            # and if the user is already chatting with someone else(isChatRequested = 1), then enters here
                            elif s is not self.connectedPeerSocket and self.isChatRequested == 1:
                                # sends a busy message to the peer that sends a chat request when this peer is
                                # already chatting with someone else
                                message = "BUSY"
                                s.send(message.encode())
                                # remove the peer from the inputs list so that it will not monitor this socket
                                inputs.remove(s)
                        # if an OK message is received then ischatrequested is made 1 and then next messages will be shown to the peer of this server
                        elif messageReceived == "OK":
                            self.isChatRequested = 1
                        # if an REJECT message is received then ischatrequested is made 0 so that it can receive any other chat requests
                        elif messageReceived == "REJECT":
                            self.isChatRequested = 0
                            inputs.remove(s)
                        # if a message is received, and if this is not a quit message ':q' and
                        # if it is not an empty message, show this message to the user
                        elif messageReceived[:2] != ":q" and len(messageReceived) != 0:
                            print(str(self.chattingClientName) + ": " + str(messageReceived))
                        # if the message received is a quit message ':q',
                        # makes ischatrequested 1 to receive new incoming request messages
                        # removes the socket of the connected peer from the inputs list
                        elif messageReceived[:2] == ":q":
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            # connected peer ended the chat
                            if len(messageReceived) == 2:
                                print("User you're chatting with ended the chat")
                                print("Press enter to quit the chat: ")
                        # if the message is an empty one, then it means that the
                        # connected user suddenly ended the chat(an error occurred)
                        elif len(messageReceived) == 0:
                            self.isChatRequested = 0
                            inputs.clear()
                            inputs.append(self.tcpServerSocket)
                            print("User you're chatting with suddenly ended the chat")
                            print("Press enter to quit the chat: ")

            # handles the exceptions, and logs them
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))
            except ValueError as vErr:
                logging.error("ValueError: {0}".format(vErr))


class Peerclient(threading.Thread):
    # variable initializations for the client side of the peer
    def __init__(self,username, chatroom, peerserver, peersToConnect=None):
        threading.Thread.__init__(self)
        # keeps the ip address of the peer that this will connect
        # keeps the username of the peer
        self.username = username
        # keeps the port number that this client should connect
        # client side tcp socket initialization
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        # keeps the server of this client
        self.peerserver = peerserver
        # keeps the phrase that is used when creating the client
        # if the client is created with a phrase, it means this one received the request
        # this phrase should be none if this is the client of the requester peer
        # keeps if this client is ending the chat or not
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
                self.peerserver.connectedPeers.append(sock)


    # main method of the peer client thread
    def run(self):
        # print("Peer client started...")
        print('Chatroom joined Successfully. \nStart typing to send a message. Send ":quit" to leave the chatroom.')
        while self.chatroom is not None:
            content = input()

            if content == ":quit":
                message = "chatroom-leave\n" + self.username
            else:
                message = "chat-message\n{}\n{}".format(self.username, content)
            for sock in self.peerserver.connectedPeers:
                try:
                    sock.send(message.encode())
                except:
                    pass

            if content == ":quit":
                self.chatroom = None
                for sock in self.peerserver.connectedPeers:
                    sock.close()



# Client side of peer
class PeerClient(threading.Thread):
    # variable initializations for the client side of the peer
 def __init__(self,ipToConnect,portToConnect,username,peerServer,responseReceived):
        threading.Thread.__init__(self)
        # keeps the ip address of the peer that this will connect
        # keeps the username of the peer
        self.username = username
        self.ipToConnect = ipToConnect
        self.portToConnect = portToConnect
        # keeps the port number that this client should connect
        # client side tcp socket initialization
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        # keeps the server of this client
        self.peerServer = peerServer
        self.isEndingChat = False
        self.responseReceived=responseReceived



    # main method of the peer client thread
 def run(self):

         print("Peer client started...")
         # connects to the server of other peer
         self.tcpClientSocket.connect((self.ipToConnect, self.portToConnect))
         # if the server of this peer is not connected by someone else and if this is the requester side peer client then enters here
         if self.peerServer.isChatRequested == 0 and self.responseReceived is None:
             # composes a request message and this is sent to server and then this waits a response message from the server this client connects
             requestMessage = "CHAT-REQUEST " + str(self.peerServer.peerServerPort) + " " + self.username
             # logs the chat request sent to other peer
             logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + requestMessage)
             # sends the chat request
             self.tcpClientSocket.send(requestMessage.encode())
             print("Request message " + requestMessage + " is sent...")
             # received a response from the peer which the request message is sent to
             self.responseReceived = self.tcpClientSocket.recv(1024).decode()
             # logs the received message
             logging.info(
                 "Received from " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + self.responseReceived)
             print("Response is " + self.responseReceived)
             # parses the response for the chat request
             self.responseReceived = self.responseReceived.split()
             # if response is ok then incoming messages will be evaluated as client messages and will be sent to the connected server
             if self.responseReceived[0] == "OK":
                 # changes the status of this client's server to chatting
                 self.peerServer.isChatRequested = 1
                 # sets the server variable with the username of the peer that this one is chatting
                 self.peerServer.chattingClientName = self.responseReceived[1]
                 # as long as the server status is chatting, this client can send messages
                 while self.peerServer.isChatRequested == 1:
                     # message input prompt
                     messageSent = input(self.username + ": ")
                     # sends the message to the connected peer, and logs it
                     self.tcpClientSocket.send(messageSent.encode())
                     logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                     # if the quit message is sent, then the server status is changed to not chatting
                     # and this is the side that is ending the chat
                     if messageSent == ":q":
                         self.peerServer.isChatRequested = 0
                         self.isEndingChat = True
                         break
                 # if peer is not chatting, checks if this is not the ending side
                 if self.peerServer.isChatRequested == 0:
                     if not self.isEndingChat:
                         # tries to send a quit message to the connected peer
                         # logs the message and handles the exception
                         try:
                             self.tcpClientSocket.send(":q ending-side".encode())
                             logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> :q")
                         except BrokenPipeError as bpErr:
                             logging.error("BrokenPipeError: {0}".format(bpErr))
                     # closes the socket
                     self.responseReceived = None
                     self.tcpClientSocket.close()
             # if the request is rejected, then changes the server status, sends a reject message to the connected peer's server
             # logs the message and then the socket is closed
             elif self.responseReceived[0] == "REJECT":
                 self.peerServer.isChatRequested = 0
                 print("client of requester is closing...")
                 self.tcpClientSocket.send("REJECT".encode())
                 logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> REJECT")
                 self.tcpClientSocket.close()
             # if a busy response is received, closes the socket
             elif self.responseReceived[0] == "BUSY":
                 print("Receiver peer is busy")
                 self.tcpClientSocket.close()
         # if the client is created with OK message it means that this is the client of receiver side peer
         # so it sends an OK message to the requesting side peer server that it connects and then waits for the user inputs.
         elif self.responseReceived == "OK":
             # server status is changed
             self.peerServer.isChatRequested = 1
             # ok response is sent to the requester side
             okMessage = "OK"
             self.tcpClientSocket.send(okMessage.encode())
             logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + okMessage)
             print("Client with OK message is created... and sending messages")
             # client can send messsages as long as the server status is chatting
             while self.peerServer.isChatRequested == 1:
                 # input prompt for user to enter message
                 messageSent = input(self.username + ": ")
                 self.tcpClientSocket.send(messageSent.encode())
                 logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> " + messageSent)
                 # if a quit message is sent, server status is changed
                 if messageSent == ":q":
                     self.peerServer.isChatRequested = 0
                     self.isEndingChat = True
                     break
             # if server is not chatting, and if this is not the ending side
             # sends a quitting message to the server of the other peer
             # then closes the socket
             if self.peerServer.isChatRequested == 0:
                 if not self.isEndingChat:
                     self.tcpClientSocket.send(":q ending-side".encode())
                     logging.info("Send to " + self.ipToConnect + ":" + str(self.portToConnect) + " -> :q")
                 self.responseReceived = None
                 self.tcpClientSocket.close()




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

        self.peerserver = None
        # client of this peer
        self.PeerClient = None

        self.Peerclient = None
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
                    password = hashlib.sha256(password.encode()).hexdigest()
                    self.createAccount(username, password)
                # if choice is 2 and user is not logged in, asks for the username
                # and the password to login
                elif choice == "2" and not self.isOnline:
                    username = input(f"{Fore.LIGHTRED_EX}username: {Fore.RESET}")
                    password = input(f"{Fore.LIGHTRED_EX}password: {Fore.RESET}")
                    password = hashlib.sha256(password.encode()).hexdigest()
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
                        self.peerserver = peerserver(self.loginCredentials[0], self.peerServerPort)
                        self.peerserver.start()
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
                    if searchStatus is not None and searchStatus != 0:
                        searchStatus = searchStatus.split(":")
                        self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]), self.loginCredentials[0],self.peerServer, None)
                        self.peerClient.start()
                        self.peerClient.join()
                    # if searched user is found, then its ip address and port number is retrieved
                    # and a client thread is created
                    # main process waits for the client thread to finish its chat


                elif choice == "OK" and self.isOnline:
                    okMessage = "OK " + self.loginCredentials[0]
                    logging.info("Send to " + str(self.peerServer.connectedPeerIP) + " -> " + okMessage)
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

                elif choice == "4" and self.isOnline:
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
                            self.Peerclient = Peerclient(self.username, name, self.peerserver)
                        else:
                            self.Peerclient = Peerclient(self.username, name, self.peerserver, response[1:])
                        self.Peerclient.start()
                        self.Peerclient.join()

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
                self.Peerclient = Peerclient(self.username, name, self.peerserver)
            else:
                self.Peerclient = Peerclient(self.username, name, self.peerserver, response[1:])
            self.Peerclient.start()
            self.Peerclient.join()

            # This section will only run after the user quits the chatroom
            self.tcpClientSocket.send("chatroom-leave-request".encode())
        else:
            # Handle other cases if needed
            print("Unknown response:", response[0])

    def printOnlineUsers(self):
        message = "PRINT"
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        print(response)


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