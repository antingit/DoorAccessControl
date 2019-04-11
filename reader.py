import serial
import os
import sys
import time
import threading
import urllib2
import xml.etree.ElementTree as ET
from ConfigParser import SafeConfigParser
import requests
import datetime
import socket
import pickle

#########################

def log_writer(mesage):

  time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  mesage=time+" "+mesage

  try:
    file = open("reader.log" , "a")
    file.write(mesage)
    file.close()
  except:
    file = open("reader.log","w")
    file.write(mesage)
    file.close()

#########################

try:
  file=open("reader.cfg","r")
  file.close()
except:
  mesage = "config file not found program will exit"+"\n"  
  log_writer(mesage)
  print mesage#
  sys.exit(0)

#########################

config=SafeConfigParser()
config.read("reader.cfg")

#########################  

rqst_data=config.get("READER","rqst_data")
xml_url=config.get("URL_CONFIG","xml_url")
entancelog_url=config.get("URL_CONFIG","entrancelog_url")
entranceerror_url=config.get("URL_CONFIG","entranceerror_url")
uptime=int(config.get("URL_CONFIG","xml_refresh_time"))
controller_id=config.get("HW_CONFIG","controller_id")
port=config.get("HW_CONFIG","port")
s_host=config.get("RC_CONFIG","host")
s_port=int(config.get("RC_CONFIG","port"))

ser = serial.Serial(
  port= port,
  baudrate= 9600,
  parity= "N", 
  stopbits= 1, 
  bytesize= 8,
  timeout= 0.05
)
ser.close()

#########################

dist_schedule={}
dist_role_alowed_gate={}
dist_et_role={}
serial_list=[]
check_list=[]
rd="stop_time"
rdc=0
log_upload_count=0
error_log_count=0
socket_data=""

#########################

try:
  f=open("card_data.dat","rb")
  card_data_list=pickle.load(f)
  f.close
  dist_et_role=card_data_list[0]
  dist_role_alowed_gate=card_data_list[1]
  dist_schedule=card_data_list[2]
  card_data_list=[]

  serial_list=dist_et_role.keys()
  serial_list=map(int,serial_list)
except:
  pass

#########################

def access_log(mesage):

  time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
  mesage=time+" "+mesage

  try:
    file = open("access.log" , "a")
    file.write(mesage)
    file.close()
  except:
    file = open("access.log","w")
    file.write(mesage)
    file.close()

#########################

def access_log_uploader(controller_id,readerdata,reader_nr,access_status):

  global log_upload_count

  log_upload_count=log_upload_count+1
  date=datetime.datetime.now().strftime("%Y-%m-%d*%H:%M:%S")
  reader_id=config.get("READER_ID",str(reader_nr))

  try:

    f=open("upload.dat","r")

    for access_data in f:
      requests.post(entancelog_url,data=access_data)
      mesage = "send access data from file upload.dat"+"\n"      
      log_writer(mesage)
      print mesage#
    
    os.remove("upload.dat")

    up_data=log_upload_count,controller_id,reader_id,readerdata,date,reader_nr,access_status
    up_data=str(up_data)
    up_data=up_data.replace("'","")
    up_data=up_data.replace("(","")
    up_data=up_data.replace(")","")
    up_data=up_data.replace(" ","")
    up_data=up_data.replace("*"," ")
    up_data=up_data.replace("L","")    
    requests.post(entancelog_url,data=up_data)
    print up_data+" data send to server"#

  except:

    try:

      up_data=log_upload_count,controller_id,reader_id,readerdata,date,reader_nr,access_status
      up_data=str(up_data)
      up_data=up_data.replace("'","")
      up_data=up_data.replace("(","")
      up_data=up_data.replace(")","")
      up_data=up_data.replace(" ","")
      up_data=up_data.replace("*"," ")
      up_data=up_data.replace("L","")
      requests.post(entancelog_url,data=up_data)
      print up_data+" data sent to server"#
            
    except:
  
      file=open("upload.dat","a")      
      up_data=log_upload_count,controller_id,reader_id,readerdata,date,reader_nr,access_status 
      up_data=str(up_data)
      up_data=up_data.replace("'","")
      up_data=up_data.replace("(","")
      up_data=up_data.replace(")","")
      up_data=up_data.replace(" ","")
      up_data=up_data.replace("*"," ")
      up_data=up_data.replace("L","")
      up_data=up_data+"\n"
      file.write(up_data)
      file.close()
      mesage = "error in log uploader write data to file upload.dat"+"\n"      
      log_writer(mesage)
      print mesage#

