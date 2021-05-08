from socket import *
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8

def checksum(str_):
    # In this function we make the checksum of our packet 
    str_ = bytearray(str_)
    csum = 0
    countTo = (len(str_) // 2) * 2

    for count in range(0, countTo, 2):
        thisVal = str_[count+1] * 256 + str_[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff

    if countTo < len(str_):
        csum = csum + str_[-1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(mySocket, ID, timeout, destAddr):
    timeLeft = timeout
    
    while 1:
        startedSelect = time.time()
        whatReady = select.select([mySocket], [], [], timeLeft) 
        #chỉ dùng tham số rlist -> có nghĩa là đợi cho đến khi sẵn sàng để đọc
        # Nếu quá timeout thì dừng
        #T ko hiểu cái select này lắm, ai explain cho phát?
        howLongInSelect = (time.time() - startedSelect) #thời gian đợi
        print(whatReady)
        if whatReady[0] == []: # Timeout
            return "0: Destination Network Unreachable"  #maybe cái này là op 2 ?

        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)

        icmpHeader = recPacket[20:28] 
        #Vì tiêu đề ICMP bắt đầu sau bit thứ 160 đến bit 224, tức là nó từ byte thứ 20 đến hết byte 27 
        icmpType, code, mychecksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)
        #lúc send pack nó vào thì giờ unpack ra, cấu trúc cũng tương tự.
        
        if icmpType == 0 and packetID == ID:
            bytesInDouble = struct.calcsize("d")  #tính số bytes của double để lấy ra
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0] #data chính là thời gian gửi
            return timeReceived - timeSent
        
            
        #Sao t không bao giờ thấy bị loss nhỉ ? 

        timeLeft = timeLeft - howLongInSelect
        
        if timeLeft <= 0:
            return "1: Destination Host Unreachable" #and đây là op 2?

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)

    myChecksum = 0
    # Make a dummy header with a 0 checksum.
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    #struct.pack(format, v1, v2, ...) là đóng gói v1, v2, ... theo định dạng trong format
    #Ở đây là đang đóng gói cái header, các kí tự thì b là kiểu signed char(1 bytes), 
    # H là unsigned short (2 bytes), h là signed short (2 bytes)
    data = struct.pack("d", time.time())
    #gửi gói tin là dấu thời gian, cũng đóng gói lại, d là double (8 bytes)
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    #tính trường checksum trên dữ liệu và header giả
    
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        myChecksum = htons(myChecksum) & 0xffff  #nếu là os darwin thì lấy 16 bit đầu
    #Convert 16-bit integers from host to network byte order.
    #htons là convert 16 bit từ thứ tự bytes máy chủ sang thứ tự bytes của network
    #khác nhau thế nào nhỉ ?
    else:
        myChecksum = htons(myChecksum)
    
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    #tạo lại header cập nhật checksum vừa tính
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str
    #Both LISTS and TUPLES consist of a number of objects
    #which can be referenced by their position number within the object

def doOnePing(destAddr, timeout):         
    icmp = getprotobyname("icmp")  #nhận một chuỗi giao thức như TCP , UDP hoặc ICMP và trả về hằng số 
                                   #liên quan cho giao thức được định nghĩa bởi mô-đun socket
    #Create Socket here
    
    mySocket = socket(AF_INET, SOCK_RAW, icmp) #tạo socket ipv4, chỉ biết SOCK_RAW là 1 socket type mạnh,
    #icmp là 1 số -> thể hiện loại protocol là icmp
    #Trong hệ điều hành, mọi process đều có một id, os.getpid() trả về ID của process hiện tại (PID)
    myID = os.getpid() & 0xFFFF  #Return the current process i  
    # & 0xFFFF là lấy 16 bit đầu, tương tự & 0xFF là lấy 8 bit đầu
    # nói chung là lấy 1 cái số ra làm ID của gói tin, i think so
    sendOnePing(mySocket, destAddr, myID) 
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)          

    mySocket.close()         
    return delay  

def ping(host, timeout=1):
    #dest = gethostbyname(host)  #trả về địa chỉ IP của máy chủ
    dest = "172.112.113.1"
    print ("Pinging " + dest + " using Python:")
    print ("")
    #Send ping requests to a server separated by approximately one second
    stt = 0
    total = 20    #đang tạm để ping 20 phát thôi để làm op1
    totalMessageReceived = 0
    RTTmax = 0
    RTTmin = 1
    RTTaverage = 0
    while stt < total:
        delay = doOnePing(dest, timeout)
        if type(delay) == float:
            print ("RTT: " + str(delay))
            totalMessageReceived = totalMessageReceived + 1
            RTTmax = max(RTTmax, delay)
            RTTmin = min(RTTmin, delay)
            RTTaverage = RTTaverage + delay
        else:
            print ("Error " + delay)
        time.sleep(1) # one second
        stt = stt + 1
    print("RTT max: " + str(RTTmax))
    print("RTT min: " + str(RTTmin))
    print("RTT average: " + str(RTTaverage/totalMessageReceived))
    print("Packet loss rate: " + str((total - totalMessageReceived)/total * 100) + "%")
    return delay

ping("toidicodedao.com")