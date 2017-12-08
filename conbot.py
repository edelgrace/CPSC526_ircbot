# Edel Altares 1009872 Tutorial 2

import argparse
import datetime
import os
import queue
import select
import socket
import sys
import time
import threading


class Bot:
    HOSTNAME = None
    PORT = None
    CHANNEL = None

    OLD_HOST = None
    OLD_PORT = None
    OLD_CHAN = None
    OLD_SCKT = None

    SECRET = None
    BOT_SOCKET = None
    CONTROLLER = None

    ATTACK_COUNT = 0
    BOT_COUNT = 0
    NICK_COUNT = 0

    MESSAGES = {}
    INPUTS = []

    PONG = False
    CONNECTED_SOCKET = False
    CONNECTED_SERVER = False
    JOINED = False
    SHUTDOWN = False
    MIGRATE = False

    def parse(self):
        """ Parse the arguments """

        parser = argparse.ArgumentParser()

        # required arguments
        parser.add_argument('hostname')
        parser.add_argument('port', type=int)
        parser.add_argument('channel')
        parser.add_argument('secret_phrase')

        # parse the arguments
        arguments = parser.parse_args()

        # save variables
        self.HOSTNAME = arguments.hostname
        self.PORT = arguments.port
        self.CHANNEL = arguments.channel
        self.SECRET = arguments.secret_phrase

        return


    def setup(self):
        """ Setup the bot """
        
        # reset variables
        self.CONTROLLER = None

        self.MESSAGES = {}
        self.INPUTS = []

        self.PONG = False
        self.CONNECTED_SOCKET = False
        self.CONNECTED_SERVER = False
        self.JOINED = False
        self.SHUTDOWN = False
        self.MIGRATE = False
        
        # setup the client socket
        try:
            # connect to server
            self.BOT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.BOT_SOCKET.connect((self.HOSTNAME, self.PORT))

            # setup select
            self.INPUTS.append(self.BOT_SOCKET)
            self.MESSAGES[self.BOT_SOCKET] = queue.Queue()

            self.CONNECTED_SOCKET = True

        except Exception as e:
            print("ERROR: " + str(e))
            self.CONNECTED_SOCKET = False

        return


    def send_msg(self, data):
        """ Function to send message to a socket """
        
        print("Sending:\t" + data)

        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data, "utf-8")

        try:
            # queue up the data
            self.MESSAGES[self.BOT_SOCKET].put(data)

        except Exception as e:
            print("ERROR: " + str(e))


    def check_data(self, data):
        """ Check the data """

        # split data into lines
        data = data.split("\r\n")


        for line in data:

            line = line.split()

            if len(line) < 2:
                continue

            # nickname collision
            if line[1] == "433":
                self.NICK_COUNT += 1
                self.CONNECTED_SERVER = False

                print("Nickname already used")

            # check if bot logged onto IRC server
            elif line[1] == "462":
                self.NICK_COUNT += 1
                self.CONNECTED_SERVER = False

                print("Nickname already used")
                
            # join server successfully
            elif line[1] == "001":
                self.CONNECTED_SERVER = True

                print("Joined server successfully")

            # join channel successfully
            elif line[1] == "JOIN":
                self.JOINED = True

                print("Joined channel successfully")

            # responde to ping
            elif line[0] == "PING" and not self.PONG:
                self.send_msg("PONG " + line[1])

                print("Sent ping")


    def cmds(self, data):
        """ Listen for commands """

        data = data.split(":")

        # get the message and sendedr
        msg = data[-1]
        sender = data[1].split("!")[0]

        # set the controller for the first time
        if self.CONTROLLER is None and sender != "edel" + str(self.NICK_COUNT):
            self.CONTROLLER = sender

        # check if the controller
        if self.CONTROLLER == sender:

            # shutdown bot
            if ("shutdown " + self.SECRET) in msg:
                print("SHUTDOWN command issued")
                self.shutdown()

            # send nick to controller
            if ("status " + self.SECRET) in msg:
                print("STATUS command issued")
                self.status()

            msg = msg.split()

            # DEBUG
            print("DEBUG msg")
            print(msg)

            # attack with bot
            if msg[0] == "attack" and msg[-1] == self.SECRET and len(msg) == 4:
                print("ATTACK command issued")
               
                host = msg[1]
                port = msg[2]

                self.attack(host, port)

            # move to another server
            elif msg[0] == "move" and msg[-1] == self.SECRET and len(msg) == 5:
                print("MOVE command issued")

                host = msg[1]
                port = msg[2]
                chan = msg[3]

                self.migrate(host, port, chan)

            else:
                # controller did not issue a command 
                return


    def handshake(self):
        """ Send the username """
        
        try:
            # send the NICk
            msg = "NICK edelControl" + str(self.NICK_COUNT) + "\n"
            self.send_msg(msg)

            # send the USER
            msg = "USER edel" + str(self.NICK_COUNT) + " * * :Edel Altares\n"
            self.send_msg(msg)

        except Exception as e:
            print(e)

        return


    def join(self):
        """ Join set channel """

        try:
            # send join request
            msg = "JOIN #" + str(self.CHANNEL) + "\n"
            self.send_msg(msg)

        except Exception as e:
            print(str(e))


    def attack(self, host, port):
        """ Perform an attack """

        port = int(port)

        # increase count
        self.ATTACK_COUNT += 1

        # connect
        try:
            attack_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            attack_socket.connect((host, port))
            
        except Exception as e:            
            print("ERROR: Attack failed " + str(e))

            # send failure to controller
            msg = "PRIVMSG " + self.CONTROLLER
            msg += " :Attack " + host + " " + str(port) + " failed " + self.SECRET
            msg += "\n"
            
            self.send_msg(msg)

            return

        print("Attack successful")

        # send message
        msg = str(self.ATTACK_COUNT) + " edel" + str(self.NICK_COUNT)
        msg = bytes(msg, "utf-8")
        attack_socket.send(msg)

        # close socket
        attack_socket.close()

        # send to controller
        msg = "PRIVMSG " + self.CONTROLLER
        msg += " :Attack " + host + " " + str(port) + " successful " + self.SECRET
        msg += "\n"
        self.send_msg(msg)

        return


    def migrate(self, host, port, chan):
        """ Migrate to a different IRC server """

        port = int(port)

        try:
            # connect
            new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_socket.connect((host, port))

        except Exception as e:
            print("Error: Move failed " + str(e))     

            # send to controller
            msg = "PRIVMSG " + self.CONTROLLER
            msg += " :Move " + host + " " + str(port) + " failed " + self.SECRET
            msg += "\n"
            
            self.send_msg(msg) 

            return

        # success
        print("Move successful")

        # send to controller
        msg = "PRIVMSG " + self.CONTROLLER
        msg += " :Move " + host + " " + str(port) + " successful " + self.SECRET
        msg += "\n"

        self.send_msg(msg)
        
        self.MIGRATE = True

        # old variables
        self.OLD_CHAN = self.CHANNEL
        self.OLD_HOST = self.HOSTNAME
        self.OLD_PORT = self.PORT
        self.OLD_SCKT = self.BOT_SOCKET

        # new variables
        self.HOSTNAME = host
        self.PORT = port
        self.CHANNEL = chan

        # reset variables
        self.BOT_SOCKET = new_socket

        self.MESSAGES[self.BOT_SOCKET] = queue.Queue()
        self.INPUTS = [self.BOT_SOCKET]

        self.PONG = False
        self.CONNECTED_SOCKET = False
        self.CONNECTED_SERVER = False
        self.JOINED = False
        self.SHUTDOWN = False
        
        # change flag
        self.MIGRATE = True

        return


    def shutdown(self):
        """ Shutdown the bot """

        # send msg
        msg = "PRIVMSG " + self.CONTROLLER + " :edel" + str(self.NICK_COUNT) + " " + self.SECRET + "\n"

        self.send_msg(msg)

        print("Terminating bot...")

        self.SHUTDOWN = True

        return


    def status(self):
        """ Report status """

        msg = "PRIVMSG " + self.CONTROLLER + " :edel" + str(self.NICK_COUNT) + " " + self.SECRET + "\n"

        self.send_msg(msg)

        return


    def run(self):
        while True:
            readable, writable, exceptable = select.select(self.INPUTS, self.INPUTS, [])

            for socket in readable:

                # receive data from socket
                socket.settimeout(5)
                data = socket.recv(1024)
                socket.settimeout(None)

                # there is data to be received
                if data:

                    # check the data
                    data = data.decode("utf-8")
                    print(data)
                    self.check_data(data)

                    # register on server
                    if not self.CONNECTED_SERVER:
                        self.handshake()

                    # join a channel
                    if self.CONNECTED_SERVER and not self.JOINED:
                        self.join()

                    # listen for commands
                    if self.CONNECTED_SERVER and self.JOINED and not self.PONG:
                        self.cmds(data)

                # connection was closed
                else:
                    self.CONNECTED_SOCKET = False

            for socket in writable:
                try:
                    # get the msg
                    next_msg = self.MESSAGES[socket].get_nowait()

                except queue.Empty:
                    # shutdown
                    if self.SHUTDOWN:
                        sys.exit(0)

                    # redo handshake and close socket
                    if self.MIGRATE:
                        self.handshake()

                        self.MIGRATE = False
                        
                        self.OLD_SCKT.close()
                    continue

                else:
                    # send the msg
                    print(next_msg)
                    socket.send(next_msg)
                    print("DEBUG: MEssage sent")


def run():
    """ Run the controller """
    conBot = Bot()

    # get parsed arguments
    conBot.parse()

    while True:
        conBot.setup()
        
        # check if connected
        if conBot.CONNECTED_SOCKET:
            conBot.run()
        else:
            # wait 5 seconds before reconnecting
            print("Attempting reconnection...")
            time.sleep(5)


# run the program
if __name__ == "__main__":
    
    try:
        run()
    except KeyboardInterrupt:    
        sys.exit(0)
