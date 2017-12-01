# Edel Altares 1009872 Tutorial 2

import select
import socket
import os
import sys
import queue
import argparse
import time
import datetime

class Bot:
    HOSTNAME = None
    PORT = None
    CHANNEL = None
    SECRET = None
    BOT_SOCKET = None

    MESSAGES = {}
    OUTPUTS = []
    INPUTS = []
    CONNECTED = False


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
            self.BOT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.BOT_SOCKET.connect((self.HOSTNAME, self.PORT))
            
            self.INPUTS.append(self.BOT_SOCKET)
            self.OUTPUTS.append(self.BOT_SOCKET)

            self.MESSAGES[self.BOT_SOCKET] = queue.Queue()

        except Exception as e:
            sys.stderr.write("Error: " + str(e))
            sys.exit(0)

        # TODO

        return


    def send_msg(self, data, sckt):
        """ Function to send message to a socket """
        if not isinstance(data, (bytes, bytearray)):
            data = bytes(data, "utf-8")

        self.MESSAGES[sckt].put(data)

        # add to the outputs
        if sckt not in self.OUTPUTS:
            self.OUTPUTS.append(sckt)


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


    def handshake(self, sckt):
        """ Grab the username """

        # send the NICk
        msg = "NICK edel"
        self.send_msg(msg, sckt)

        # send the USER
        msg = "USER edel * * :Edel Altares"
        self.send_msg(msg, sckt)

        self.CONNECTED = True

        return


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
        """ Run the bot """

        if not self.CONNECTED:
            self.handshake()

        while self.INPUTS:

            readable, writable, error = select.select(self.INPUTS, self.OUTPUTS, [])

            print(len(readable))

            # go through inputs
            for sckt in readable:
                print("readable")
                print(len(readable))
                
                data = sckt.recv(1024)

                if data:
                    print(data)

                # no more data = close connection
                else: 
                    print("Close?")
                    self.close_socket(sckt)
    
            # go through outputs
            for sckt in writable:
                print("writable")
                print(len(writable))

                if not self.CONNECTED:
                    self.handshake(sckt)

                try:
                    # grab the next message
                    next_msg = self.MESSAGES[sckt].get_nowait()

                    print(next_msg)

                except queue.Empty:
                    self.OUTPUTS.remove(sckt)
                    
                else:
                    # send the message
                    sckt.send(next_msg)


def run():
    """ Run the client """
    bot = Bot()
    bot.setup()

    while True:
        bot.run()


# run the program
if __name__ == "__main__":
    
    try:
        run()
    except KeyboardInterrupt:    
        sys.exit(0)