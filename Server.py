import socket
import os
import json
from threading import Thread, Lock


HOST = 'localhost'
PORT = 12345
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()


user_data_file = 'users.json'
user_data_lock = Lock()


if not os.path.exists(user_data_file):
    with open(user_data_file, 'w') as file:
        json.dump({}, file)

def handle_client(conn, addr):
    print(f"Connected by {addr}")
    try:
        current_user = None
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            command, *args = data.split()

            if command == 'LOGIN':
                username, password = args
                with user_data_lock:
                    with open(user_data_file, 'r') as file:
                        users = json.load(file)
                if username in users and users[username]['password'] == password:
                    conn.sendall(b'Login successful')
                    current_user = username
                    user_folder = f"user_data/{username}"
                    if not os.path.exists(user_folder):
                        os.makedirs(user_folder)
                    file_list = os.listdir(user_folder)
                    conn.sendall(f"Files: {', '.join(file_list)}".encode())
                else:
                    conn.sendall(b'Login failed')

            elif command == 'SIGNUP':
                username, password = args
                with user_data_lock:
                    with open(user_data_file, 'r+') as file:
                        users = json.load(file)
                        if username not in users:
                            users[username] = {'password': password, 'files': []}
                            file.seek(0)
                            json.dump(users, file)
                            file.truncate()
                            conn.sendall(b'Signup successful')
                            os.makedirs(f"user_data/{username}")
                        else:
                            conn.sendall(b'Username already exists')

            elif command == 'UPLOAD':
                filename = args[0]
                filepath = f"user_data/{current_user}/{filename}"
                with open(filepath, 'wb') as file:
                    while True:
                        file_data = conn.recv(1024)
                        if file_data.endswith(b'EOF'):
                            file.write(file_data[:-3])
                            break
                        file.write(file_data)
                conn.sendall(b'File uploaded successfully')

            elif command == 'DOWNLOAD':
                filename = args[0]
                try:
                    with open(f"user_data/{current_user}/{filename}", 'rb') as file:
                        conn.sendall(file.read())
                except FileNotFoundError:
                    conn.sendall(b'File not found')

            elif command == 'DELETE':
                filename = args[0]
                try:
                    os.remove(f"user_data/{current_user}/{filename}")
                    conn.sendall(b'File deleted successfully')
                except FileNotFoundError:
                    conn.sendall(b'File not found')

            elif command == 'RENAME':
                old_filename, new_filename = args
                try:
                    os.rename(f"user_data/{current_user}/{old_filename}", f"user_data/{current_user}/{new_filename}")
                    conn.sendall(b'File renamed successfully')
                except FileNotFoundError:
                    conn.sendall(b'File not found')

            elif command == 'LOGOUT':
                conn.sendall(b'loging out , closing connection...')
                break
    finally:
        conn.close()

def accept_connections():
    while True:
        conn, addr = server_socket.accept()
        Thread(target=handle_client, args=(conn, addr)).start()


print("SERVER IS RUNNING")
accept_connections()
