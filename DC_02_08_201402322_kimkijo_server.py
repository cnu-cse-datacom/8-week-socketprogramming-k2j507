import socket
#server

socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind(("10.0.2.15",9000)) #ip address in virual machine

print("file recv start from 10.0.2.15") 
file_name, addr = socket.recvfrom(2000)
print("File Name : " + file_name.decode())
file_size, addr = socket.recvfrom(2000)
size = file_size.decode()
total_size = int(size)
print("File Size : " + str(total_size))

f = open(file_name, "wb")
current_size = 0;

while(current_size < total_size):
    data, addr = socket.recvfrom(1024)
    current_size = min(current_size + 1024, int(total_size))
    print("current_size / total_size = " + str(current_size) + "/" + str(total_size) + " " + str((current_size/total_size)*100))

    f.write(data)
