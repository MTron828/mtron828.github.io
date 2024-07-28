import json
import bcrypt

def loadJson(file):
    txt = ""
    with open(file, "r") as f:
        txt = f.read()
    return json.loads(txt)

def storeJson(file, data):
    txt = json.dumps(data)
    with open(file, "w") as f:
        f.write(txt)

def getUserData(user):
    data = loadJson("./users.json")
    if user in data:
        return data[user]
    else: return None

def setUserData(user, userData):
    data = loadJson("./users.json")
    data[user] = userData
    storeJson("./users.json", data)

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def checkPassword(user, password):
    data = getUserData(user)
    return data and check_password(password, data["password"])

def setPassword(user, password):
    hashed = hash_password(password)
    data = getUserData(user)
    data["password"] = hashed
    setUserData(user, data)

def newUser(name, password):
    if (getUserData(name)):
        return
    data = {
        "username":name,
        "password":hash_password(password),
        "stacks":[],
        "trash":[]
    }
    setUserData(name, data)

def inStack(user, id):
    data = getUserData(user)
    stack = data["stack"]
    trash = data["trash"]
    stack = stack[len(stack)-1]
    trash = trash[len(trash)-1]
    for v in stack:
        if id in v:
            return True 
    return False
