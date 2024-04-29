import socket

def main():
    host = socket.gethostname()
    print(host)
    port = 3000
    message = " "
    client_socket = socket.socket()
    client_socket.connect((host, port))
    
    while message.lower().strip() !='quit':
        client_socket.send(message.encode())
        msg = client_socket.recv(1024).decode()
        print(f'Received message {msg}')
        message = input('>>> ')

    client_socket.close()

if __name__ == '__main__':
    main()