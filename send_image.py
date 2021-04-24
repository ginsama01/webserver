from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import socket
import ssl
import base64

subject = "An email with attachment from Python"
body = "This is an email with attachment sent from Python"
sender_email = "computer.net.3000@gmail.com"
receiver_email = "gdra136@gmail.com"
password = 'quanghuy1234'




def send_email(sender_email, password, receiver_email, msg, mailserver='smtp.gmail.com', port=587):
    """
    send an byte-formatted message to a mail server
    :param sender_email: address of sender
    :param password: password for signing in sender_email
    :param receiver_email: address of receiver
    :param msg: byte-formatted message
    :param mailserver: address of mail server
    :param port: port number of mail server
    :return: a status :0 ~ successfully send
    """
    endmsg = "\r\n.\r\n"
    # Choose a mail server (e.g. Google mail server) and call it mailserver

    # Create socket called clientSocket and establish a TCP connection with mailserver
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    clientSocket.connect((mailserver, port))
    recv = clientSocket.recv(1024)
    print(recv)
    if recv[:3] != '220':
        logging.error('220 reply not received from server.')

    # Send HELO command and print server response.
    command = 'HELO Alice\r\n'
    heloCommand = command.encode()
    clientSocket.send(heloCommand)
    recv1 = clientSocket.recv(1024)
    print(recv1)

    if recv1[:3] != '250':
        logging.error('250 reply not received from server.')

    # Request an encrypted connection

    command = 'STARTTLS\r\n'.encode()
    clientSocket.send(command)
    recv = clientSocket.recv(1024).decode()
    print(recv)

    if recv[:3] != '220':
        logging.error('220 reply not received from server')

    # Encrypt the socket
    clientSocket = ssl.wrap_socket(clientSocket)

    # email and password for authentication
    email = (base64.b64encode(sender_email.encode()) + ('\r\n').encode())
    password = (base64.b64encode(password.encode()) + ('\r\n').encode())

    # Authentication
    clientSocket.send('AUTH LOGIN \r\n'.encode())
    recv1 = clientSocket.recv(1024).decode()
    print(recv1)
    if recv1[:3] != '334':
        logging.error('334 reply not received from server')

    clientSocket.send(email)
    recv1 = clientSocket.recv(1024).decode()
    print(recv1)

    if recv1[:3] != '334':
        logging.error('334 reply not received from server')

    clientSocket.send(password)
    recv1 = clientSocket.recv(1024).decode()
    print(recv1)
    if recv1[:3] != '235':
        logging.error('235 reply not received from server')

    # Send MAIL FROM command and print server response.
    clientSocket.send("MAIL FROM: <{}>\r\n".format(sender_email).encode())
    recv2 = clientSocket.recv(1024).decode()
    if recv2[:3] != '250':
        logging.error('250 reply not received from server.')

    # Send RCPT TO command and print server response.
    clientSocket.send("RCPT TO: <{}>\r\n".format(receiver_email).encode())
    recv2 = clientSocket.recv(1024).decode()
    print(recv2)

    # Send DATA command and print server response.
    clientSocket.send("DATA\r\n".encode())
    recv2 = clientSocket.recv(1024).decode()
    print(recv2)

    # Send data
    clientSocket.send(msg)

    # Message ends with a single period.
    clientSocket.send(endmsg.encode())
    recv2 = clientSocket.recv(1024).decode()
    print(recv2)

    # Send QUIT command and get server response.
    clientSocket.send("QUIT\r\n".encode())
    recv2 = clientSocket.recv(1024).decode()
    print(recv2)

    # Close connection with client socket
    clientSocket.close()

    return 0


def create_message(subject, body, sender_email, receiver_email, filenames=["img.jpeg"], return_text=False):
    """
    create a email message including text and file content.
    :param subject: subject of email
    :param body: textual data of email
    :param sender_email: address of sender
    :param receiver_email: address of receiver
    :param filenames: name of attached files
    :param return_text: whether return value is in textual (ascii) format or bytes format
    :return: str or bytes
    """
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email

    message.attach(MIMEText(body, "plain"))
    for filename in filenames:
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)
            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {filename}",
            )
            # Add attachment to message and convert message to string
            message.attach(part)
    if return_text:
        return message.as_string()
    return message.as_bytes()


text = create_message(subject='wibu', body='this is your love', sender_email=sender_email,
                      receiver_email=receiver_email, return_text=False, filenames=['img.jpeg'])

send_email(sender_email, password, receiver_email, text)
