import tkinter as tk
import socket
import threading

# Server address and port
HOST = '127.0.0.1'
PORT = 65432

# Prompt user to enter username
username = input("Enter your username: ")

# Connect to server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# Send username to server
client_socket.sendall(username.encode('utf-8'))

# Function to receive messages from server
def receive():
    while True:
        try:
            # Receive message from server
            message = client_socket.recv(1024).decode('utf-8')
            message_listbox.insert(tk.END, message)
        except:
            # If there's an error receiving a message, assume the server has disconnected and break the loop
            break

# Function to send message to server
def send():
    message = message_entry.get()
    client_socket.sendall(message.encode('utf-8'))
    message_entry.delete(0, tk.END)

# Create GUI
root = tk.Tk()
root.title("Chat Room")

# Create message listbox
message_listbox = tk.Listbox(root, height=20, width=50)
message_listbox.grid(row=0, column=0, sticky=tk.NSEW)

# Create message entry box and send button
message_frame = tk.Frame(root)
message_frame.grid(row=1, column=0, sticky=tk.NSEW)

message_entry = tk.Entry(message_frame)
message_entry.grid(row=0, column=0, sticky=tk.NSEW)

send_button = tk.Button(message_frame, text="Send", command=send)
send_button.grid(row=0, column=1, sticky=tk.NSEW)

# Configure grid weights for responsiveness
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)
message_frame.grid_columnconfigure(0, weight=1)

# Create thread to receive messages from server
receive_thread = threading.Thread(target=receive)
receive_thread.start()

# Start GUI
root.mainloop()

# Close socket when GUI is closed
client_socket.close()

