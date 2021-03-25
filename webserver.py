from socket import *
import sys
from threading import Thread
import logging
import os


def get_logger(name=None):
    name = os.path.basename(name)
    name = os.path.splitext(name)[0]
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-18s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger
logger = get_logger(__file__)


class ServeThread(Thread):
    def __init__(self, socket, connectionSocket, addr):
        Thread.__init__(self)
        self.serverSocket = socket
        self.connectionSocket = connectionSocket
        self.addr = addr

    def run(self):
        connectionSocket, addr = self.connectionSocket, self.addr
        try:
            message = connectionSocket.recv(1024)
            logger.info('message received : \n{}\nFROM\n{}'.format(message.decode('utf-8'),addr))

            filename = message.split()[1]
            f = open(__file__ + "\..\\" + filename[1:].decode('utf-8'), encoding='utf-8')
            outputdata = f.read(1024)
            # Send one HTTP header line into socket
            connectionSocket.send('\nHTTP/1.1 200 OK\r\n'.encode())

            # Send the content of the requested file to the client
            for i in range(0, len(outputdata)):
                connectionSocket.send(outputdata[i].encode())
            connectionSocket.send("\r\n".encode())

            connectionSocket.close()

        except IOError:
            # Send HTTP response message for file not found
            connectionSocket.send("\nHTTP/1.1 404 Not Found\r\n".encode())

            connectionSocket.close()


class ServerManager(Thread):
    def __init__(self, sv):
        Thread.__init__(self)
        self.serverSocket = sv
        self.serve_threads={}

    def run(self):
        logger.info('Ready to serve...')
        while True:
            connectionSocket, addr = self.serverSocket.accept()
            if addr not in self.serve_threads:
                self.serve_threads[addr] = ServeThread(self.serverSocket, connectionSocket, addr)
            self.serve_threads[addr].run()

        serverSocket.close()
serverPort = 1234
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)
a = ServerManager(serverSocket)
a.run()
