import socket
import threading

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

clients = {}
lock = threading.Lock()

def broadcast(message, sender_username=None):
    with lock:
        # Iterate over connected clients and send message
        for client, username in clients.items():
            if username != sender_username:
                try:
                    client.sendall(message)
                except:
                    # If the client connection is broken, remove the client from the clients dictionary
                    del clients[client]
                    print(f"Client {username} has disconnected unexpectedly")

def private_message(message, recipient_username, sender_username):
    with lock:
        # Find the recipient client by username
        for client, username in clients.items():
            if username == recipient_username:
                try:
                    client.sendall(message)
                except:
                    # If the client connection is broken, remove the client from the clients dictionary
                    del clients[client]
                    print(f"Client {username} has disconnected unexpectedly")
                break

def handle_client(client, address):
    with client:
        # Receive username from client
        username = client.recv(1024).decode('utf-8')
        
        with lock:
            clients[client] = username
        
        # Send welcome message to client
        client.sendall(f'Welcome to the chat room, {username}! '.encode('utf-8'))
        
        # Notify other clients that a new client has joined
        broadcast(f'{username} has joined the chat'.encode('utf-8'), username)
        
        # Send message explaining private messaging to client
        client.sendall("(/w to Private Message, /quit to Disconnect)".encode('utf-8'))

        while True:
            # Receive message from client
            try:
                message = client.recv(1024).decode('utf-8')
            except:
                # If there's an error receiving a message, assume the client has disconnected and break the loop
                break
            # When message starts with /w client sends private message
            if message.startswith('/w'):
                parts = message.split(' ', 2)
                if len(parts) < 3:
                    client.sendall('Please specify a recipient and a message'.encode('utf-8'))
                    continue
                recipient_username = parts[1]
                private_message(f'[WHISPER] {username}: {parts[2]}'.encode('utf-8'), recipient_username, username)
            else:
                # Broadcast message to all clients
                broadcast(f'{username}: {message}'.encode('utf-8'), username)

                # Check if client wants to quit
                if message == '/quit':
                    break
                else:
                    # Show message in the chat box
                    client.sendall(f'[You]: {message}'.encode('utf-8'))
        
        with lock:
            if client in clients:
                # Remove client from clients dictionary
                del clients[client]
        
        # Notify other clients that a client has left
        broadcast(f'{username} has left the chat'.encode('utf-8'), username)
        print(f"Client {username} has disconnected")


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f'Server listening on IP:{HOST} PORT:{PORT}')
    
    while True:
        # Wait for new client connections
        client, address = s.accept()
        print(f'New client connected: {address}')
        
        # Start a new thread to handle client communication
        threading.Thread(target=handle_client, args=(client, address)).start()
