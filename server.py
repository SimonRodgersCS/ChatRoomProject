import socket
import threading
import time
import os

# Constants and configurations
HOST = 'localhost'
PORT = 18000
MAX_USERS = 3
users = {}  # {username: (address, port)}
history = []  # [(timestamp, username, message)]


# Handle incoming client requests
def handle_client(client_socket, address):
    username = None
    try:
        # Receive JOIN_REQUEST or any other message
        while True:
            message = client_socket.recv(1024).decode('ascii')
            if message.startswith("JOIN_REQUEST"):
                # Check if chatroom is full or username exists
                if len(users) >= MAX_USERS:
                    reject_message = "JOIN_REJECT_FLAG=1 PAYLOAD=The server rejects the join request. The chatroom has reached its maximum capacity."
                    client_socket.send(reject_message.encode('ascii'))
                else:
                    username = message.split('=')[1]  # Example: "JOIN_REQUEST=XYZ"
                    if username in users:
                        reject_message = f"JOIN_REJECT_FLAG=1 PAYLOAD=The server rejects the join request. Another user is using this username."
                        client_socket.send(reject_message.encode('ascii'))
                    else:
                        # Accept the join request
                        users[username] = address
                        history.append(
                            (time.strftime("%Y-%m-%d %H:%M:%S"), 'server', f"{username} joined the chatroom"))

                        join_accept_msg = f"JOIN_ACCEPT_FLAG=1 USERNAME={username} PAYLOAD={history}"
                        client_socket.send(join_accept_msg.encode('ascii'))
                        # Broadcast the new user announcement
                        broadcast(f"NEW_USER_FLAG=1 USERNAME={username} PAYLOAD={username} joined the chatroom.")
                        break

            elif message.startswith("QUIT_REQUEST"):
                if username:
                    users.pop(username)
                    history.append((time.strftime("%Y-%m-%d %H:%M:%S"), 'server', f"{username} left the chatroom"))
                    quit_message = f"QUIT_ACCEPT_FLAG=1 USERNAME={username} PAYLOAD={username} left the chatroom."
                    client_socket.send(quit_message.encode('ascii'))
                    broadcast(f"QUIT_ACCEPT_FLAG=1 USERNAME={username} PAYLOAD={username} left the chatroom.")
                    break

            elif message.startswith("REPORT_REQUEST"):
                report_response = f"REPORT_RESPONSE_FLAG=1 NUMBER={len(users)} PAYLOAD={users}"
                client_socket.send(report_response.encode('ascii'))

            elif message.startswith("ATTACHMENT"):
                filename = message.split('=')[1]
                save_file(client_socket, filename)
                # Broadcast the file to all clients
                broadcast(f"ATTACHMENT_FLAG=1 FILENAME={filename} PAYLOAD={open(filename, 'r').read()}")
    except:
        print(f"Error with client {username} or {address}")
    finally:
        client_socket.close()


# Save file received from a client
def save_file(client_socket, filename):
    with open(f"downloads/{filename}", "wb") as file:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file.write(data)


# Broadcast messages to all clients
def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('ascii'))
        except:
            pass


# Accept client connections
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print("Server listening on port 18000...")

    while True:
        client_socket, address = server_socket.accept()
        print(f"New connection from {address}")
        thread = threading.Thread(target=handle_client, args=(client_socket, address))
        thread.start()


if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    start_server()
