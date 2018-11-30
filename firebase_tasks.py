import sys
import requests
import json

endpoint = "http://<loadbalancer_ip>:5000/task/" #change this to the loadbalancer ip

if (sys.argv[1]) == "tarefa adicionar": 
    data = {"title": sys.argv[2], "description": sys.argv[3]}
   
    req = requests.post(endpoint, json = data)
    print(req.text)

elif (sys.argv[1]) == "tarefa listar":
    req = requests.get(endpoint)
    print(req.text)
