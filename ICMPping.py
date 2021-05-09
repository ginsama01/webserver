from socket import *
import os, sys, struct, time, select, binascii
import logging, json

ICMP_ECHO_REQUEST = 8
# load bảng tra cứu lỗi từ file
ERROR_CODES = json.load(open(os.path.dirname(__file__) + '/icmp_error_code/error_codes.json'))


def split_4(dec_ip, base=8):
    """ dịch ip dec -> dạng chuẩn"""
    b = bin(dec_ip)[2:]
    rs = []
    while len(b) > 0:
        rs.append(str(int(b[:base], 2)))
        b = b[base:]
    return '.'.join(rs)



def header2dict(names, struct_format, data):
    """ convert dữ liệu về dạng dic với format cho trước """
    unpacked_data = struct.unpack(struct_format, data)
    return dict(zip(names, unpacked_data))


class Report:
    """ đây là bản báo cáo về ping"""
    RTT_MEM = []
    MAX_SIZE = 10000000
    SENDED = 0
    LOST = 0
    RECIEVED = 0

    def update_report(self, delay):
        """ update các thông số trong báo cáo """
        self.SENDED += 1
        if type(delay) is not str:
            self.RECIEVED += 1
            self.RTT_MEM.append(delay)
        if len(self.RTT_MEM) >= self.MAX_SIZE:
            del self.RTT_MEM[0]

    def report(self):
        """ thông báo ra màn hình kết quả thống kê """
        print(
            "\nPing statistics for 142.250.204.142:\n    Packets: Sent = {}, Received = {}, Lost = {} ({}% loss),\n".format(
                self.SENDED, self.RECIEVED, self.SENDED - self.RECIEVED,
                                            (self.SENDED - self.RECIEVED) / self.SENDED * 100))
        print(
            'Approximate round trip times in milli-seconds:\n    Minimum = {}ms, Maximum = {}ms, Average = {}ms\n'.format(
                int(min(self.RTT_MEM) * 1000), int(1000 * max(self.RTT_MEM)),
                int(sum(self.RTT_MEM) / len(self.RTT_MEM) * 1000)))


def checksum(str_):
    # In this function we make the checksum of our packet
    str_ = bytearray(str_)
    csum = 0
    countTo = (len(str_) // 2) * 2
    for count in range(0, countTo, 2):
        thisVal = str_[count + 1] * 256 + str_[count]
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
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []:  # Timeout
            print("Request timed out.")
            return "Request timed out."
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024)
        # Fill in start
        # Fetch the ICMP header from the IP packet
        icmpHeader = recPacket[20:28]
        icmpType, code, mychecksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

        if type != 8 and packetID == ID:
            # nếu trả về ip tiến trình hiện tại
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            ip_header = header2dict(
                names=[
                    "version", "type", "length",
                    "id", "flags", "ttl", "protocol",
                    "checksum", "src_ip", "dest_ip"
                ],
                struct_format="!BBHHHBBHII",
                data=recPacket[:20]
            ) # dịch header sang dạng dic để lấy được thông tin
            print(
                'Reply from {}: bytes={} time={}ms TTL={}'.format(split_4(ip_header['src_ip']), 32,
                                                                  int((timeReceived - timeSent) * 1000),
                                                                  ip_header['ttl']))
            return timeReceived - timeSent
        # nếu xuất hiện lỗi, sẽ dựa vào bảng tra cứu vầ in ra lỗi
        if str(icmpType) in ERROR_CODES:
            if str(code) in ERROR_CODES[str(icmpType)]:
                print(ERROR_CODES[str(icmpType)][str(code)])
        # Fill in end
        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return "Request timed out."


def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    # Make a dummy header with a 0 checksum# struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    data = struct.pack("d", time.time())
    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)
    # Get the right checksum, and put in the header
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    packet = header + data
    mySocket.sendto(packet, (destAddr, 1))  # AF_INET address must be tuple, not str
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.


def doOnePing(destAddr, timeout):
    icmp = getprotobyname("icmp")
    # SOCK_RAW is a powerful socket type. For more details: http://sockraw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)
    myID = os.getpid() & 0xFFFF  # Return the current process i
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
    mySocket.close()
    return delay


def ping(host, timeout=1, report=True, echo=4):
    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost
    dest = gethostbyname(host)
    print("Pinging " + dest + " using Python:")
    print("")
    if report:
        a = Report()
    # Send ping requests to a server separated by approximately one second
    while echo > 0:
        echo -= 1
        delay = doOnePing(dest, timeout)
        if report:
            # update kết quả thống kê
            a.update_report(delay)
        time.sleep(1)  # one second
    if report:
        # in báo cáo thống kê cuối ra màn hình
        a.report()
    return delay


if __name__ == '__main__':
    ping("google.com")
