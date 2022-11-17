# FLASK Tutorial 1 -- We show the bare-bones code to get an app up and running

# imports
import os  # os is used to get environment variables IP & PORT
from flask import Flask  # Flask is the web app that we will customize
from flask import render_template
from flask import request, session
from flask import redirect, url_for 
from model import Todo
from database import db
from flask_socketio import SocketIO 
from model import Todo as Todo
from model import Project as Project
from model import User as User



app = Flask(__name__)  # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///velox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
# chat secret key
app.config['SECRET_KEY'] = 'chatsecret'
# New project secret key
app.config['SECRET_KEY'] = 'SE3155'
socketio = SocketIO(app)

#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)

# Setup models
with app.app_context():
    db.create_all()   # run under the app context

# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page)
@app.route('/main')
def main():
    a_user = db.session.query(User).filter_by(email='chill117@uncc.edu')
    my_projects = db.session.query(Project).all()
    return render_template('main.html', notes = my_projects, user = a_user)

@app.route('/main/new', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        title = request.form["title"]
        text = request.form["projectText"]
        from datetime import date
        today = date.today()
        today = today.strftime("%m-%d-%Y")
        newProject = Project(title, text, today, session['user_id'])
        db.session.add(newProject)
        db.session.commit()
        return redirect(url_for('main'))
    else:
        a_user = db.session.query(User).filter_by(email='chill117@uncc.edu')
        return render_template('new.html', user = a_user)

@app.route('/main/delete/<project_id>', methods=['POST'])
def delete_project(project_id):
    my_project = db.session.query(Project).filter_by(id=project_id).one()
    db.session.delete(my_project)
    db.session.commit()
    return redirect(url_for('main'))
    
@app.route('/main/edit/<project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if request.method == 'POST':
        title = request.form['title']
        text = request.form['projectText']
        project = db.session.query(Project).filter_by(id=project_id).one()
        project.title = title
        project.text = text
        db.session.add(project)
        db.session.commit()

        return redirect(url_for('main'))
    else:
        a_user = db.session.query(User).filter_by(email='chill117@uncc.edu').one()
        my_project = db.session.query(Project).filter_by(id=project_id).one()
        return render_template('new.html', project=my_project, user = a_user)

@app.route('/chat')
def sessions():
    return render_template('chat.html')

def messageReceived(methods=['GET', 'POST']):
    print('message was received!!!')

@socketio.on('my event')
def handle_my_custom_event(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    socketio.emit('my response', json, callback=messageReceived)








app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)), debug=True)

# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000/index

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.