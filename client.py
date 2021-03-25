from socket import *
import sys

#Check input
if len(sys.argv) != 4:
    print ("Your command is not right. Please be in this format:client.py server_host server_port filename")
    sys.exit(0)

#Connect to server from input
serverName = str(sys.argv[1])
serverPort = int(sys.argv[2])
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName,serverPort))

#Send request to server
request = "\nGET /" + str(sys.argv[3]) + " HTTP/1.1\n\n"
clientSocket.send(request.encode())

#Receive response from server
modifiedSentence = clientSocket.recv(1024)
print ('From Server:')
while True:
    if not modifiedSentence:
        break
    print(modifiedSentence.decode())
    modifiedSentence = clientSocket.recv(1024)

#Close client socket
clientSocket.close()