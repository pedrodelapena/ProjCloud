from flask import Flask, url_for, request, redirect
import requests
import boto3
import random
from threading import Timer

#gotta import user credentials nicely, till then this might do

global secGroupID, instanceQT

ownerName = "pedro" #change this to your owner tag value
keyPair = "pedro" #change this to your keypair
secGroupName = "APS_Pedro" #change this to your secgroup 
secGroupID= ""
instanceQT = 3 #change this to the amount of instances you desire

#boto3 to ec2 stuff (run aws configure)
credentials = boto3.Session().get_credentials()
ec2_resource = boto3.resource('ec2', aws_access_key_id=credentials.access_key, aws_secret_access_key=credentials.secret_key,region_name='us-east-1')
client = boto3.client('ec2', region_name='us-east-1')

#waiters
waiterterm = client.get_waiter('instance_terminated')
waiterip = client.get_waiter('instance_running')
waiterstatus = client.get_waiter('instance_status_ok')

#Available Instance dictionary 
instDict = {} 
instIps = list(instDict.values())

#easy running instances check
running_instances = ec2_resource.instances.filter(Filters=[{ 
'Name': 'instance-state-name',
'Values': ['pending','running']}])

def list_instances():
    try:
        global secGroupID#this is required to launch new instances that belong to the same security group as the currently running ones

        #bilipe forba is my savior, for real
        response = client.describe_instances()
        full_info_instances = list(response.values())[0]  #this is a big dictionary
        for instances in full_info_instances:
            inst = instances["Instances"] #getting small but still big instance info
            for i in inst:
                if (i["State"]["Code"] == 16): #checks if the instance is actually running
                    for j in i["Tags"]:
                        if(j["Key"] == "owner" and j["Value"] == ownerName): #guarantees that you're getting the right instances
                            instDict[i["InstanceId"]] = i["PublicIpAddress"] #adds the id and ip to the available instances list

                    for g in i["SecurityGroups"]:
                        if g["GroupName"] == secGroupName: #checks if the instance security group is the expected one
                            secGroupID= g["GroupId"] #gets the group id so we can use it to generate new instances
                            #print("Sec group " + secGroupID)
    except:
        print("Failed to list instances, please check your internet connection")  

def healthchecker(): #healthcheck thread
    global instanceQT
    instIps = list(instDict.values()) #current ips on the dictionary

    for i in instIps:
        try:
            response = requests.get("http://" + i + ":5000/healthcheck", timeout=7) #waits 7 secs max, else it kills the instance
            print("IP " + i + " - status: " + str(response.status_code))
            #instCounter +=1
        except:
            print("IP "+ i + " is dead, rest in pepperoni")
            for inst_id, inst_ip in instDict.items():  #k,v in dict
                if i == inst_ip: #finds the malfunctioning ip
                    temp_id = inst_id 

            instDict.pop(temp_id) #don't change the size of it while you're iterating over it11!!1!! (this caused me problems)
            terminate_intances(temp_id) #deletes the malfunctioning instances...
            create_instances() #then creates a new ones!
            
    if (len(instIps) < instanceQT):
        loadbalancer()

    print("-----------")
    Timer(10, healthchecker).start() #loop thread

def terminate_intances(term_id):
    
    print("Terminating instance - id: " + term_id)
    try:
        client.terminate_instances(InstanceIds=[term_id])
        print("Instance terminated")
    except:
        print("Termination failed")

def create_instances():
    global secGroupID,instanceQT
    list_instances()
    currentInstances = len(instDict)
    neededInstances = instanceQT - currentInstances
    print("Instances needed: " + str(neededInstances) + "\n")

    try:
        newTempIds = []
        for i in range(neededInstances): #could be done in a different way, but like this it's better to get them all waiting at the same time
            tags = [{'Key': 'owner', 'Value': ownerName},]
            tag_specification = [{'ResourceType': 'instance', 'Tags': tags},]

            newInst = client.run_instances(ImageId='ami-0ad07225144f2e444',
            InstanceType = "t2.micro", 
            SecurityGroupIds=[secGroupID,],
            KeyName = keyPair, 
            MinCount=1, #I mean, I could've put the number of required instances right here
            MaxCount=1,     
            TagSpecifications=tag_specification,
            UserData = """#!/bin/bash
                sudo apt-get -y update 
                sudo apt-get install -y python3-pip
                sudo pip3 install flask
                sudo pip3 install boto3
                sudo pip3 install pyrebase
                sudo pip install pyrebase
                sudo pip3 install flask_restful
                git clone https://github.com/pedrodelapena/projcloud
                cd / 
                cd projcloud
                python3 firebase_api.py
            """)

            #------------

            print("Instance created! Waiting till it is ready")
            newInstId = newInst["Instances"][0]["InstanceId"] #gets the id out of the info dictionary
            print("New instance id " + newInstId)
            newTempIds.append(newInstId)

        print("Waiting till new instance(s) is(are) running!")
        waiterip.wait(InstanceIds=newTempIds) #waits till the instance(s) is(are) running
        print("Waiting till new instance(s) is(are) done initializing! This can take a while...")
        waiterstatus.wait(InstanceIds=newTempIds) #waits till the instance(s) is(are) done initializing (checks 2/2)
        list_instances() #refreshes running instances and adds then new id/ip(s) to the instance dictionary
        print(instDict)

    except:
        print("Instance creation failed")

def loadbalancer():
    print("\n")
    global instanceQT
    print("Provisioning new instances till we get to "+ str(instanceQT)+ "!")
    list_instances()
    currentInstances = len(instDict)
    print("Current instances: " + str(currentInstances))
    create_instances()


#flask
app = Flask(__name__)

@app.route('/', defaults={'path': ''}, methods = ["POST", "GET", "PUT", "DELETE"])
@app.route('/<path:path>',methods=["GET", "POST", "PUT", "DELETE"])

def catch_all(path): #loadbalancer
    ip = random.choice(list(instDict.values())) #picks random available ip]
    return redirect("http://" + ip + ":5000/task/") #redirects you to a random available ip

#-------------------------- END FUNCTIONS ----------------------------------

list_instances()
initCheck = []
for i in instDict.keys():
    initCheck.append(i)

print("Before we start, lets make sure every instance is running properly!")
print("This might take a while if you have just created the instances\n")
waiterstatus.wait(InstanceIds=initCheck)
list_instances()
print("Current instances in dictionary")
print(instDict)
print("\n")
Timer(10, healthchecker).start()
app.run( port = 5000, host = '0.0.0.0')
