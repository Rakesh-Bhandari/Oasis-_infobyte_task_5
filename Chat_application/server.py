import socket
import threading
import os
from datetime import datetime

# Global variables to store client connections and usernames
clients = {}
usernames = []

# Function to handle client connections
def handle_client(client_socket, client_address):
    try:
        # Receive and verify the username
        username = client_socket.recv(1024).decode('utf-8').strip()
        if not username or username == "REQUEST_HISTORY":
            client_socket.send("invalid username".encode('utf-8'))
            client_socket.close()
            return

        usernames.append(username)
        clients[username] = client_socket

        print(f"{username} joined from {client_address}.")
        broadcast(f"{username} has joined the chat.", "Server")
        log_message( "Server",f"{username} has joined the chat.")

        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8').strip()
                if not message:
                    break

                if message == "REQUEST_HISTORY":
                    send_history(client_socket)
                else:
                    # Process the message
                    sender, msg = message.split(":", 1)
                    broadcast(msg.strip(), sender)
                    log_message(sender, msg.strip())

            except socket.error as e:
                print(f"Error: {e}")
                break

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if username:
            if username in usernames:
                usernames.remove(username)
            if username in clients:
                del clients[username]
            broadcast(f"{username} has left the chat.", "Server")
            log_message("Server",f"{username} has left the chat.")
            print(f"{username} disconnected.")
        client_socket.close()

# Function to broadcast messages to all clients
def broadcast(message, sender):
    timestamp = datetime.now().strftime('%Y-%m-%d|%I:%M %p')
    formatted_message = f"{sender}:{message}"
    for client_username, client_socket in clients.items():
        try:
            client_socket.send(formatted_message.encode('utf-8'))
        except socket.error as e:
            print(f"Error: {e}")
            client_socket.close()
            if client_username in usernames:
                usernames.remove(client_username)
                del clients[client_username]

# Function to log messages to the history file
def log_message(sender, message):
    timestamp = datetime.now().strftime('%Y-%m-%d|%I:%M %p')
    with open("chat_history.txt", "a") as f:
        f.write(f"{sender}|{timestamp}|{message}\n")

# Function to send the chat history to a client
def send_history(client_socket):
    if os.path.exists("chat_history.txt"):
        with open("chat_history.txt", "r") as f:
            history_data = f.read()
            client_socket.send(history_data.encode('utf-8'))
    else:
        client_socket.send("No history available.".encode('utf-8'))

# Main function to start the server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))  # Replace with your server's IP and port
    server_socket.listen(5)
    print("Server started. Waiting for connections...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        # Start a new thread to handle the client's communication
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
