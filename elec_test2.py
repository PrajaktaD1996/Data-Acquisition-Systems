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
    response = client.insert({"doctype":"IOT Raw Log","data":""+data+"","timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"iot_session":session})
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
    command1 = '<A,ABOUT>'
    command2 = '<A,SAMPLE>'
    command3 = '<A,HEADER>'
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
        s_port = ser.Serial("/dev/ttyUSB0",9600,timeout=4)
        s_port.write(command2.encode())

        if  detect_start_press():
            if  client ==  None:
               break;                                              
            try:
                
                s_port.write(command2.encode())
                print("vital data")
                ser_data = s_port.readlines()   ##
                x = str(ser_data).split('\\t')
                print(x)
                print(len(x))
                print("\n")
                
                s_port.write(command3.encode())
                print("abt vital data")
                abt_data = s_port.readlines()   ##
                y = str(abt_data).split('\\t')
                print(y)
                print(len(y))
                print("\n")

                res = dict(map(lambda i,j : (i,j) , y,x))
                #print(res)
                str_res = str(res).replace('\'','').replace('"','')
                #print(str_res)
                s = "".join(sum(map(list,str_res),[]))
                print(s)
                print(len(s))

                #print(s)
                #print(len(s))

                #st = "EUT data"
                #print(len(st))
        
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
                output = insert_log(client,session_doc["name"],abt_data)   #data_split

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
        time.sleep(3)
