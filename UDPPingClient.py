from socket import *
import sys
import time

#Check input
if len(sys.argv) != 3:
    print ("Your command is not right. Please be in this format:UDPPingClient.py server_host server_port")
    sys.exit(0)

#Connect to server from input
serverName = str(sys.argv[1])
serverPort = int(sys.argv[2])
address = (serverName, serverPort)
clientSocket = socket(AF_INET, SOCK_DGRAM)

# To set waiting time of one second for reponse from server
clientSocket.settimeout(1)

# Find max, min, average RTT, packet loss rate
RTTmax = 0
RTTmin = 1
RTTaverage = 0
packet = 10 

for i in range(1, 11):
    start = time.time() # Lay time hien tai
    message = 'Ping ' + str(i) + ' ' + time.ctime(start)
    try:
        clientSocket.sendto(message.encode(), address)
        print('Sent: ' + message)
        modifiedMessage = clientSocket.recvfrom(1024)
        print('Receive: ' + modifiedMessage[0].decode()) # [0] la message [1] la address cua server
        end = time.time()
        elapsed = end - start
        RTTmax = max(RTTmax, elapsed)
        RTTmin = min(RTTmin, elapsed)
        RTTaverage = RTTaverage + elapsed
        print("RTT: " + str(elapsed) + " seconds\n")
    except timeout:
        print("#" + str(i) + " Requested Time out\n")
        packet = packet - 1

print("RTTmin: " + str(RTTmin) + " seconds")
print("RTTmax: " + str(RTTmax) + " seconds")
print("RTTaverage: " + str(RTTaverage/packet) + " seconds")
print("Packet loss rate: " + str(packet / 10 * 100) + "%")
clientSocket.close()