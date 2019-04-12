import pickle

user_input=""
card_data_list=[]
schedule_list=[]
gate_schedule_id_list=[]
dist_et_role={}
dist_role_alowed_gate={}
dist_schedule={}

#########################

try:
  f=open("card_data.dat","rb")
  card_data_list=pickle.load(f)
  f.close
  dist_et_role=card_data_list[0]
  dist_role_alowed_gate=card_data_list[1]
  dist_schedule=card_data_list[2]
  card_data_list=[]
except:
  pass

#########################

while user_input !="exit and not save":

  print """



\t\t###### Card id registration #######


1.Card data registration

2.View registred card data

3.Schedules registration

4.View schedules data

5.Role registration

6.Delete schedules data

7.Delete card data

8.Delete role data

9.Exit

"""

  if user_input=="1":
    card_id=raw_input("please input card id number:")
    role_id=raw_input("please input role id:")
    dist_et_role[card_id]=role_id
    print dist_et_role
  else:
      pass

  if user_input=="2":
    print dist_et_role
    print " "
    dist_role_alowed_gate_str=str(dist_role_alowed_gate)    
    print dist_role_alowed_gate_str.replace("[","ROLE [")
  else:
    pass

  if user_input=="3":
    schedule_id=raw_input("please input schedule id:")
    dow1f=raw_input("input dow 1 start time:")
    dow1t=raw_input("input dow 1 stop time:") 
    schedule_list.append("1")
    schedule_list.append(dow1f)
    schedule_list.append(dow1t)
    dow2f=raw_input("input dow 2 start time:")
    dow2t=raw_input("input dow 2 stop time:")
    schedule_list.append("2")
    schedule_list.append(dow2f)
    schedule_list.append(dow2t)
    dow3f=raw_input("input dow 3 start time:")
    dow3t=raw_input("input dow 3 stop time:")
    schedule_list.append("3")
    schedule_list.append(dow3f)
    schedule_list.append(dow3t)
    dow4f=raw_input("input dow 4 start time:")
    dow4t=raw_input("input dow 4 stop time:")
    schedule_list.append("4")
    schedule_list.append(dow4f)
    schedule_list.append(dow4t)
    dow5f=raw_input("input dow 5 start time:")
    dow5t=raw_input("input dow 5 stop time:")
    schedule_list.append("5")
    schedule_list.append(dow5f)
    schedule_list.append(dow5t)
    dow6f=raw_input("input dow 6 start time:")
    dow6t=raw_input("input dow 6 stop time:")
    schedule_list.append("6")
    schedule_list.append(dow6f)
    schedule_list.append(dow6t)
    dow7f=raw_input("input dow 7 start time:")
    dow7t=raw_input("input dow 7 stop time:")
    schedule_list.append("7")
    schedule_list.append(dow7f)
    schedule_list.append(dow7t) 
    dist_schedule[schedule_id]=schedule_list
    schedule_list=[]
    print dist_schedule 
  else:
    pass
  
  if user_input=="4":
    dist_schedule_str=str(dist_schedule)
    print dist_schedule_str.replace("[","SCHEDULE [")
  else:
    pass

  if user_input=="5":
    role_id=raw_input("please input role id:")
    while user_input != "q":     
      gate_id=raw_input("please input gate id:")
      schedule_id=raw_input("please input schedule id:")
      gate_schedule_id_list.append(gate_id)
      gate_schedule_id_list.append(schedule_id)
      user_input=raw_input("press 'q' for exit or 'enter' for next gate id and schedule data registration:")
    dist_role_alowed_gate[role_id]=gate_schedule_id_list
    gate_schedule_id_list=[]
    print dist_role_alowed_gate
  else:
    pass

  if user_input=="6":
    schedule_id=raw_input("please input schedule id for delete:")
    if schedule_id in dist_schedule:
      del dist_schedule[schedule_id]
      print "schedule deleted"
    else:
      print"schedule not found"
 
  if user_input=="7":
    card_id=raw_input("please input card id number for delete:")  
    if card_id in  dist_et_role:
      del dist_et_role[card_id]
      print "card data deleted"
    else:
      print "card id not found"

  if user_input=="8":
    role_id=raw_input("please input role id for delete:")  
    if role_id in dist_role_alowed_gate:
      del dist_role_alowed_gate[role_id]
      print "role data deleted"
    else:
      print "role id not found"

  if user_input=="9":
    card_data_list.append(dist_et_role)
    card_data_list.append(dist_role_alowed_gate)
    card_data_list.append(dist_schedule)
    print card_data_list
    f=open("card_data.dat","wb")
    pickle.dump(card_data_list,f)
    f.close()
    print "data saved"
    user_input="exit and not save"
    continue
  else:
    pass  

  user_input=raw_input("Please press(1-9):")
  