#########################

def error_log_uploader(mesage):

  global error_log_count 
  mesage_a=mesage

  if error_log_count > 0:
    error_log_count=error_log_count-1
  else:
    time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    up_data=time+" "+"contr_id "+str(controller_id)+" >> "+mesage
    try:
      requests.post(entranceerror_url,data=up_data)
      mesage="error log send to server"+"\n"
      log_writer(mesage_a)
      log_writer(mesage)      
      print mesage_a,mesage#
      error_log_count=20
    except:
      mesage="error in log uploader error data not send"+"\n"
      log_writer(mesage_a)
      log_writer(mesage)      
      print mesage_a,mesage#
      error_log_count=10

#########################

def backup_xml():

  global error_log_count

  time.sleep(2)

  mesage="restoring data from backup.xml"+"\n"
  log_writer(mesage)
  print mesage#
  try:
    os.system("cp backup.xml card.xml")
    xmlpars()
  except:
    mesage="error restoring data from backup"+"\n"
    error_log_count=0
    t4=threading.Thread(target=error_log_uploader,args=(mesage,))
    t4.start()

#########################

def getxml():

  global error_log_count

  timer=uptime
  
  while True:
    if timer==uptime:
      try:
        xml=urllib2.urlopen(xml_url)
        xml_data=xml.read()
        f=open("card.xml","w")
        f.write(xml_data)
        f.close()
        timer=0        
        mesage="card.xml received update"+"\n"
        log_writer(mesage)
        print mesage#
        try:
          xmlpars()
        except:
          mesage="card.xml error"+"\n"
          error_log_count=0
          t4=threading.Thread(target=error_log_uploader,args=(mesage,))
          t4.start()
          backup_xml()
          pass
        f=open("backup.xml","w")
        f.write(xml_data)
        f.close()  
      except:        
        mesage="url conection error"+"\n"
        log_writer(mesage)
        print mesage#

        try:
          file=open("card.xml","r")
          file.close()
        except:
          mesage = "xml file not found"+"\n"
          print mesage#
          log_writer(mesage) 
          timer=0
          backup_xml()
          continue
        
        try:
          xmlpars()
        except:
          mesage="card.xml error"+"\n"
          error_log_count=0
          t4=threading.Thread(target=error_log_uploader,args=(mesage,))
          t4.start()
          backup_xml()
          pass
        timer=0
    else:
      timer=timer+1
      time.sleep(1)
      
#########################

def xmlpars():

  global dist_schedule
  global dist_role_alowed_gate
  global dist_et_role 
  global serial_list

  tree=ET.parse("card.xml")
  root=tree.getroot()

  counter_a=0
  counter_b=0
  counter_c=0
  dist_role_alowed_gate={}
  dist_et_role={}
  dist_schedule={}
  schedule_list=[]
  gate_group_list=[]

  while counter_a != len(root[2]):
    a=root[2][counter_a].attrib["id"]

    while counter_b != len(root[2][counter_c]):
      b=root[2][counter_a][counter_b].attrib["gate_group"]
      c=root[2][counter_a][counter_b].attrib["schedule"]
      gate_group_list.append(b)
      gate_group_list.append(c)
      counter_b=counter_b+1

    counter_b=0  
    counter_a=counter_a+1
    counter_c=counter_c+1
    dist_role_alowed_gate[a]=gate_group_list
    gate_group_list=[]

  counter_a=0
  counter_b=0
  counter_c=0

  while counter_a != len(root[3]):
    a=root[3][counter_a].attrib["et"]
    b=root[3][counter_a].attrib["role"]
    dist_et_role[a]=b
    counter_a=counter_a+1

  counter_a=0

  while counter_a != len(root[0]):
    a=root[0][counter_a].attrib["id"]

    while counter_b != len(root[0][counter_c]):
      b=root[0][counter_a][counter_b].attrib["dow"]
      c=root[0][counter_a][counter_b].attrib["from"] 
      d=root[0][counter_a][counter_b].attrib["to"] 
      schedule_list.append(b)
      schedule_list.append(c)
      schedule_list.append(d)
      counter_b=counter_b+1

    counter_b=0
    counter_a=counter_a+1
    counter_c=counter_c+1
    dist_schedule[a]=schedule_list
    schedule_list=[]

  counter_a=0
  counter_b=0
  counter_c=0

  serial_list=dist_et_role.keys()
  serial_list=map(int,serial_list)

  print dist_schedule#
  print ""#
  print dist_role_alowed_gate#
  print ""#
  print dist_et_role#

  card_data()

