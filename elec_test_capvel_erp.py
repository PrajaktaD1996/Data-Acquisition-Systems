#!/usr/bin/python3

################################################
#Date: 29-6-23
#elec_test2.py
#Edit_code_____elec_test.py
################################################                  
from frappe_client.frappeclient import FrappeClient
from frappe_client import auth                            
from datetime import datetime
import serial as ser
import time
import os
import signal
##import resilience as res
import logging
#import RPi.GPIO as GPIO
#GPIO.setwarnings(False)
#GPIO.setmode(GPIO.BOARD)
#GPIO.setup(13,GPIO.IN,pull_up_down=GPIO.PUD_UP)
#GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_UP)
input1=13
input2=18

def detect_start_press():
    #use gpio check when enter is pressed
    return True

def detect_device(ser):
    return Device()

##def get_device_template(device):
    #get item qualiyt inspection template from ERPNext
    ##template_name = client.get_value("Item", "quality_inspection_template",device.item_code)
    ##template = None
    ##if template_name :
        ##template = client.get_doc("Quality Inspection Template", template_name['quality_inspection_template'])

    ##return template

def create_serial_comm(s_port):
    if s_port != None:
        if s_port.isOpen():
            return s_port
        else:
            try:
                s_port = ser.Serial(name+str(i), 9600, timeout=2)
                if s_port.isOpen():
                    return s_port
                #else:
            except:
                print("not able to create port")
    return None
#def validate_results(device, param):
    #return True
#def test_paramter(device, param):
    #return

def create_session(product_group,client,session_id,description = "Test Log"):
    session_doc = { "doctype":"IOT Session",
                    "product":product_group,
                    "start_time": datetime.now().strftime("%Y-%m-%d %H:%H:%S"),
                    "description":description
                 }
    try:
        return client.insert(session_doc)
    except:
        logging.info("Could not create session")
        return None

def get_session(session_id,client):
    session = None
    try:
        session =  client.get_doc("IOT Session",session_id)
        return session
    except:
        logging.info("No session by the given name")
        return None
    
def insert_log(client,session,data):
    response = client.insert({"doctype":"IOT Raw Log","data":data,"data":"'" + data + "'","timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"iot_session":session})
    return response


if __name__ == "__main__":
    ##res.intiate_logging()
    #client = c.create_client(auth.url, api_key = auth.api_key, api_secret = auth.api_secret)    
    client = FrappeClient(auth.url, api_key = auth.api_key, api_secret = auth.api_secret)      
    assert client is not None                                                                   
    REBOOT_MAX = 50
    reboot_ctr = REBOOT_MAX

######### user config ####################
    sleep_time_s =60 
    product_group = "Product-Capvel VAT"
    #command = '<A,SAMPLE>'
    command = '<A,OUTPUT?,45890>'
    session_descripton  = "Testing new firmware version 1.0"
    baud_rate = 9600
    session_id =  "IS-00027" #if set to none, a new session is created
    print_output = False
#############################################

    s_port = None
    session_doc = None                                                                         
    session_doc = get_session(session_id, client)                                           
    if session_doc == None or "name" not in session_doc:                                       
        session_doc = create_session(product_group, client,session_id, session_descripton)     

#    assert session_doc["name"] != None                                                         
###############################################  write simple while.....                                    
    while True and client != None:
        s_port = ser.Serial("/dev/ttyUSB1",9600,timeout=4)
        s_port.write(command.encode())
        if  detect_start_press():
            if  client ==  None:
               break;

           ##s_port = create_serial_comm(s_port)  ###
            #assert s_port != None     ##                                                        
            #if command is not None:                                                           
                #s_port.write(command)                                                           
            try:
                
                s_port.write(command.encode())
                print("reading vital data")
                ser_data = s_port.readlines()   ##
                print("ser_data")
                #print("converting to string and replacing unicodes")
                str_data=str(ser_data)#.replace('\\t',',').replace(':','-').replace('<','').replace("['",'') ## creating issue here 
                #print("Splitting the data")
                data_split=str_data.split('>')  ##                  data stopped here
                print("data split")
                print(data_split)
                #print("adding input1 and input 2")
                #packet_data=data_split[0]+','+input1_state +','+input2_state ##
                #final_packet=''.join(map(str,packet_data))  ##
                #print(final_packet)
                #check=len(final_packet)   ##
                #print("length of final packet",check)  #creating trap not pushing data here if it is not commented
                client = FrappeClient(auth.url, api_key = auth.api_key, api_secret = auth.api_secret)

            except:
                print(Exception)   ##
                print("exception")
                s_port.close()    ##
                #s_port = create_serial_comm(s_port) ##
                continue
            try:
                print("inserting log")
                #output = insert_log(client,session_doc["name"],str(final_packet))
                output = insert_log(client,session_doc["name"],str(str_data))   #data_split
                if print_output:
                    logging.info(output)
            except:
                print(Exception)
                logging.info("could not insert log")
                #client = c.create_client(auth.url, api_key = auth.api_key, api_secret = auth.api_secret)
                client = FrappeClient(auth.url, api_key = auth.api_key, api_secret = auth.api_secret)

                reboot_ctr = reboot_ctr - 1
                if reboot_ctr == round(REBOOT_MAX/2):
                    print('x')
                    ##res.restart_networking("ctr {}".fmt(reboot_ctr))
                elif reboot_ctr == 0:
                    print('y')
                    ##res.reboot("ctr {}".format(reboot_ctr))
                else:
                    reboot_ctr = REBOOT_MAX
        print("sleeping")     
        time.sleep(sleep_time_s)
