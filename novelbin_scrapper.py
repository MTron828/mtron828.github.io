import time
import random
import requests
import json
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
#from bs4 import BeautifulSoup
import os
from fill_chapter_data import fill_chapter_data
from progress_bar import printProgressBar


driver = uc.Chrome(executable_path = "./chromedriver.exe")

data = {}

def loadData():
    global data
    with open("novelbin_data.json", "r", encoding='utf-8') as f:
        data = json.loads(f.read())

def storeData():
    with open("novelbin_data.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(data))

def jump(url):
    driver.get(url)

def getById(obj, id):
    return obj.find_element(By.ID, id)

def getByXPATH(obj, xpath):
    return obj.find_element(By.XPATH, xpath)

def getByClass(obj, cl):
    return obj.find_element(By.CLASS_NAME, cl)

def getElsByClass(obj, cl):
    return obj.find_elements(By.CLASS_NAME, cl)

def getByTag(obj, tag):
    return obj.find_element(By.TAG_NAME, tag)

def getElsByTag(obj, tag):
    return obj.find_elements(By.TAG_NAME, tag)

def getNovelListElement():
    return getByXPATH(driver, '//*[@id="list-page"]/div[1]/div')

def novelListIterator():
    for novel in getElsByClass(getNovelListElement(), "row"):
        yield novel

def indexNovel(el):
    h3 = getByClass(el, "novel-title")
    a = getByTag(h3, "a")
    name = a.get_attribute("innerText")
    href = a.get_attribute("href")
    data[name] = {"name":name, "link":href}
    
def indexNovels():
    for novel in novelListIterator():
        indexNovel(novel)

def jumpPopularPage(n):
    jump("https://novelbin.me/sort/novelbin-popular?page="+str(n+1))


def scrapNovels():
    PAGE_NUM = 242
    for i in range(242):
        jumpPopularPage(i)
        indexNovels()
        print("Page: {}, data_size: {}".format(i+1, len(data)))
        storeData()

def scrapNovelDescriptions():
    global data
    total = len(data)
    cnt = 0
    for name in data:
        novel_data = data[name]
        cnt+=1
        jump(novel_data["link"])
        descr = getByXPATH(driver, '//*[@id="tab-description"]/div')
        data[name]["description"] = descr.get_attribute("innerText")
        print("Scrapped description of novel {} of {}. {:.2f}%".format(cnt, total, 100.0*cnt/total))
        storeData()

def scrapNovelTags():
    global data
    total = len(data)
    count = 0
    for name in data:
        novel_data = data[name]
        count+=1
        jump(novel_data["link"])
        
        ul = getByXPATH(driver, '//*[@id="novel"]/div[1]/div[1]/div[3]/ul')
        tags = []

        for li in getElsByTag(ul, "li"):
            
            cnt = getByTag(li, "h3").get_attribute("innerText")
            time.sleep(0.1)
            if not ("Genre" in cnt or "Tag" in cnt):
                continue
            if "Genre" in cnt:
                print("Genre present.")
            if "Tag" in cnt:
                print("Tag present.")
            
            try:
                div = getByClass(li, "showmore")
                a = getByTag(div, "a")
                a.click()
                time.sleep(0.1)
                print("Show more present.")
            except:
                pass

            for el in getElsByTag(li, "a"):
                tags.append(el.get_attribute("innerText"))

        data[name]["tags"] = tags
        print("Scrapped tags of novel {} of {}. {:.2f}%".format(count, total, 100.0*count/total))
        storeData()

def getLinks(link):
    print("Getting links...")
    jump(link)
    getById(driver, "tab-chapters-title").click()
    print("Waiting to load...")
    while len(getElsByClass(driver, "loading")) != 0:
        time.sleep(0.1)
    """panel = getByClass(driver, "panel-body")
    res = []
    print("Scrapping links...")
    for li in getElsByTag(panel, "li"):
        a = getByTag(li, "a")
        res.append(a.get_attribute("href"))
    print("Done, returing {} links.".format(len(res)))
    return res"""
    print("Getting links...")
    res = driver.execute_script("""
var res = [];
for (let li of document.getElementsByClassName("panel-body")[0].getElementsByTagName("li")) {
    res[res.length] = li.getElementsByTagName("a")[0].href;
}
return res;
""")
    print("Done, returing {} links.".format(len(res)))
    return res

def getChapter(link):
    """user_agents = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36']
    headers = {'User-Agent': random.choice(user_agents)} 
    html = requests.get(link, headers=headers).text
    soup = BeautifulSoup(html, features="html.parser")
    txt = soup.find(id="chr-content").get_text()"""
    jump(link)
    txt = getById(driver, "chr-content").get_attribute("innerText")
    return txt

def getNovelId(name, chap_cnt):
    print("Getting novel id...")
    print("Opening json...")
    novels = {}
    with open("./novels/novels.json", "r", encoding='utf-8') as f:
        novels = json.loads(f.read())
    print("Searching novel array...")
    max_id = 0
    for novel in novels["novels"]:
        if novel["title"] == name:
            print("Found, novel id: {}.".format(novel["id"]))
            return novel["id"]
        else:
            max_id = max(max_id, novel["id"])
    print("Not found, creating new entry into novels:")
    print("  title:    {}".format(name))
    print("  chapters: {}".format(chap_cnt))
    print("  id:       {}".format(max_id+1))
    novels["novels"].append({
        "title":name,
        "chapters":chap_cnt,
        "id":max_id+1
    })
    print("Saving modified novel data...")
    with open("./novels/novels.json", "w", encoding='utf-8') as f:
        f.write(json.dumps(novels))
    print("Done, returning id: {}".format(max_id+1))
    return max_id+1

def updateNovelFolder(name, id):
    if not os.path.exists("./novels/{}".format(id)):
        os.mkdir("./novels/{}".format(id))
    if not os.path.isfile("./novels/{}/data.json".format(id)):
        with open("./novels/{}/data.json".format(id), "w", encoding='utf-8') as f:
            f.write(json.dumps({
                "title":name,
                "chapters":[]
            }))
    if not os.path.exists("./novels/{}/chapters".format(id)):
        os.mkdir("./novels/{}/chapters".format(id))

def downloadNovel(name):
    print("--------------------------------------------------------")
    print("Downloading all chapters from novel {}.".format(name))
    print("Getting link from data")
    novel_link = data[name]["link"]
    print("Calling getLinks")
    links = getLinks(novel_link)
    print("Calling getNovelId")
    id = getNovelId(name, len(links))
    print("Calling updateNovelFolder")
    updateNovelFolder(name, id)
    chapter_directory = "./novels/{}/chapters/".format(id)
    print("Downloading chapters of {}:".format(name))
    for i in range(len(links)):
        if not os.path.exists(chapter_directory+"{}.txt".format(i)):
            txt = getChapter(links[i])
            with open(chapter_directory+"{}.txt".format(i), "w", encoding='utf-8') as f:
                f.write(txt)
        printProgressBar(i+1, len(links), prefix = "Progress: ", length = 50)
    print("Updating chapter data...")
    fill_chapter_data()
    print("Done.")

def downloadNovels():
    for name in data:
        downloadNovel(name)


while True:
    try:
        try:
            driver.close()
        except:
            pass
        driver = uc.Chrome(executable_path = "./chromedriver.exe")
        loadData()
        print("Data loaded...")
        print("Data size: {}".format(len(data)))
        #scrapNovelTags()
        #scrapNovelDescriptions()
        #scrapNovels()
        downloadNovels()
        storeData()
        driver.close()
        break
    except Exception as ec:
        print(ec)

