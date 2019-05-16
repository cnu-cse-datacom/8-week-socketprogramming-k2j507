import socket

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind(("10.0.2.15",9000)) #ip address in virual machine

file_name, addr = socket.recvfrom(2000)
print("File Name:" + file_name.decode())
file_size, addr = socket.recvfrom(2000)
size = file_size.decode()
max_size = int(size)

f = open(file_name, "wb")
current_size = 0;

while(current_size < max_size):
    data, addr = socket.recvfrom(1024)
    current_size = min(current_size + 1024, int(max_size))
    print("current_size / max_size = " + str(current_size) + "/" + str(max_size) + " " + str((current_size/max_size)*100))

    f.write(data)
