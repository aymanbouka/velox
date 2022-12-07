# FLASK Tutorial 1 -- We show the bare-bones code to get an app up and running
# imports
import os  # os is used to get environment variables IP & PORT
from flask import Flask  # Flask is the web app that we will customize
from flask import render_template
from flask import request, session
from flask import redirect, url_for 
from flask import flash
from database import db
from model import Todo as Todo
from model import Project as Project
from model import User as User
from model import Comment as Comment
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send, emit
from forms import RegisterForm, LoginForm, CommentForm, PasswordForm
import bcrypt




app = Flask(__name__)  # create an app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///velox.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['SECRET'] = 'secret!123'
app.config['SECRET_KEY'] = 'SE3155'
socketio = SocketIO(app, cors_allowed_origins = '*')


#  Bind SQLAlchemy db object to this Flask app
db.init_app(app)

# Setup models
with app.app_context():
    db.create_all()   # run under the app context


# @app.route is a decorator. It gives the function "index" special powers.
# In this case it makes it so anyone going to "your-url/" makes this function
# get called. What it returns is what is shown as the web page)
@app.route('/')
@app.route('/velox')
def velox():
    return render_template("landing_page.html")

@app.route('/main')
def main():
    if session.get('user'):
        my_projects = db.session.query(Project).filter_by(user_id=session['user_id']).all()
        return render_template('main.html', project = my_projects, user = session['user'])
    return render_template("landing_page.html")

@app.route('/main/<project_id>')
def get_project(project_id):
    if session.get('user'):
        my_project = db.session.query(Project).filter_by(id=project_id).one()

        form = CommentForm()
    return render_template('project_view.html', project = my_project, user = session['user'], form=form)


@app.route('/main/new', methods=['GET', 'POST'])
def new_project():
    if session.get('user'):  
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
            return render_template('new.html', user = session['user'])

@app.route('/main/delete/<project_id>', methods=['POST'])
def delete_project(project_id):
    my_project = db.session.query(Project).filter_by(id=project_id).one()
    db.session.delete(my_project)
    db.session.commit()
    return redirect(url_for('main'))
    
@app.route('/main/edit/<project_id>', methods=['GET', 'POST'])
def edit_project(project_id):
    if session.get('user'):      
        if request.method == 'POST':
            title = request.form["title"]
            text = request.form["projectText"]
            project = db.session.query(Project).filter_by(id=project_id).one()
            project.title = title
            project.text = text
            db.session.add(project)
            db.session.commit()
            return redirect(url_for('main'))
        else:
            my_project =  db.session.query(Project).filter_by(id=project_id).one()
            return render_template('new.html', project=my_project, user=session['user'])

@app.route("/todo")
def todo():
    todo_list = Todo.query.all()
    print(todo_list)
    return render_template("todo.html", todo_list=todo_list)

@app.route("/todo/add", methods=['GET',"POST"])
def add():
    name = request.form.get("title")
    new_todo = Todo(name=name, status=False)
    db.session.add(new_todo)
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/update/<int:todo_task_id>")
def update(todo_task_id):
    todo = Todo.query.filter_by(task_id=todo_task_id).first()
    todo.status = not todo.status
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/delete/<int:todo_task_id>")
def delete(todo_task_id):
    todo = Todo.query.filter_by(task_id=todo_task_id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("todo"))


@app.route( '/chat' )
def hello():
  return render_template( 'chat.html' )

def messageRecived():
  print( 'message was received!!!' )

@socketio.on( 'my event' )
def handle_my_custom_event( json ):
  print( 'recived my event: ' + str( json ) )
  socketio.emit( 'my response', json, callback=messageRecived )

@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegisterForm()

    if request.method == 'POST' and form.validate_on_submit():
        # salt and hash password
        h_password = bcrypt.hashpw(
            request.form['password'].encode('utf-8'), bcrypt.gensalt())
        # get entered user data
        first_name = request.form['firstname']
        last_name = request.form['lastname']
        # create user model
        new_user = User(first_name, last_name, request.form['email'], h_password)
        # add user to database and commit
        db.session.add(new_user)
        db.session.commit()
        # save the user's name to the session
        session['user'] = first_name
        session['email']= request.form['email']
        session['user_id'] = new_user.id  # access id value from user model of this newly added user
       
        # show user dashboard view
        return redirect(url_for('main'))

    # something went wrong - display register view
    return render_template('signup.html', form=form)

@app.route('/login', methods=['POST', 'GET'])
def login():
    login_form = LoginForm()
    # validate_on_submit only validates using POST
    if login_form.validate_on_submit():
        # we know user exists. We can use one()
        the_user = db.session.query(User).filter_by(email=request.form['email']).one()
        # user exists check password entered matches stored password
        if bcrypt.checkpw(request.form['password'].encode('utf-8'), the_user.password):
            # password match add user info to session
            session['user'] = the_user.first_name
            session['email']= request.form['email']
            session['user_id'] = the_user.id
            # render view
            return redirect(url_for('main'))

        # password check failed
        # set error message to alert user
        login_form.password.errors = ["Incorrect username or password."]
        return render_template("login.html", form=login_form)
    else:
        # form did not validate or GET request
        return render_template("login.html", form=login_form)

@app.route('/logout')
def logout():
    if session.get('user'):
        session.clear()
    return redirect(url_for('main'))

@app.route('/main/<project_id>', methods=['POST'])
def new_comment(project_id):
    if session.get('user'):
        comment_form = CommentForm()
        # validate_on_submit only validates using POST
        if comment_form.validate_on_submit():
            # get comment data
            comment_text = request.form['comment']
            new_record = Comment(comment_text, int(project_id), session['user_id'])
            db.session.add(new_record)
            db.session.commit()

        return redirect(url_for('get_project', project_id=project_id))

    else:
        return redirect(url_for('login'))

@app.route("/main/delete_comment/<project_id>/<comment_id>", methods=['POST'])
def delete_comment(project_id,comment_id):
    delete_comment = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(delete_comment)
    db.session.commit()
    return redirect(url_for('get_project', project_id=project_id))

@app.route('/dashboard', methods=["GET", "POST"])
def dashboard():
    password_form = PasswordForm()
    
    
    return render_template('profile.html', form=password_form)

app.run(host=os.getenv('IP', '127.0.0.1'), port=int(os.getenv('PORT', 5000)), debug=True)



# To see the web page in your web browser, go to the url,
#   http://127.0.0.1:5000/index

# Note that we are running with "debug=True", so if you make changes and save it
# the server will automatically update. This is great for development but is a
# security risk for production.