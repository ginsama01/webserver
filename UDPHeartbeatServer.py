from socket import *
import time

# Create a UDP socket
# Notice the use of SOCK_DGRAM for UDP packets
serverSocket = socket(AF_INET, SOCK_DGRAM)
# Assign IP address and port number to socket
serverSocket.bind(('', 12000))
print("Started UDP server on port 12000")
serverSocket.settimeout(6)

messageStt = 0
while True:
    try:
        # Receive the client packet along with the address it is coming from
        message, address = serverSocket.recvfrom(1024)
        print("Receive: " + message.decode())
        splitMessage = message.decode().split(' ', 2) # Message co dang Ping Stt Time
    
        messageTime = time.strptime(splitMessage[2], "%a %b %d %H:%M:%S %Y") #convert to struct-time
        messageTime = time.mktime(messageTime) #convert struct-time to ticks
        currentTime = time.time()
        print("Different Time: " + str(currentTime - messageTime) + " seconds\n")
        if int(splitMessage[1]) != messageStt + 1: #Neu nhan mess ko dung thu tu
            responseMessage = "Don't receive message " + str(messageStt + 1)
            serverSocket.sendto(responseMessage.encode(), address)
        else:
            serverSocket.sendto(message.upper(), address)
            messageStt = messageStt + 1
    except timeout:
        print("Requested time out. Maybe client has stopped\n Server closed!")
        break

serverSocket.close()
