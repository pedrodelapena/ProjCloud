import os
from flask import Flask, render_template, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal, abort

from pyrebase import pyrebase

app = Flask(__name__)
api = Api(app)

#json config
config = {
    "apiKey": "AIzaSyAwIa1N5DbbCGjhqUiDgkXXpKctf_ELS0g",
    "authDomain": "stateless-b8501.firebaseapp.com",
    "databaseURL": "https://stateless-b8501.firebaseio.com",
    "projectId": "stateless-b8501",
    "storageBucket": "stateless-b8501.appspot.com",
    "messagingSenderId": "747828869830"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#old api but updated so it can only do posts and gets
class Tarefa(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required = True, help='Missing arguments', location='json')
        self.reqparse.add_argument('description', type=str, default = "", location='json')
        super(Tarefa, self).__init__()
        
    def get(self):
        print(db.get())
        return db.child("Tarefa").get().val()
                                   
    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'title': args['title'],
            'description': args['description']
        }
        db.child("Tarefa").set(task)
        return db.child("Tarefa").get().val()

@app.route('/healthcheck/', methods = ['GET']) 
def healthcheck():
    return 'still alive', 200

api.add_resource(Tarefa, '/task/', endpoint='tasks')

if __name__ == "__main__":
    app.run(debug = True, port = 5000, host = "0.0.0.0")

