from socket import *

serverPort = 1234
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
serverSocket.listen(1)

while True:
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()
    try:
        message = connectionSocket.recv(1024)
        print(message)
        filename = message.split()[1]
        f = open(filename[1:])
        outputdata = f.read()
        #Send one HTTP header line into socket
        connectionSocket.send('\nHTTP/1.1 200 OK\r\n'.encode())

        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)): 
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
 
        connectionSocket.close()
    
    except IOError:
        # Send HTTP response message for file not found
        connectionSocket.send("\nHTTP/1.1 404 Not Found\r\n".encode())

        connectionSocket.close()

serverSocket.close()