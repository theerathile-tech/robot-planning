import socket

ESP32_IP = "192.168.1.100"
PORT = 8080

def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ESP32_IP, PORT))
        s.sendall((command + "\n").encode())
        response = s.recv(1024).decode()
        print("ESP32:", response)
