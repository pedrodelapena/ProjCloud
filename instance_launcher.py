import boto3
import time
#globals
global ownername, security_group_id

#amazon stuff 
credentials = boto3.Session().get_credentials()
ec2 = boto3.resource('ec2', aws_access_key_id=credentials.access_key, aws_secret_access_key=credentials.secret_key,region_name='us-east-1')
client = boto3.client('ec2', region_name='us-east-1')

#waiters
waiterterm = client.get_waiter('instance_terminated')
waiterip = client.get_waiter('instance_running')

#read public key
f = open("id_rsa.pub","r") #change this to yours to use your own amazon account
pubkey = f.read()
f.close()

#user input
ownerName = "pedro" #this is used to filter instances by tag (in case you share accounts with someone else)
keyPair = "pedro" #this is the name of your keypair
secGroupName = "APS_Pedro" #this is used to filter instances by tag (in case you share accounts with someone else)
loadBalancerTag = "pedro_lb" #this is used to filter instances by tag, differs load balancer from other instances

#functions
def import_key_pair(yourkeyname):

    global ownername

    #filters + terminates old instances from the same owner
    terminatingList = []

    response = client.describe_instances()
    full_info_instances = list(response.values())[0] 
    for instances_group in full_info_instances: 
        instances = instances_group["Instances"]
        for i in instances:
            if (i["State"]["Code"] == 16): #checks if instance is actually running
                for j in i["Tags"]: 
                    if(j["Key"] == "owner" and (j["Value"] == ownerName or j["Value"] == loadBalancerTag)): #filters by owner so it doesn't kill unwanted instances
                        print("Terminating old instance - id: " + str(i["InstanceId"]))
                        terminatingList.append(i["InstanceId"]) #instance to the doomlist adds to the list
                        client.terminate_instances(InstanceIds=[i["InstanceId"]]) #kills the instance

    if len(terminatingList) > 0:
        waiterterm.wait(InstanceIds=terminatingList) #waiting for instances to be terminated so we can generate new ones
        print("Instance(s) terminated")

    try:  
        client.delete_key_pair(DryRun=False, KeyName=yourkeyname) #delete
        client.import_key_pair(DryRun=False, KeyName=yourkeyname, PublicKeyMaterial=pubkey) #generate
        ownername = yourkeyname
    except:
        print("uh")

def create_sec_group(): #previously with sec_group_name and description
    global security_group_id
    response = client.describe_vpcs()
    vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')
    try:
        client.delete_security_group(GroupName=secGroupName)
    except:
        print("Creating Security Group")

    response = client.create_security_group(GroupName=secGroupName, Description="APS msm", VpcId=vpc_id)

    security_group_id = response['GroupId']

    client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
            'FromPort': 80,
            'ToPort': 80,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
            'FromPort': 5000,
            'ToPort': 5000,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])

        
def create_instance(numinst):
    if (numinst <= 0):
        print("Invalid number of instances!")
        return

    tags = [{'Key': 'owner', 'Value': ownerName},]
    tag_specification = [{'ResourceType': 'instance', 'Tags': tags},]

    ec2.create_instances(ImageId='ami-0ad07225144f2e444',
    InstanceType = "t2.micro", 
    SecurityGroupIds= [security_group_id,],
    KeyName = keyPair, 
    MinCount=numinst, 
    MaxCount=numinst,     
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

    tags = [{'Key': 'owner', 'Value': loadBalancerTag},]
    tag_specification = [{'ResourceType': 'instance', 'Tags': tags},]

    ec2.create_instances(ImageId='ami-0ad07225144f2e444',
    InstanceType = "t2.micro", 
    SecurityGroupIds= [security_group_id,],
    KeyName = keyPair, 
    MinCount=1, 
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
    sudo snap install aws-cli --classi
    git clone https://github.com/pedrodelapena/projcloud
    """)


#-------------------------- END FUNCTIONS ----------------------------------
      
#running instance list
running_instances = ec2.instances.filter(Filters=[{
'Name': 'instance-state-name',
'Values': ['pending','running']}])

instqt = int(input("Insert the number of instances: "))
import_key_pair(keyPair)

print("Successfully added KeyPair name")
print("Updating Security Group")
create_sec_group()

print("Creating instance(s)")
create_instance(instqt)

tempIds = []
tempInstances = []
print("Waiting for IPv4")
time.sleep(3)

for i in running_instances:
    for tag in i.tags:
        if 'Name'in tag['Key']:
            name = tag['Value']
    if i.key_name == keyPair:
        tempIds.append(i.instance_id)
    
waiterip.wait(InstanceIds=tempIds)

#print(client.describe_instances(InstanceIds=[j],))
        
print("Instance(s) sucessfully launched!")

#print(ec2info.items())
