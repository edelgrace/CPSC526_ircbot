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
    SECRET = None
    BOT_SOCKET = None

    BOT_COUNT = 0
    NICK_COUNT = 0

    MESSAGES = {}
    INPUTS = []

    CONNECTED_SOCKET = False
    CONNECTED_SERVER = False
    JOINED = False

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
        
        # get parsed arguments
        self.parse()

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
        
        print("Sending: " + data)

        try:
            self.BOT_SOCKET.send(data.encode())

        except Exception as e:
            print(str(e))


    def check_data(self, data):
        """ Check the data """
        data = data.split("\r\n")


        for line in data:

            line = line.split()

            if len(line) < 2:
                continue

            # check if bot logged onto IRC server
            if line[1] == "433":
                self.NICK_COUNT += 1
                self.CONNECTED_SERVER = False
                
            # join server successfully
            elif line[1] == "001":
                self.BOT_COUNT += 1
                self.CONNECTED_SERVER = True
                print(str(self.BOT_COUNT))

            # join channel successfully
            elif line[1] == "JOIN":
                print("Joined channel")
                self.JOINED = True


    def close_socket(self, sckt):
        """ Close a connection """
        print("Socket closed")
        # remove from outputs
        if sckt in self.OUTPUTS:
            self.OUTPUTS.remove(sckt)
        
        # remove from inputs
        self.INPUTS.remove(sckt)

        # close the socket
        sckt.close()


    def handshake(self):
        """ Send the username """
        
        try:
            # send the NICk
            msg = "NICK edel" + str(self.NICK_COUNT) + "\n"
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


    def attack(self):
        """ Perform an attack """

        return


    def migrate(self, server):
        """ Migrate to a different IRC server """

        return


    def shutdown(self):
        """ Shutdown the bot """

        return


    def status(self):
        """ Report status """

        return


    def run(self):
        while True:
            readable, writable, exceptable = select.select(self.INPUTS, self.INPUTS, [])

            for socket in readable:

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
                    if self.CONNECTED_SERVER and self.JOINED:
                        self.cmds()

                # connection was closed
                else:
                    self.CONNECTED_SOCKET = False

            for socket in writable:
                try:
                    # get the msg
                    next_msg = self.MESSAGES[socket].get_nowait()

                except queue.Empty:
                    continue

                else:
                    # send the msg
                    socket.send(next_msg)

def run():
    """ Run the client """
    bot = Bot()

    while True:
        bot.setup()
        
        # check if connected
        if bot.CONNECTED_SOCKET:
            bot.run()

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
