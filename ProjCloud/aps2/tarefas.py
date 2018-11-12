import requests
import json
import sys

global endpoint
endpoint = 'http://127.0.0.1:5000/'

def AddTask(content): #adicionar
    content_dict = {'name': content}
    r = requests.post(endpoint + 'task', data=json.dumps(content_dict))
    print("Content added!")

def ListTasks(): #listar
    r = requests.get(endpoint + 'task')
    print(r.text)

def SearchTask(id): #buscar
    r = requests.get(endpoint + 'task/' + str(id))
    print(r.text)

def DelTask(id): #deletar
    r = requests.delete(endpoint + 'task/' + str(id))
    print("Task " + str(id) + " deleted!")

def UpdateTask(id, content): #atualizar
    r = requests.put(endpoint + 'task/' + str(id), data=json.dumps({'name': content}))
    print("Content updated!")

def main():
    inputSys = sys.argv
    methodList = ["help", "add", "list", "search", "delete", "update"]

    if (len(inputSys) > 1) and (inputSys[1] in methodList):
        if inputSys[1] == methodList[0]: #help
            print("""
Command list: \n
help - Shows this duh \n
add - Adds a task to the list - input format -> add <content> \n
list - Lists all stored tasks - input format -> list \n
search - Selects task based on id - input format -> search <id> \n
delete - Deletes task based on id - input format -> delete <id> \n
update - Updates task content based on id - input format -> update <id> <content>
            """)

        elif inputSys[1] == methodList[1]: #add
            try:
                AddTask(inputSys[2])
            except:
                print("Invalid arguments")
        
        elif inputSys[1] == methodList[2]: #list
            try:
                ListTasks()
            except:
                print("Invalid arguments")

        elif inputSys[1] == methodList[3]: #search
            try:
                SearchTask(inputSys[2])
            except:
                print("Invalid arguments")
        
        elif inputSys[1] == methodList[4]: #delete
            try:
                DelTask(inputSys[2])
            except:
                print("Invalid arguments")
            
        elif inputSys[1] == methodList[5]: #update
            try:
                UpdateTask(inputSys[2], inputSys[3])
            except:
                print("Invalid arguments")

    else:
        print("Invalid command")

if __name__ == "__main__":
    main()