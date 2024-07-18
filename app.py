from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import User
from users import *

app = Flask(__name__)
app.secret_key = 'replace_with_a_strong_secret_key'

# Initialize extensions
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)


@login_manager.user_loader
def load_user(username):
    return User(username, username, getUserData(username)["password"])

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if checkPassword(username, password):
            user = User(username, username, getUserData(username)["password"])
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password!', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=current_user.username)

@app.route('/get_stack', methods=['POST'])
@login_required
def get_stack():
    """print("I am a post")
    if request.form:
        print("I have form data")
        #print(request.form['kommentar'])
    if request.data:
        print("I have data")
    if request.json:
        print("I have json")
        # Do stuff with the data...
        return jsonify({"message": "OK"})
    else:
        print("fail")"""
    user = current_user.username 
    data = getUserData(user)
    #print(request.json)
    stack_name = request.json.get("stack_name")
    stack_type = stack_name.split("_")[0]
    stack_idx = int(stack_name.split("_")[1])
    txt = json.dumps(data[stack_type][stack_idx])
    return txt

@app.route('/info', methods=['POST'])
@login_required
def get_info():
    user = current_user.username 
    req = request.json
    req_arr = req.get("req_arr")
    id = req.get("id")
    res = {}
    if "novelName" in req_arr:
        res["name"] = getNameFromId(id)
    if "chapterCount" in req_arr:
        res["chapters"] = getChapterCount(id)
    if "description" in req_arr:
        res["description"] = getNovelDescription(id)
    if "tags" in req_arr:
        res["tags"] = getNovelTags(id)
    return json.dumps(res)

@app.route('/info', methods=['POST'])
@login_required
def get_recomendations():
    user = current_user.username 
    req = request.json
    

@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    username = current_user.username
    password = request.form.get("password")
    new_password = request.form.get("new_password")
    if (checkPassword(username, password)):
        setPassword(username, new_password)
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)