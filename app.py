from flask import Flask, Blueprint, render_template, get_template_attribute, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import User
from users import *
from novels import *
from utility import *
from werkzeug.routing import BaseConverter
from markupsafe import Markup
import novelbin_scrapper
import threading

class BooleanConverter(BaseConverter):
    def __init__(self, url_map):
        super().__init__(url_map)
        self.regex = 'true|false|1|0|yes|no|y|n'

    def to_python(self, value):
        if value.lower() in ['true', '1', 'yes', 'y']:
            return True
        elif value.lower() in ['false', '0', 'no', 'n']:
            return False
        else:
            raise ValueError(f"Invalid boolean value: {value}")

    def to_url(self, value):
        return 'true' if value else 'false'


app = Flask(__name__)
app.url_map.converters['bool'] = BooleanConverter
app.secret_key = 'replace_with_a_strong_secret_key'

app.static_folder = 'static'

img_bp = Blueprint('imgs', __name__, static_folder='imgs', static_url_path='/webnovel/imgs')
app.register_blueprint(img_bp)

# Initialize extensions
login_manager = LoginManager(app)
login_manager.login_view = 'login'
bcrypt = Bcrypt(app)

@login_manager.user_loader
def load_user(username):
    return User(username, username, getUserData(username)["password"])

@app.route('/webnovel/')
def index():
    return redirect(url_for('home'))

@app.route('/webnovel/login', methods=['GET', 'POST'])
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

@app.route('/webnovel/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/webnovel/home')
@login_required
def home():
    user = current_user.username
    user_data = getUserData(user)
    novel_data = getNovelData()
    return render_template('home.html', user_data = user_data, novel_data = novel_data)

@app.route('/webnovel/search_result', methods=['GET', 'POST'])
def search_results():
    user = current_user.username
    req = {}
    if request.method == "GET":
        req = request.args 
    elif request.method == "POST":
        req = request.json 
    else:
        return "Error! No query provided for search."
    
    res = []
    string = req.get("string")

    if "title" in req.get("methods"):
        tres = searchTitles(string)
        res = addNotPresent(res, tres) 
    if "tags" in req.get("methods"):
        tres = searchTags(string)
        res = addNotPresent(res, tres)  
    if "description" in req.get("methods"):
        tres = searchDescriptions(string)
        res = addNotPresent(res, tres)  
    if "embbeding" in req.get("methods"):
        pass #TODO
    if "aiTags" in req.get("methods"):
        pass #TODO
    if "aiDescription" in req.get("methods"):
        pass #TODO
    if "aiDescriptionEmbbeding" in req.get("methods"):
        pass #TODO
    
    if "minChapters" in req:
        minChaps = req.get("minChapters")
        res = [x for x in res if minChaps <= getChapterCount(x)]
    if "tagExpression" in req:
        nres = []
        tagExp = req.get("tagExpression") 
        # tag expression example:
        # 'a' & 'b' & (!'c' | 'd')
        # recursive evaluation
        for i in res:
            if evaluateTagExpression(i, tagExp):
                nres.append(i)
        
        res = nres
    
    novel_data = getNovelData()

    stack = getUserData(user)["stack"][-1]

    for i in range(len(novel_data)):
        novel_data[i]["inStack"] = False
    for st in stack:
        for el in st:
            novel_data[el]["inStack"] = True

    return render_template("search_results.html", string=string, results=res, novel_data = novel_data)
    

@app.route('/webnovel/get_stack', methods=['POST'])
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
    try:
        txt = json.dumps(data[stack_type][len(data[stack_type])-1][stack_idx])
        return txt
    except:
        return json.dumps([])

@app.route('/webnovel/update_stack', methods=['POST'])
@login_required
def update_stack():
    user = current_user.username 
    data = getUserData(user)
    stacks = request.json.get("stacks")
    trashes = request.json.get("trashes")
    data["stack"].append(stacks)
    data["trash"].append(trashes)
    setUserData(user, data)

@app.route('/webnovel/novels/<int:novel_id>/')
@login_required
def get_novel(novel_id):
    novel_data = getNovelData()[novel_id]
    return render_template("novel.html", novel_data = novel_data, len = len, zip = zip)

