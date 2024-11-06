import socket
import os

HOST = 'localhost'
PORT = 18000

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))


def menu():
    print("\nPlease select one of the following options:")
    print("1. Get a report of the chatroom from the server.")
    print("2. Request to join the chatroom.")
    print("3. Quit the program.")
    choice = input("Enter choice: ")
    return choice


def get_report():
    client_socket.send("REPORT_REQUEST=1".encode('ascii'))
    response = client_socket.recv(1024).decode('ascii')
    print(response)


def join_chatroom():
    username = input("Please enter a username: ")
    client_socket.send(f"JOIN_REQUEST={username}".encode('ascii'))
    response = client_socket.recv(1024).decode('ascii')
    print(response)

    if "JOIN_ACCEPT_FLAG=1" in response:
        chat_history = response.split("PAYLOAD=")[1]
        print(f"Welcome to the chatroom! Here's the history:\n{chat_history}")


def quit_chatroom():
    client_socket.send("QUIT_REQUEST=1".encode('ascii'))
    response = client_socket.recv(1024).decode('ascii')
    print(response)


def send_message():
    message = input("Enter your message: ")
    client_socket.send(message.encode('ascii'))


def upload_file():
    filename = input("Please enter the file path and name: ")
    if os.path.exists(filename):
        client_socket.send(f"ATTACHMENT={filename}".encode('ascii'))
        with open(filename, 'rb') as file:
            data = file.read(1024)
            while data:
                client_socket.send(data)
                data = file.read(1024)
        print(f"File {filename} uploaded successfully!")
    else:
        print("File not found!")


while True:
    choice = menu()

    if choice == '1':
        get_report()
    elif choice == '2':
        join_chatroom()
    elif choice == '3':
        quit_chatroom()
        break
    elif choice == 'a':
        upload_file()
    else:
        print("Invalid choice.")
