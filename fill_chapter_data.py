import json
import glob
from progress_bar import printProgressBar

def fill_chapter_data():
    #TODO
    novel_data_str = ""
    with open("./novels/novels.json", "r") as f:
        novel_data_str = f.read()
    novel_data = json.loads(novel_data_str)
    cnt = 0
    for novel in novel_data["novels"]:
        cnt += 1
        id = novel["id"]
        json_str = ""
        with open("./novels/"+str(id)+"/data.json", "r") as f:
            json_str = f.read()
        data = json.loads(json_str)
        data["chapters"] = []
        #print("Novel: "+novel["title"])
        chaps = []
        for chap in glob.glob("./novels/"+str(id)+"/chapters/*.txt"):
            #print("Chapter: "+chap.split(".txt")[0].split("/")[-1].split("\\")[-1])
            chaps.append(int(chap.split(".txt")[0].split("/")[-1].split("\\")[-1]))
        chaps.sort()
        ai_chaps = []
        for chap in glob.glob("./novels/"+str(id)+"/chapters/ai/*.txt"):
            ai_chaps.append(int(chap.split(".txt")[0].split("/")[-1].split("\\")[-1]))
        ai_chaps.sort()
        for chap in chaps:
            data["chapters"].append(str(chap))
        for chap in ai_chaps:
            data["chapters"].append("ai/"+str(chap))
        json_str = json.dumps(data)
        with open("./novels/"+str(id)+"/data.json", "w") as f:
            f.write(json_str)
        printProgressBar(cnt, len(novel_data["novels"]), prefix="Updating chapter data: ", length = 30)

#fill_chapter_data()