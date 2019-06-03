import socket
import os
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('', 8080))
print("Server Socket Open")

def parsing_first_msg(recv_msg):
   cksum = recv_msg[:20]
   seqNum = chr(recv_msg[20])
   filename = recv_msg[21:32]
   filesize = recv_msg[32:36]
   msg = recv_msg[36:]

   dataarray = [cksum,seqNum,filename,filesize, msg]
   return dataarray

def parsing_msg(recv_msg):
   cksum = recv_msg[:20]
   seqNum = chr(recv_msg[20])
   msg = recv_msg[21:]

   dataarray = [cksum,seqNum,msg]
   return dataarray

def checksum_not_reverse(msg):
   import math
   cksum = bytearray(20)
   carry = 0
   end_round_carry = 0
   for i in range(0,len(msg)):
      j = i%20
      temp = cksum[j]
      cksum[j]= (cksum[j] + msg[i] + carry) & 0xFF
      carry = (temp + msg[i] + carry) / 0xFF
      carry = math.floor(carry)
      if j==19:
         end_round_carry+=carry
         carry = 0
   carry = 0
   temp = cksum[0]
   cksum[0] = (cksum[0]+end_round_carry) & 0xFF
   carry = (temp + end_round_carry) /0xFF
   carry = math.floor(carry)
   for i in range(1,20):
      if carry > 0:
         temp = cksum[i]
         cksum[i] +=carry
         carry = (temp + cksum[i]) /0xFF
         carry = math.floor(carry)
      else:
         break
   cksum.reverse()
   return cksum

def check_cks(cks,msg):
   import sys
   cks = bytearray(cks)
   pcheck = checksum_not_reverse(msg)
   for i in range(0,20):
      pcheck[i] = (pcheck[i]+cks[i]) &0xFF
      pcheck[i] = ~pcheck[i] & 0xFF
   checkValue = True
   for i in range(0,20):
      if pcheck[i] != 0:
         checkValue = False
   return checkValue
def size_of_file(filesize):
   count = 0
   for i in range(0,4):
      temp = int(chr(filesize[i]),base=16)
      count += temp * ( 16 ** (3-i))
   return count
   
####################################################################

seqNum_toggle = [1,0]
seqNum = seqNum_toggle[0]
base = ""
data, addr = server_socket.recvfrom(2048)
dataarray = parsing_first_msg(data)
#print(type(dataarray[1]))   #seqNum
#print(type(dataarray[2]))   #filename
#print(type(dataarray[3]))   #filesize
#print(type(dataarray[4]))   #msg
#chk_temp = dataarray[1].encode()+dataarray[2]+dataarray[3]+dataarray[4]
#print(check_cks(dataarray[0],chk_temp))   --> true

chk_temp = dataarray[1].encode()+dataarray[2]+dataarray[3]+dataarray[4]
isSuccess = False
transffered_data = 0

server_socket.settimeout(5)
while not isSuccess:
   try:
      isAcquired = check_cks(dataarray[0],chk_temp)
      if isAcquired: 
         print("Send file info ACK...")
         server_socket.sendto(str(seqNum).encode(), addr)
         server_socket.settimeout(None)
         isSuccess = True
         seqNum = seqNum_toggle[seqNum]
      else:      
         server_socket.sendto("2".encode(), addr)
         data, addr = server_socket.recvfrom(2048)
         server_socket.settimeout(None)
         dataarray = parsing_first_msg(data)
         chk_temp = dataarray[1].encode()+dataarray[2]+dataarray[3]+dataarray[4]

   except socket.timeout:
      print("Wait for 5...") 
      server_socket.settimeout(5)
      server_socket.sendto("2".encode(), addr)
       
tname = dataarray[2].decode().strip("0")
base=os.path.basename(tname)
filepath = dataarray[2].decode().strip("0")
filesize = dataarray[3]
filesize = size_of_file(filesize)
print("FileName : ", base)
print("FIleSize : ",filesize)
print("Received File Path : ", filepath)
transffered_data += len(dataarray[4])
print("current_size / totalsize = ", transffered_data, "/", filesize,",", (transffered_data / filesize) * 100, "%")

with open(base,'wb') as ttt:
   received_msg = dataarray[4]
   ttt.write(received_msg)
   
   while(True):
      isSuccess = False
      while not isSuccess:
         try:
            server_socket.settimeout(5)
            data, addr = server_socket.recvfrom(2048)
            parsed_msg = parsing_msg(data)
            #print(bytearray(parsed_msg[1]), type(parsed_msg[2]))
            isAcquired = check_cks(parsed_msg[0], (parsed_msg[1]).encode()+parsed_msg[2])
            if isAcquired:
               if parsed_msg[1] == str(seqNum):
                  continue
               ttt.write(parsed_msg[2])
               server_socket.sendto(str(seqNum).encode(), addr)
               server_socket.settimeout(None)
               isSuccess = True
               seqNum = seqNum_toggle[seqNum]
            else:
               raise ValueError
            
            transffered_data += len(parsed_msg[2])
            print("**current_size / totalsize = ", transffered_data, "/", filesize,",", (transffered_data / filesize) * 100, "%")
         except ValueError:
            print("Packet corrupted!!! Send to Sender NAK")
            server_socket.sendto("2".encode(), addr)
         except socket.timeout:
            server_socket.sendto("2".encode(), addr)
            
      if transffered_data == filesize: break