#########################

def card_data():

  card_data_list=[]
  card_data_list.append(dist_et_role)
  card_data_list.append(dist_role_alowed_gate)
  card_data_list.append(dist_schedule)
  f=open("card_data.dat","wb")
  pickle.dump(card_data_list,f)
  f.close()

#########################

def data_processing(readerdata):

  global check_list
  global error_log_count

  serial_nr=readerdata[8:-4]
  reader_nr=readerdata[2:4]
  reader_nr=int(reader_nr,16)
  serial_nr=int(serial_nr,16)

  try:
    reader_id=config.get("READER_ID",str(reader_nr))
  except:
    mesage=str(reader_nr)+" reader nr not found in reader config"+"\n"
    error_log_count=0
    t4=threading.Thread(target=error_log_uploader,args=(mesage,))
    t4.start()
    return 
    
  print reader_nr#
  print serial_nr#
  
  if serial_nr in serial_list:
    check_list.append(True)
    schedule_check(serial_nr,reader_nr) #>>
    print check_list#
  else:
    check_list.append(False) 
    print check_list#

  if False in check_list:
    mesage="Access denied reader "+str(reader_nr)+" s_n "+str(serial_nr)+"\n"
    access_log(mesage)
    print mesage#
    denied(reader_nr)
    access_status="AccessDenied"
    t3=threading.Thread(target=access_log_uploader,args=(controller_id,serial_nr,reader_nr,access_status))
#    t3.start()
    check_list=[]
  else:
    mesage="Access granted reader "+str(reader_nr)+" s_n "+str(serial_nr)+"\n"
    access_log(mesage)
    print mesage#
    aloved(reader_nr)
    access_status="AccessGranted"
    t3=threading.Thread(target=access_log_uploader,args=(controller_id,serial_nr,reader_nr,access_status))
#    t3.start()
    check_list=[]    

#########################

def aloved(reader_nr):
  
  command=""

  try:
    aloved_command=config.get("READER_ALOWED",str(reader_nr))
  except:
    mesage="aloved command not found in reader config"+"\n"
    log_writer(mesage)
    print mesage#
    return

  for i in str(aloved_command):
    command=command+i
    if i ==":":
      command=command.replace(":","")
      try:
        command=command.decode("hex")
      except:
        print "aloved command error chck config"
        pass
      ser.open()
      ser.write(command)
      ser.read(32)
      ser.close()  
      print command.encode("hex")#
      command=""
    else:
      pass

#########################

def denied(reader_nr):

  command=""

  try:
    denied_command=config.get("READER_DENIED",str(reader_nr))
  except:
    mesage="denied command not found in reader config"+"\n"
    log_writer(mesage)
    print mesage#
    return

  for i in str(denied_command):
    command=command+i
    if i == ":":
      command=command.replace(":","")
      try:
        command=command.decode("hex")
      except:
        print "denied command error chck config"
        pass
      ser.open()
      ser.write(command)
      ser.read(32)
      ser.close()
      print command.encode("hex")#
      command=""
    else:
      pass

#########################

