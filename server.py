import socket
import threading
import time

#setting server up
host = '127.0.0.1' #localhost
port = 18000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port)) #server is bound to the local host on poer 18000
server.listen() #server is listening for connections

#lists
clients = []
nicknames = []

def broadcast(message): #broadcasts message from server to all clients in chat
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024) #if message is recieved from client, then it will send the message to everyone else
            broadcast(message)
        except:
            index = clients.index(client) #if message is not recieved, then remove the client from the list
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('ascii'))
            nicknames.remove(nickname)
            break

def recieve():
    while True:
        client, address = server.accept() #accepting all clients
        print(f"Connected with {str(address)}")

        client.send('NICK'.encode('ascii')) #server promting client for nickname 
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname) #takes in nickname
        clients.append(client) #adds client to client list
        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} joined the chat!'.encode('ascii')) #sends message to everyone in chat the '....' joined
        client.send('connected to the server!'.encode('ascii')) #tells client that they have joined the server

        thread = threading.Thread(target = handle, args = (client,))
        thread.start()

print("Server is active:)")
recieve()