
import json
import glob

novel_data_str = ""
with open("./novels/novels.json", "r") as f:
    novel_data_str = f.read()
novel_data = json.loads(novel_data_str)

for novel in novel_data["novels"]:
    id = novel["id"]
    json_str = ""
    with open("./novels/"+id+"/data.json", "r") as f:
        json_str = f.read()
    data = json.loads(json_str)
    data["chapters"] = []
    print("Novel: "+novel["title"])
    for chap in glob.glob("./novels/"+id+"/chapters/*.txt"):
        print("Chapter: "+chap.split(".txt")[0].split("/")[-1].split("\\")[-1])
        data["chapters"].append(chap.split(".txt")[0].split("/")[-1].split("\\")[-1])
    json_str = json.dumps(data)
    with open("./novels/"+id+"/data.json", "w") as f:
        f.write(json_str)

