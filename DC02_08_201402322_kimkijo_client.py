import socket
import os
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

file_name = input("input file name:")

ip_addr = "10.0.2.15"
port_num = 9000
socket.sendto(file_name.encode(), (ip_addr,int(port_num)))


f = open(file_name,"rb")

current_size = 0 
max_size = os.path.getsize(file_name)

socket.sendto(str(max_size).encode(), (ip_addr,int(port_num)))

while(current_size < max_size):
        data = f.read(1024)
        socket.sendto(data, (ip_addr,int(port_num)))
        current_size = min(current_size + 1024, int(max_size))
        print("current_size / max_size = "+ str(current_size) +"/" + str(max_size) + " " + str((current_size/max_size)*100))


print("ok\n")
print("file_send_end")

