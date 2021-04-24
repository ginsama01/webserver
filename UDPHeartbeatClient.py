from socket import *
import sys
import time
import random

#Check input
if len(sys.argv) != 3:
    print ("Your command is not right. Please be in this format:UDPHeartbeatClient.py server_host server_port")
    sys.exit(0)

#Connect to server from input
serverName = str(sys.argv[1])
serverPort = int(sys.argv[2])
address = (serverName, serverPort)
clientSocket = socket(AF_INET, SOCK_DGRAM)

# To set waiting time of one second for reponse from server


stt = 1
while stt < 11:
    time.sleep(2)
    start = time.time() # Lay time hien tai
    message = 'Ping ' + str(stt) + ' ' + time.ctime(start)
     # Generate random number in the range of 0 to 10
    rand = random.randint(0, 10)
    if rand < 3:
        stt = stt + 1
        continue

    clientSocket.sendto(message.encode(), address)
    print('Sent: ' + message)
    modifiedMessage = clientSocket.recvfrom(1024)
    decodeMessage = modifiedMessage[0].decode() # [0] la message [1] la address cua server
    print('Receive: ' + decodeMessage + '\n') 
    

    if decodeMessage.startswith("PING"):  #Neu mess dung thu tu
        stt = stt + 1
    else:   #Neu sai thu tu
        splitMessage = decodeMessage.split()
        stt = int(splitMessage[3])        #Go back N - gui lai tu goi bi sai thu tu
        
clientSocket.close()