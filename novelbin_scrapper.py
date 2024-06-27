import time
import requests
import json
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


driver = uc.Chrome()

data = {}

def loadData():
    global data
    with open("novelbin_data.json", "r") as f:
        data = json.loads(f.read())

def storeData():
    with open("novelbin_data.json", "w") as f:
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
    #TESTING - delete later
    link = "https://novelbin.com/b/nine-star-hegemon-body-arts"
    jump(link)
    getById(driver, "tab-chapters-title").click()
    while len(getElsByClass(driver, "loading")) != 0:
        time.sleep(0.1)
    panel = getByClass(driver, "panel-body")
    res = []
    for li in getElsByTag(panel, "li"):
        a = getByTag(li, "a")
        res.append(a.get_attribute("href"))
    return res

def getChapter(link):
    html = requests.get(link).text
    soup = BeautifulSoup(html)
    txt = soup.find(id="chr-content").get_text()
    return txt

def downloadNovel(name):
    novel_link = data[name]["link"]
    links = getLinks(novel_link)

loadData()
print("Data loaded...")
print("Data size: {}".format(len(data)))
downloadNovel("Ascension Through Skills")
#scrapNovelTags()
#scrapNovelDescriptions()
#scrapNovels()
storeData()
driver.close()

