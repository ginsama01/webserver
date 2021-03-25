from socket import *
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

    def run(self, conn):
        logger.info("Connected with {}:{}".format(conn.getpeername()[0], conn.getpeername()[1]))
        try:
            message = conn.recv(1024)
            logger.info('message received : \n{}\n'.format(message.decode('utf-8')))

            filename = message.split()[1]
            f = open(__file__ + "\..\\" + filename[1:].decode('utf-8'), encoding='utf-8')
            outputdata = f.read(1024)
            # Send one HTTP header line into socket
            conn.send('\nHTTP/1.1 200 OK\r\n'.encode())

            # Send the content of the requested file to the client
            for i in range(0, len(outputdata)):
                conn.send(outputdata[i].encode())
            conn.send("\r\n".encode())

            conn.close()

        except Exception:
            # Send HTTP response message for file not found
            conn.send("\nHTTP/1.1 404 Not Found\r\n".encode())
            conn.close()


class ServerManager(Thread):
    def __init__(self, sv):
        Thread.__init__(self)
        self.serverSocket = sv
        self.serve_threads = {}

    def run(self):
        logger.info('Ready to serve...')
        while True:
            conn, addr = self.serverSocket.accept()
            """
            Khi có một kết nối với server, nó socket server sẽ chấp nhận, tạo một connection mới,
            đẩy nó cho một thread xử lý, và tiếp tục quay lại chờ đợi.
            Điều này liệu đã giải quyết được vấn đề các truy cập xuất hiện cùng lúc ?
            """
            if addr not in self.serve_threads:
                self.serve_threads[addr] = ServeThread()
            self.serve_threads[addr].run(conn)
            """
            Mỗi thread sẽ phục vụ riêng 1 tổ hợp (ip_client và port_client)
            ̣https://docs.python.org/3/library/socket.html
            """
        serverSocket.close()


# if __name__ == 'main':
serverPort = 1234
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5) # hình như set như thế này để nó chấp nhập được 5 connection
a = ServerManager(serverSocket)
a.run()
