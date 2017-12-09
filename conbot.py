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
    STATE = None
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


    STATUS = []
    MOVE = []
    ATTACK = []
    SHUTDOWN_ARRY = []

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
            self.BOT_SOCKET.settimeout(None)
            self.BOT_SOCKET.connect((self.HOSTNAME, self.PORT))
            self.BOT_SOCKET.setblocking(0)
            print("Attempting to connect...")

            # setup select
            self.INPUTS.append(self.BOT_SOCKET)
            self.MESSAGES[self.BOT_SOCKET] = queue.Queue()

            self.CONNECTED_SOCKET = True

        except Exception as e:
            print("ERROR: " + str(e))
            self.CONNECTED_SOCKET = False

        print("Connected to server!")

        return


    def send_msg(self, data):
        """ Function to send message to a socket """
        
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

            elif line[1] == ":CLOSING":
                self.CONNECTED_SERVER = False

            # respond to ping
            elif line[0] == "PING" and not self.PONG:
                self.send_msg("PONG " + line[1] + "\n")

                print("Sent ping")

            # check if collecting status
            elif self.STATE == "status":
                if line[2] == ("edelControl" + str(self.NICK_COUNT)) and line[-1] == self.SECRET:
                    self.STATUS.append(line[3][1:])

            # check if collecting status
            elif self.STATE == "move":
                if line[2] == ("edelControl" + str(self.NICK_COUNT)) and line[-1] == self.SECRET:
                    bot = line[0].split(":")[1].split("!")[0]
                    result = line[6]

                    self.MOVE.append((bot, result))

            # check if collecting status
            elif self.STATE == "shutdown":
                if line[2] == ("edelControl" + str(self.NICK_COUNT)) and line[-1] == self.SECRET:
                    self.SHUTDOWN_ARRY.append((line[3][1:], "successful"))

            # check if collecting status
            elif self.STATE == "attack":
                if line[2] == ("edelControl" + str(self.NICK_COUNT)) and line[-1] == self.SECRET:
                    bot = line[0].split(":")[1].split("!")[0]
                    result = line[6]

                    self.ATTACK.append((bot, result))
                    
        # finalizing print
        if self.STATE == "status":
            self.status()
        
        elif self.STATE == "move":
            self.migrate()

        elif self.STATE == "attack":
            self.attack()

        elif self.STATE == "shutdown":
            self.shutdown()

        self.STATE = None
            

    def handshake(self):
        """ Send the username """
        
        try:
            # send the NICk
            msg = "NICK edelControl" + str(self.NICK_COUNT) + "\n"
            self.send_msg(msg)

            # send the USER
            msg = "USER edelControl" + str(self.NICK_COUNT) + " * * :Edel Altares\n"
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


    def attack(self):
        """ Perform an attack """
        count_y = 0
        count_n = 0

        for bot in self.ATTACK:
            print(bot[0] + " " + bot[1])

            if "success" in bot[1]:
                count_y +=1
            else:
                count_n +=1

        print("Bots attacked: " + str(count_y))
        print("Bots failed: " + str(count_n))

        self.ATTACK = []


        return


    def migrate(self):
        """ Migrate to a different IRC server """
        count_y = 0
        count_n = 0

        for bot in self.MOVE:
            print(bot[0] + " " + bot[1])

            if "success" in bot[1]:
                count_y +=1
            else:
                count_n +=1

        print("Bots moved: " + str(count_y))
        print("Bots failed: " + str(count_n))

        self.MOVE = []

        return


    def shutdown(self):
        """ Shutdown the bot """
        count_y = 0
        count_n = 0

        for bot in self.SHUTDOWN_ARRY:
            print(bot[0] + " " + bot[1])

            if "success" in bot[1]:
                count_y +=1
            else:
                count_n +=1

        print("Bots shut down: " + str(count_y))
        print("Bots failed: " + str(count_n))


        self.SHUTDOWN_ARRY = []

        return


    def status(self):
        """ Report status """

        for bot in self.STATUS:
            print(bot)

        print("TOTAL BOTS: " + str(len(self.STATUS)))

        self.STATUS = []

        return


    def input(self):
        """ Get input from user """

        while True:
            if self.CONNECTED_SERVER and self.CONNECTED_SOCKET:
                cmd = input("")

                if cmd == "status":
                    print("STATUS command issued")

                    # send message to channgel
                    msg = "PRIVMSG #" + self.CHANNEL + " :status " + self.SECRET + "\n"
                    self.send_msg(msg)

                    self.STATE = "status"

                elif cmd == "shutdown":
                    print("SHUTDOWN command issued")

                    # send message to channgel
                    msg = "PRIVMSG #" + self.CHANNEL + " :shutdown " + self.SECRET + "\n"
                    self.send_msg(msg)

                    self.STATE = "shutdown"

                elif cmd == "quit":
                    print("QUIT command issued")
                    print("Terminating")

                    os._exit(1)

                elif "attack" in cmd:
                    print("ATTACK command issued")

                    # send message to channgel
                    msg = "PRIVMSG #" + self.CHANNEL + " :" + cmd + " " + self.SECRET + "\n"
                    self.send_msg(msg)

                    self.STATE = "attack"

                elif "move" in cmd:
                    print("MOVE command issued")

                    # send message to channgel
                    msg = "PRIVMSG #" + self.CHANNEL + " :" + cmd + " " + self.SECRET + "\n"
                    self.send_msg(msg)

                    self.STATE = "move"

                else:
                    print("Invalid command")
            

    def run(self):
        cmd_input = threading.Thread(target=self.input).start()

        while True:
            readable, writable, exceptable = select.select(self.INPUTS, self.INPUTS, [])

            for socket in readable:

                if not self.STATE is None:
                    time.sleep(5)

                socket.settimeout(5)
                data = socket.recv(1024)
                socket.settimeout(None)

                # there is data to be received
                if data:

                    # check the data
                    data = data.decode("utf-8")

                    # 
                    self.check_data(data)

                    # register on server
                    if not self.CONNECTED_SERVER:
                        self.handshake()

                    # join a channel
                    if self.CONNECTED_SERVER and not self.JOINED:
                        self.join()

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

                    continue

                else:
                    # send the msg
                    socket.send(next_msg)


def run():
    """ Run the controller """

    conBot = Bot()

    # get parsed arguments
    conBot.parse()

    try:
        while True:
            print("Connecting...")
            conBot.setup()
            
            # check if connected
            if conBot.CONNECTED_SOCKET:
                print("Running...")
                conBot.run()

            else:
                # wait 5 seconds before reconnecting
                print("Attempting reconnection...")
                time.sleep(5)

    except Exception as e:
        print("ERROR: " + str(e))


# run the program
if __name__ == "__main__":
    
    try:
        run()
    except KeyboardInterrupt:    
        sys.exit(0)