def schedule_check(serial_nr,reader_nr):
  
  counter_a=1
  counter_b=0
  schedule_check_list=[]

  reader_id=config.get("READER_ID",str(reader_nr))
  timenow=datetime.datetime.now().strftime('%H:%M')
  daynow=datetime.datetime.today().weekday()  
  role_id=dist_et_role.get(str(serial_nr))
  gate_id=dist_role_alowed_gate.get(role_id)

  print role_id# 
  print reader_id# 
  print gate_id# 

  while len(gate_id)>counter_a:
    gate=gate_id[counter_b]
    counter_b=counter_b+2

    if gate == reader_id:
      schedule_id=gate_id[counter_a]
      counter_a=counter_a+2      
      schedule_time=dist_schedule.get(schedule_id,"None")
      
      print schedule_id#
      print schedule_time#
      
      if str(daynow+1) in schedule_time:
        dow=schedule_time.index(str(daynow+1))
        starttime=schedule_time[dow+1]
        stoptime=schedule_time[dow+2]
        
        print starttime#
        print stoptime#
        print daynow+1#
        
        if timenow >= stoptime:
          schedule_check_list.append(False)
        elif timenow >= starttime:
          schedule_check_list.append(True)
        else:
          schedule_check_list.append(False)        
        
      else:
          schedule_check_list.append(False)    
    else:
      counter_a=counter_a+2
      schedule_check_list.append(False)

  print schedule_check_list#

  if True in schedule_check_list:
    check_list.append(True)
  else:
    check_list.append(False)
      
#########################

def reader():

  global rd
  global rdc
  global socket_data

  poling_command=""
  checksum=0 

  while True:    
    for i in rqst_data:
      poling_command=poling_command+i
      if i == ":":
        poling_command=poling_command.replace(":","")
        try:   
          poling_command=poling_command.decode("hex")
        except:
          print "rqst data error chck config"
          pass
        ser.open()
        ser.write(poling_command)
        poling_command=""
        readerdata = ser.read(14)
        ser.close()
        if socket_data != "":
          readerdata=socket_data
          socket_data=""
        else:
          pass
        
        readerdata=readerdata.encode("hex")

        try:
          len_check_in=readerdata[4:6]
          len_check_data=readerdata[5:-5]
          len_check_data=len_check_data.decode("hex")
          check_data=readerdata[2:-4] 
          check_data=check_data.decode("hex")                  
          check_byte=readerdata[-4:-2]
        except:
          print "error no data or corrupted data received"                  
          continue

        if readerdata[:2] != "aa" or readerdata[-2:] != "bb":
          mesage="start or stop byte excepted"+"\n"
          print mesage# 
          continue
        else:
          pass

        len_check_out=len(len_check_data)
        len_check_out=hex(len_check_out)
        len_check_out=len_check_out[2:]
        if len(len_check_out)==1:
          len_check_out="0"+len_check_out

        for bytes in check_data:
          checksum=checksum^ord(bytes)
        checksum=hex(checksum)
        checksum=checksum[2:]
        if len(checksum)==1:
          checksum="0"+checksum
        chksum=checksum#

        if checksum==check_byte and len_check_in==len_check_out:
          checksum=0
          pass
        else:
          mesage="error in received data"+"\n"
          print mesage#
          t4=threading.Thread(target=error_log_uploader,args=(mesage,))
          t4.start()          
          checksum=0
          continue

        if rd == readerdata and rdc > 1:
          readerdata="stop_time"
        else:
          pass

        if len(readerdata) >= 16 and len(readerdata) < 30:
          print "processing data"#
          data_processing(readerdata)
          rd=readerdata
          rdc=5
        else:
          continue
  
        print readerdata#
        print check_data.encode("hex")#
        print check_byte#
        print chksum#
        print len(readerdata)#

#########################

def rc_socket():

  global socket_data
  global error_log_count 

  data="" 
  
  s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  s.bind((s_host,s_port))
  s.listen(5)

  while True:
    conn ,addr=s.accept()
    conn.settimeout(5.0)
    msg="socket connected ",addr
    mesage=str(msg)+"\n"
    log_writer(mesage)
    print msg#

    while True:
      try:
        data=conn.recv(1024)
      except:
        data=""

      if data == "":
        print "socket disconected ",str(addr)#
        conn.close()
        break
       
      else:
        socket_data=data
        conn.close()
        time.sleep(1)     

#########################

t1=threading.Thread(target=getxml)
t1.setDaemon(True)
t1.start()
mesage="thread getxml started"+"\n"
log_writer(mesage)
print mesage#

t2=threading.Thread(target=reader)
t2.setDaemon(True)
t2.start()
mesage="thread reader started"+"\n"
log_writer(mesage)
print mesage#

t5=threading.Thread(target=rc_socket)
t5.setDaemon(True)
t5.start()
mesage="thread rc_socket started"+"\n"
log_writer(mesage)
print mesage#

#########################

while True:

  if rdc > 0:
    rdc=rdc-1
  else:
    pass

  time.sleep(1)
  




