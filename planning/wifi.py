import socket

ESP32_IP = "192.168.1.100"
PORT = 8080
wifi_connected = False

def check_wifi_connection():
    global wifi_connected
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ESP32_IP, PORT))
            wifi_connected = True
            return True
    except:
        wifi_connected = False
        return False

def send_command(command):
    global wifi_connected
    
    if not check_wifi_connection():
        print("WiFi connection to ESP32 is not available")
        return False
        
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)  
            s.connect((ESP32_IP, PORT))
            s.sendall((command + "\n").encode())
            response = s.recv(1024).decode()
            print("ESP32:", response)
            wifi_connected = True
            return True
    except:
        print(f"Failed to send command '{command}' to ESP32")
        wifi_connected = False
        return False
