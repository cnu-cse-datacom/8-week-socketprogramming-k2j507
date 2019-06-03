import socket
import sys
from time import sleep
from os.path import getsize
FLAGS = None

class SenderSocket():

   def __init__(self):
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

   def socket_send(self):
      
      print("Sender Socket open...")
      HOST = input("Receiver IP = ")
      if not HOST:
         HOST = FLAGS.ip
      PORT = input("Receiver PORT = ")
      if not PORT:
         PORT = FLAGS.port
      else:
         PORT = int(PORT)
      filename = input("Input file name: ")
      filesize_str = str(getsize(filename))
      if not filesize_str:
         print("Error : ", filename, " is not exist")
         sys.exit()
      filesize = int(filesize_str)
      ##################################################################
#      data, r = self.socket.recvfrom(1024)
#      if not r:
#         print("File[%s]: Cannot connect server" %filename)
      seqNum_togle = [1,0]
      seqNum = seqNum_togle[1];
      self.socket.connect((HOST,PORT))
      #self.socket.sendto(FLAGS.ip,FLAGS.port)
      print("Send file info filename, filesize, seqNum to Server...")
      formatstring = fileformatset(seqNum,filename,filesize)
      #print(type(formatstring))      --> bytearray
      #print(formatstring)
      
      transffered_data = 0
      with open(filename,'rb') as ssf:
         little_msg = ssf.read(1024)
         #type,filename,filesize,message => total byte
         total_msg = formatstring+little_msg               
         #checksum 20byte
         cksumbyte = checksum(total_msg)
         isSuccess = False
         self.socket.settimeout(0.5)
         #print(cksumbyte)
         #print(total_msg)
         self.socket.sendall(cksumbyte+total_msg)
         while not isSuccess:
            try:
               ACK, addr = self.socket.recvfrom(1024)
               self.socket.settimeout(None)
               #print("***********",ACK.decode())
               if ACK.decode() == "2":
                  raise ValueError
               isSuccess = True
               seqNum = seqNum_togle[seqNum]
            except socket.timeout:
               print("*Time out!***")
               self.socket.settimeout(0.5)
               self.socket.sendall(cksumbyte+total_msg)
            except ValueError:
               print("* Received NAK - Retransmit !")
               self.socket.settimeout(0.5)
               self.socket.sendall(cksumbyte+total_msg)

         transffered_data +=len(little_msg)
         print("current_size / totalsize = ", transffered_data, "/", filesize,",", (transffered_data / filesize) * 100, "%") 
         sleep(0.5)
         while(True):
            isSuccess = False
            little_msg = ssf.read(1024)
            if not little_msg: break
            stype = hex(seqNum).encode()[2:]
            cksumbyte = checksum(stype+little_msg)
            total_msg = cksumbyte+stype+little_msg
            self.socket.settimeout(0.5)
            self.socket.sendto(total_msg, (FLAGS.ip,FLAGS.port))
            while not isSuccess:
               try:
                  ACK, addr = self.socket.recvfrom(1024)
                  self.socket.settimeout(None)
                  #print("******",ACK.decode())
                  if ACK.decode() == "2":
                     raise ValueError
                  isSuccess = True
                  seqNum = seqNum_togle[seqNum]
               except socket.timeout:
                  print("**Time out!***")
                  self.socket.settimeout(0.5)
                  self.socket.sendto(total_msg, (FLAGS.ip,FLAGS.port))
               except ValueError:
                  print("**Retransmission***")
                  self.socket.settimeout(0.5)
                  self.socket.sendto(total_msg, (FLAGS.ip,FLAGS.port))
                  
            transffered_data += len(little_msg)
            print("current_size / totalsize = ", transffered_data, "/", filesize,",", (transffered_data / filesize) * 100, "%") 
            


   def main(self):
      self.socket_send()

#############################################
def checksum(msg):
   import math
   checksum = bytes(20)
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
      
   pcksum = bytearray(20)
   for i in range(0,20):
      pcksum[i]=(0xFF&~cksum[i])
   pcksum.reverse()
   return pcksum

def fileformatset(ttype, tfilename, tsize):
   stype = hex(ttype).encode()[2:]
   size = hex(tsize).encode()[2:]
   if len(size) <= 4:
      size = size.zfill(4)
   name = tfilename.zfill(11)   
   name = name.encode()
   tttt = bytearray(stype + name + size)
   return tttt

################################################
if __name__=='__main__':
   import argparse

   parser = argparse.ArgumentParser()
   parser.add_argument('-i', '--ip', type=str, default='localhost')
   parser.add_argument('-p', '--port', type=int, default=8080)

   FLAGS, _= parser.parse_known_args()

   sender_socket = SenderSocket()
   sender_socket.main()
