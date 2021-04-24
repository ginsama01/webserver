from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import socket
import ssl
import base64

subject = "An email with attachment from Python"
body = "This is an email with attachment sent from Python"
file = "test.png"
sender_email = "computer.net.3000@gmail.com"
receiver_email = "ginsama2001@gmail.com"
password = 'quanghuy1234'
mailserver = ('smtp.gmail.com', 587)


def send_email(sender_email, password, receiver_email, msg):
    endmsg = "\r\n.\r\n"
    # Choose a mail server (e.g. Google mail server) and call it mailserver

    # Create socket called clientSocket and establish a TCP connection with mailserver
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    clientSocket.connect(mailserver)
    recv = clientSocket.recv(1024).decode()
    print('After connect: ' + recv)
    if recv[:3] != '220':
        print('220 reply not received from server.')

    # Send HELO command and print server response.
    command = 'HELO Alice\r\n'    #Gui loi chao 
    heloCommand = command.encode()
    clientSocket.send(heloCommand)
    recv1 = clientSocket.recv(1024).decode()
    print('After send HELO: ' + recv1)
    if recv1[:3] != '250':
        print('250 reply not received from server.')

    # Request an encrypted connection
    #Yeu cau thiet lap 1 ket noi an toan (duoc ma hoa)
    command = 'STARTTLS\r\n'.encode()
    clientSocket.send(command)
    recv = clientSocket.recv(1024).decode()
    print('After send STARTTLS: ' + recv)
    if recv[:3] != '220':
        print('220 reply not received from server')

    # Encrypt the socket
    clientSocket = ssl.wrap_socket(clientSocket) #boc trong 1 ket noi an toan   

    # email and password for authentication
    email = (base64.b64encode(sender_email.encode()) + ('\r\n').encode())
    password = (base64.b64encode(password.encode()) + ('\r\n').encode())

    # Authentication
    clientSocket.send('AUTH LOGIN \r\n'.encode())
    recv1 = clientSocket.recv(1024).decode()
    print('After send login request: ' + recv1)
    if recv1[:3] != '334':
        print('334 reply not received from server')

    clientSocket.send(email)
    recv1 = clientSocket.recv(1024).decode()
    print('After send usermail: ' + recv1)
    if recv1[:3] != '334':
        print('334 reply not received from server')

    clientSocket.send(password)
    recv1 = clientSocket.recv(1024).decode()
    print('After send password: ' + recv1)
    if recv1[:3] != '235':
        print('235 reply not received from server')

    # Send MAIL FROM command and print server response.
    clientSocket.send("MAIL FROM: <{}>\r\n".format(sender_email).encode()) #dia chi mail gui
    recv2 = clientSocket.recv(1024).decode()
    print('After send MAIL FROM: ' + recv2)
    if recv2[:3] != '250':
        print('250 reply not received from server.')

    # Send RCPT TO command and print server response.
    clientSocket.send("RCPT TO: <{}>\r\n".format(receiver_email).encode()) #dia chi mail nhan
    recv2 = clientSocket.recv(1024).decode()
    print('After send RCPT TO: ' + recv2)
    if recv2[:3] != '250':
        print('250 reply not received from server.')


    # Send DATA command and print server response.
    clientSocket.send("DATA\r\n".encode()) #Danh dau bat dau gui message
    recv2 = clientSocket.recv(1024).decode()
    print('After send DATA: ' + recv2)
    if recv2[:3] != '354':
        print('354 reply not received from server.')

    # Send data
    clientSocket.send(msg.encode())

    # Message ends with a single period.
    clientSocket.send(endmsg.encode()) #Ket thuc message
    recv2 = clientSocket.recv(1024).decode()
    print('After send end message: ' + recv2)
    if recv2[:3] != '250':
        print('250 reply not received from server.')

    # Send QUIT command and get server response.
    clientSocket.send("QUIT\r\n".encode())   #Gui yeu cau ket thuc
    recv2 = clientSocket.recv(1024).decode()
    print('After send QUIT: ' + recv2)
    if recv2[:3] != '221':
        print('221 reply not received from server.')

    # Close connection with client socket
    clientSocket.close()

    print('Mail sent and connection closed')


def create_message(subject, body, sender_email, receiver_email, password, filename, return_text=True):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mess emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # In same directory as script

    # Open file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream") #Dinh dang tap tin nhi phan
        part.set_payload(attachment.read()) #Add data

    # Encode file in ASCII characters to send by email
    encoders.encode_base64(part)

    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        "attachment; filename= {filename}",
    )
    #Them header cho tep dinh kem + dinh dang mac dinh hien thi cho file
    #Neu khong trinh duyet web se bat buoc tai xuong tep thay vi hien thi truc tiep

    # Add attachment to message and convert message to string
    message.attach(part)
    if return_text:
        return message.as_string()
    return message


text = create_message(subject, body, sender_email, receiver_email, password, file)
send_email(sender_email, password, receiver_email, text)