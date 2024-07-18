import json
import os
from progress_bar import printProgressBar

json_cache = {}
def loadJson(file):
    if file in json_cache:
        #print(json_cache[file])
        return json_cache[file]
    txt = ""
    with open(file, "r") as f:
        txt = f.read()
    json_cache[file] = json.loads(txt)
    #print(json_cache[file])
    return json_cache[file]

def storeJson(file, data):
    if file in json_cache:
        del json_cache[file]
    txt = json.dumps(data)
    with open(file, "w") as f:
        f.write(txt)

def getIdToName():
    return loadJson("./id_to_name.json")

def setIdToName(arr):
    return storeJson("./id_to_name.json", arr)

def getNameFromId(id):
    names = getIdToName()
    if id < len(names):
        return names[id]
    else:
        return None

def getIdFromName(name):
    names = getIdToName()
    for i in range(len(names)):
        if names[i] == name:
            return i 
    names.append(name)
    setIdToName(names)
    return len(names)-1

def updateNovelsIdsFromNovelJson():
    data = loadJson("./novels/novels.json")
    #print(data)
    for el in data["novels"]:
        print(el["title"], el["id"])
        print(el["title"], getIdFromName(el["title"]))
        if el["id"] != getIdFromName(el["title"]):
            print("Wtf!")
            break

def giveIdsToNovels():
    data = loadJson("./novelbin_data.json")
    for name in data:
        getIdFromName(name)

def getChapterCountNovelbin(id):
    filenum = id//100
    offset = id%100
    file = loadJson("./novelbin_links_{}.json".format(filenum))
    return len(file[offset])

def getAiChapterCountOsPath(id):
    path = "./novels/{}/chapters/ai".format(id)
    if os.path.isdir(path):
        return sum(1 for entry in os.listdir(path) if os.path.isfile(os.path.join(path, entry)))
    else:
        return 0

def getNovelDescriptionNovelbin(id):
    data = loadJson("./novelbin_data.json")
    return data[getNameFromId(id)]["description"]

def getNovelTagsNovelbin(id):
    data = loadJson("./novelbin_data.json")
    return data[getNameFromId(id)]["tags"]  

def precalc_novel_data():
    novelbin_data = loadJson("./novelbin_data.json")
    names = getIdToName()
    data = loadJson("novel_data.json")
    for i in range(1, len(names)):
        if len(data) == i:
            data.append({})
        elif data[i] != {}:
            continue
        name = getNameFromId(i)
        src = None
        description = None
        tags = []
        chapters = None
        chaptersAi = None
        if name in novelbin_data:
            src = "novelbin"
            description = getNovelDescriptionNovelbin(i)
            tags = getNovelTagsNovelbin(i)
            chapters = getChapterCountNovelbin(i)
            chaptersAi = getAiChapterCountOsPath(i)

        def isMissing(field):
            return (not (field in data[i])) or (data[i][field] == None)

        def replaceIfMissing(field, value):
            if isMissing(field) and value != None:
                data[i][field] = value
        
        replaceIfMissing("name", name)
        replaceIfMissing("source", src)
        replaceIfMissing("description", description)
        replaceIfMissing("tags", tags)
        replaceIfMissing("chapters", chapters)
        replaceIfMissing("chaptersAi", chaptersAi)
        printProgressBar(i, len(names)-1, prefix = "Progress: ", suffix = "{} of {}".format(i, len(names)-1), length = 30)
    storeJson("novel_data.json", data)
