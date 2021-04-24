from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

subject = "An email with attachment from Python"
body = "This is an email with attachment sent from Python"
sender_email = "computer.net.3000@gmail.com"
receiver_email = "gdra136@gmail.com"
password = 'quanghuy1234'

import socket
import ssl
import base64


def send_email(sender_email, password, receiver_email, msg, mailserver='smtp.gmail.com'):
    endmsg = "\r\n.\r\n"
    # Choose a mail server (e.g. Google mail server) and call it mailserver

    # Create socket called clientSocket and establish a TCP connection with mailserver
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    clientSocket.connect((mailserver, 587))
    recv = clientSocket.recv(1024)
    print(recv)
    if recv[:3] != '220':
        print('220 reply not received from server.')

    # Send HELO command and print server response.
    command = 'HELO Alice\r\n'
    heloCommand = command.encode()
    clientSocket.send(heloCommand)
    recv1 = clientSocket.recv(1024)
    print(recv1)

    if recv1[:3] != '250':
        print('250 reply not received from server.')

    # Request an encrypted connection

    command = 'STARTTLS\r\n'.encode()
    clientSocket.send(command)
    recv = clientSocket.recv(1024).decode()
    print(recv)

    if recv[:3] != '220':
        print('220 reply not received from server')

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
        print('334 reply not received from server')

    clientSocket.send(email)
    recv1 = clientSocket.recv(1024).decode()
    print(recv1)

    if recv1[:3] != '334':
        print('334 reply not received from server')

    clientSocket.send(password)
    recv1 = clientSocket.recv(1024).decode()
    print(recv1)
    if recv1[:3] != '235':
        print('235 reply not received from server')

    # Send MAIL FROM command and print server response.
    clientSocket.send("MAIL FROM: <{}>\r\n".format(sender_email).encode())
    recv2 = clientSocket.recv(1024).decode()
    if recv2[:3] != '250':
        print('250 reply not received from server.')

    # Send RCPT TO command and print server response.
    clientSocket.send("RCPT TO: <{}>\r\n".format(receiver_email).encode())
    recv2 = clientSocket.recv(1024).decode()
    print(recv2)

    # Send DATA command and print server response.
    clientSocket.send("DATA\r\n".encode())
    recv2 = clientSocket.recv(1024).decode()
    print(recv2)

    # Send data
    clientSocket.send(msg.encode())

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

    print('Mail sent and connection closed')


def create_message(subject, body, sender_email, receiver_email, password, filename="img.jpeg", return_text=True):
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # In same directory as script

    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
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
    return message


# Log in to server using secure context and send email
text = create_message(subject, 'this is another sample', sender_email, receiver_email, password)
# print(text)
# context = ssl.create_default_context()
# with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
#     server.login(sender_email, password)
#     server.sendmail(sender_email, receiver_email, text)

send_email(sender_email, password, receiver_email, text)
