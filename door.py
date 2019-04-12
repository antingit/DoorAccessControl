import socket
import pickle

#########################

data_dist={}
data_list=[]
user_input=""

#########################

try:
  f=open("save.dat","rb")
  data_dist=pickle.load(f)
  f.close
  print data_dist#
except:
  pass

#########################

def rc_control(serial_nr,reader_nr,controller_ip,controller_port):

  host=controller_ip
  port=int(controller_port)

  d1="aa"   #stx
  d2=""     #reader_nr
  d3=""     #data len
  d4="00"   #status
  d5=""     #serial data
  d6=""     #checksum
  d7="bb"   #etx
  checksum=0

  d2=hex(int(reader_nr))
  d2=d2[2:]
  if len(d2)==1:
    d2="0"+d2
  print d2#

  serial_data=hex(int(serial_nr))
  serial_data=serial_data[2:]
  print serial_data#
  print len(serial_data)#

  if len(serial_data)%2 == 0:
    d5=serial_data
  else:
    d5="0"+serial_data
  print d5  

  data_len=d4+d5
  data_len=data_len.decode("hex")
  d3=len(data_len)
  d3=hex(d3)
  d3=d3[2:]
  if len(d3)==1:
    d3="0"+d3
  print d3
  
  check_data=d2+d3+d4+d5
  print check_data#
  check_data=check_data.decode("hex")

  for bytes in check_data:
    checksum=checksum^ord(bytes)  
  checksum=hex(checksum)
  checksum=checksum[2:]
  if len(checksum)==1:
    checksum="0"+checksum
  print checksum#

  check_data=check_data.encode("hex")

  command=d1+check_data+checksum+d7
  print command#
  print len(command)#
  command=command.decode("hex")

  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.settimeout(5)
  s.connect((host,port))
  s.send(command)
  s.close

#########################

while user_input !="exit and not save":

  print """



\t\t###### DoorAccessControl #######


1.Open door

2.Data registration

3.View registred data

4.Remove registred data

5.Exit

"""
    

  if user_input=="1":
    objekt_id=raw_input("Please input object id:")
    if objekt_id in data_dist:
      a=data_dist.get(objekt_id)
      serial_nr=a[0]
      reader_nr=a[1]
      controller_ip=a[2]
      controller_port=a[3]
      rc_control(serial_nr,reader_nr,controller_ip,controller_port)
    else:
      print "Object not found please register first"
  else:
    pass      

  if user_input == "2":
    objekt_id=raw_input("Please input object id:")
    if objekt_id in data_dist:
      print "The object is already registered try another id"
    else:
      serial_nr=raw_input("Please input card serial number:")
      reader_nr=raw_input("Please input reader number:")
      controller_ip=raw_input("Please input controller ip:")
      controller_port=raw_input("Please input controller port:")
      data_list.append(serial_nr)
      data_list.append(reader_nr)
      data_list.append(controller_ip)
      data_list.append(controller_port)
      data_dist[objekt_id]=data_list
      data_list=[]
      print data_dist#
  else:
    pass

  if user_input == "3":
    for i in data_dist.items():
      print i
    else:
      pass

  if user_input == "4":
    objekt_id=raw_input("Please input object id to remove:")
    if objekt_id in data_dist:
      del data_dist[objekt_id]
      print "Object removed"
    else:
      print "Object not found"

  if user_input == "5":
    print "Data saved"
    f=open("save.dat","wb")
    pickle.dump(data_dist,f)
    f.close()
    user_input="exit and not save"
    continue
  else:
    pass
  
  user_input=raw_input("Please press(1-5):")
  





