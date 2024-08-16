import json
import os
from progress_bar import printProgressBar
import copy


json_cache = {}
def loadJson(file):
    if file in json_cache:
        #print(json_cache[file])
        return copy.deepcopy(json_cache[file])
    txt = ""
    with open(file, "r") as f:
        txt = f.read()
    json_cache[file] = json.loads(txt)
    return copy.deepcopy(json_cache[file])

def storeJson(file, data):
    if file in json_cache:
        del json_cache[file]
    txt = json.dumps(data)
    with open(file, "w") as f:
        f.write(txt)

def getIdToName():
    return loadJson("./id_to_name.json")

def setIdToName(arr):
    storeJson("./id_to_name.json", arr)

def getNovelData():
    return loadJson("./novel_data.json")

def setNovelData(data):
    storeJson("./novel_data.json", data)

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
    try:
        file = loadJson("./novelbin_links_{}.json".format(filenum))
        return len(file[offset])
    except:
        return None

def getAiChapterCountOsPath(id):
    path = "./novels/{}/chapters/ai".format(id)
    if os.path.isdir(path):
        return sum(1 for entry in os.listdir(path) if os.path.isfile(os.path.join(path, entry)))
    else:
        return 0

def getNovelDescriptionNovelbin(id):
    data = loadJson("./novelbin_data.json")
    try:
        return data[getNameFromId(id)]["description"]
    except:
        return None

def getNovelTagsNovelbin(id):
    data = loadJson("./novelbin_data.json")
    try:
        return data[getNameFromId(id)]["tags"]  
    except:
        return None

def update_novel_data_entry(i):
    data = getNovelData()
    novelbin_data = loadJson("./novelbin_data.json")
    if len(data) == i:
        data.append({})
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
    replaceIfMissing("id", i)
    replaceIfMissing("name", name)
    replaceIfMissing("source", src)
    replaceIfMissing("description", description)
    replaceIfMissing("tags", tags)
    replaceIfMissing("chapters", chapters)
    replaceIfMissing("chaptersAi", chaptersAi)
    setNovelData(data)

def update_novel_data_entries(arr):
    data = getNovelData()
    novelbin_data = loadJson("./novelbin_data.json")
    for i in arr:
        if len(data) == i:
            data.append({})
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
        replaceIfMissing("id", i)
        replaceIfMissing("name", name)
        replaceIfMissing("source", src)
        replaceIfMissing("description", description)
        replaceIfMissing("tags", tags)
        replaceIfMissing("chapters", chapters)
        replaceIfMissing("chaptersAi", chaptersAi)
    setNovelData(data)

def precalc_novel_data():
    names = getIdToName()
    for i in range(1, len(names)):
        crate_novel_data_entry(i)

def getChapterCount(id):
    novel = getNovelData()[id]
    if "chapters" in novel:
        return novel["chapters"]
    return None

def getAiChapterCount(id):
    novel = getNovelData()[id]
    if "chaptersAi" in novel:
        return novel["chaptersAi"]
    return None

def getNovelDescription(id):
    novel = getNovelData()[id]
    if "description" in novel:
        return novel["description"]
    return None

def getNovelTags(id):
    novel = getNovelData()[id]
    if "tags" in novel:
        return novel["tags"]
    return None

def searchTitles(string):
    res = []
    data = getNovelData()
    for novel in data[1:]:
        if "name" in novel and string.lower() in novel["name"].lower():
            res.append(novel["id"])
    return res

def searchTags(string):
    res = []
    data = getNovelData()
    for novel in data[1:]:
        if "tags" in novel and True in [string.lower() in x.lower() for x in novel["tags"]]:
            res.append(novel["id"])
    return res

def searchDescriptions(string):
    res = []
    data = getNovelData()
    for novel in data[1:]:
        if "description" in novel and string.lower() in novel["description"].lower():
            res.append(novel["id"])
    return res

def getNovelChapter(novel, chapter):
    path = "./novels/{}/chapters/{}.txt".format(novel, chapter)
    print(path)
    if os.path.isfile(path):
        txt = ""
        with open(path, "r", encoding='utf-8') as f:
            txt = f.read()
        return txt
    return None 

def getAiGeneratedNovelChapter(novel, chapter):
    path = "./novels/{}/chapters/ai/{}.txt".format(novel, chapter)
    if os.path.isfile(path):
        txt = ""
        with open(path, "r", encoding='utf-8') as f:
            txt = f.read()
        return txt
    return None

def getNovelLinks(id):
    filenum = id//100
    offset = id%100
    file = loadJson("./novelbin_links_{}.json".format(filenum))
    return file[offset]

def getDownladedChapterCount(novel):
    path = "./novels/{}/chapters".format(novel)
    if os.path.isdir(path):
        total_files = 0
        for root, dirs, files in os.walk(path):
            total_files += len(files)
        return total_files
    return 0
