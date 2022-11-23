from database import db
import datetime

class User(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(100))
    email = db.Column("email", db.String(100))
    

    def __init__(self, name, email):
        self.name = name
        self.email = email

class Todo(db.Model):
    task_id = db.Column("task_id",db.Integer, primary_key = True)
    name = db.Column("name",db.String(100))
    status = db.Column("status",db.Boolean)

    def __init__(self,name,status):
        self.name = name
        self.status = status

class Project(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    title = db.Column("title", db.String(200))
    text = db.Column("text", db.String(100))
    date = db.Column("date", db.String(50))
#    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __init__(self, title, text, date):
        self.title = title
        self.text = text
        self.date = date
        
   
