from flask import Flask, url_for, request, redirect
import json

app = Flask(__name__)
global task_dict, task_id 
task = {} #dict
task_id = 0

class Tarefa():
    def __init__(self, id, name):
        self.id = id
        self.name = name

@app.route('/')
def page():
    return "Claimed by Ninninn"

@app.route('/task', methods = ["POST", "GET"])
def get_insert():
    global task_id
    
    if request.method == "POST":
        content = json.loads(request.data)
        task[task_id] = Tarefa(task_id, content["name"])
        task_id += 1
        return json.dumps({'status': 200}), 200
    else:   
        return json.dumps(task, default = lambda d: d.__dict__)

@app.route('/task/<int:id>', methods = ['DELETE', 'GET', 'PUT'])
def cng(id):

    if request.method == "PUT":
        content = json.loads(request.data)
        print(id, content)

        try:
            task[id].name = content["name"]
            return json.dumps({'status': 200, 'message': "Task updated" }), 200
        except:
            return json.dumps({'status': 404, 'message': "Not found"}), 404

    elif request.method == "DELETE":
        try:
            del task[id]
            return json.dumps({'status': 200, 'message': "[Content Deleted]"}), 200
        except:
            return json.dumps({'status': 404, 'message': "Not found"}), 404
    
    else:
        try:
            data = task[id]
            return json.dumps(data, default = lambda d: d.__dict__)
        
        except:
            return json.dumps({'status': 404}), 404

if __name__ == "__main__":
    app.run(debug = True, port = 5000, host = '0.0.0.0')