@app.route('/webnovel/novels/<int:novel_id>/chapters/<bool:ai_generated>/<int:chapter_id>')
@login_required
def get_chapter(novel_id, chapter_id, ai_generated):
    novel_data = getNovelData()[novel_id]
    txt = ""
    script = ""
    #print(ai_generated)
    if not ai_generated:
        txt = getNovelChapter(novel_id, chapter_id)
        novelbin_scrapper.addScrapChapters(novel_data["name"], chapter_id, 10)
        if not txt:
            txt = "Waiting for autoscrapper to download chapter...\n"
            txt += "Meanwhile, you can visit the chapter in it's <a href = '{0}'>original source</a>.".format(getNovelLinks(novel_id)[chapter_id])
            txt = Markup(txt)
            script = """
            <script>
                setTimeout(()=>{
                    window.location.reload();
                }, 5000);
            </script>
            """
    else:
        txt = getAiGeneratedNovelChapter(novel_id, chapter_id)
        if not txt:
            txt = "Automatic ai generation is a work in progress."
    return render_template("chapter.html", txt=txt, script=script, novel_data = novel_data, chapter_id=chapter_id, novel_id=novel_id, ai_generated=ai_generated)


@app.route('/webnovel/novel_info', methods=['POST'])
@login_required
def get_novel_info():
    user = current_user.username 
    req = request.json
    req_arr = req.get("req_arr")
    id = req.get("id")
    res = {}
    if "novelName" in req_arr:
        res["name"] = getNameFromId(id)
    if "chapterCount" in req_arr:
        res["chapters"] = getChapterCount(id)
    if "aiChapterCount" in req_arr:
        res["aiChapters"] = getAiChapterCount(id)
    if "description" in req_arr:
        res["description"] = getNovelDescription(id)
    if "tags" in req_arr:
        res["tags"] = getNovelTags(id)
    if "preview" in req_arr:
        novel_data = getNovelData()[id]
        if "showAddToStackButton" in req_arr:
            novel_data["inStack"] = inStack(user, id)
        novel_preview = get_template_attribute('novel_preview.html', 'novel_preview')
        res["preview"] = novel_preview(novel_data)
    return json.dumps(res)

@app.route('/webnovel/add_to_stack', methods=['POST'])
@login_required
def add_to_stack():
    user = current_user.username 
    req = request.json 
    novel_id = req["novel"]
    if inStack(user, novel_id):
        return "alredy in stack"
    data = getUserData(user)
    current_stack = data["stack"][-1]
    current_trash = data["trash"][-1]
    new_trash = []
    for trash in current_trash:
        new_trash.append([])
        for el in trash:
            if el != novel_id:
                new_trash[-1].append(el)
    data["trash"].append(new_trash)
    new_stack = []
    added = False
    for stack in current_stack:
        new_stack.append([])
        if not added:
            new_stack[-1].append(novel_id)
            added = True
        for el in stack:
            if el != novel_id:
                new_stack[-1].append(el)
    data["stack"].append(new_stack)
    setUserData(user, data)
    return "ok"

@app.route('/webnovel/recomendations', methods=['POST'])
@login_required
def get_recomendations():
    user = current_user.username 
    req = request.json
    string = req.get("string")
    res = []
    if "title" in req.get("types"):
        tres = searchTitles(string)
        res = addNotPresent(res, tres) 
    if "tags" in req.get("types"):
        tres = searchTags(string)
        res = addNotPresent(res, tres)  
    if "description" in req.get("types"):
        tres = searchDescriptions(string)
        res = addNotPresent(res, tres)  
    if "embbeding" in req.get("types"):
        pass #TODO
    if "aiTags" in req.get("types"):
        pass #TODO
    if "aiDescription" in req.get("types"):
        pass #TODO
    if "aiDescriptionEmbbeding" in req.get("types"):
        pass #TODO
    return json.dumps(res)
    

@app.route('/webnovel/change_password', methods=['POST'])
@login_required
def change_password():
    username = current_user.username
    password = request.form.get("password")
    new_password = request.form.get("new_password")
    if (checkPassword(username, password)):
        setPassword(username, new_password)
    return redirect(url_for("home"))

@app.route('/webnovel/restart_server')
@login_required
def restart_server():
    os.system("shutdown /f /g /t 0")

if __name__ == '__main__':
    scrapper = None
    server = None
    try:
        scrapper = threading.Thread(target = novelbin_scrapper.scrap)
        scrapper.daemon = True
        scrapper.start()
        def run_server():
            app.run(debug=False, port=5000)
        server = threading.Thread(target = run_server)
        server.daemon = True
        server.start()
        server.join()
        scrapper.join()
    finally:
        novelbin_scrapper.driver.quit()
