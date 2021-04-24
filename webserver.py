from socket import *
import sys
from threading import Thread


class ServeThread(Thread):
    def __init__(self, socket, connectionSocket, addr):
        Thread.__init__(self)
        self.serverSocket = socket
        self.connectionSocket = connectionSocket
        self.addr = addr

    def run(self):
        connectionSocket, addr = self.connectionSocket, self.addr
        print("Serving {}".format(addr))
        try:
            message = connectionSocket.recv(1024)
            filename = message.split()[1]
            print(message)
            print(filename[1:])
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
        while True:
            print('Ready to serve...')
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
