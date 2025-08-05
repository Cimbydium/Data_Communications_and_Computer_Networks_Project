import socket
import os


HOST = 'localhost'
PORT = 12345
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def send_command(command):
    client_socket.sendall(command.encode())
    response = client_socket.recv(1024)
    print(response.decode())

try:
    while True:
        command = input("Please choose an option :\n* Login\n* Signup\n* Upload\n* Download\n* Delete\n* Rename\n* Logout\n ").upper()
        if command in ['LOGIN', 'SIGNUP']:
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            send_command(f"{command} {username} {password}")
        elif command == 'UPLOAD':
            filepath = input("Enter the path of the file to upload: ")
            if os.path.isfile(filepath):
                send_command(f"UPLOAD {os.path.basename(filepath)}")
                with open(filepath, 'rb') as file:
                    while True:
                        bytes_read = file.read(1024)
                        if not bytes_read:
                            break
                        client_socket.sendall(bytes_read)
                client_socket.sendall(b'EOF')
                print(client_socket.recv(1024).decode())
            else:
                print("File not found.")
        elif command == 'DOWNLOAD':
            filename = input("Enter filename to download: ")
            send_command(f"DOWNLOAD {filename}")
            response = client_socket.recv(1024)

            if response == b'File not found':
                print("File not found on server.")
            else:
                with open(filename, 'wb') as file:
                    file.write(response)
                print(f"File '{filename}' downloaded successfully.")
        elif command == 'DELETE':
            filename = input("Enter filename to delete: ")
            send_command(f"DELETE {filename}")
        elif command == 'RENAME':
            old_filename = input("Enter old filename: ")
            new_filename = input("Enter new filename: ")
            send_command(f"RENAME {old_filename} {new_filename}")
        elif command == 'LOGOUT':
            send_command("LOGOUT")
            break
        else:
            print("Unknown command")
finally:
    client_socket.close()
