from database import db
import datetime

class Todo(db.Model):
    task_id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))
    status = db.Column(db.Boolean)

    def __init__(self,task_id,name,status):
        self.task_id = task_id
        self.name = name
        self.status = status

    
