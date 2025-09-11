import requests
from bs4 import BeautifulSoup
import os
import shutil
from PIL import Image
from urllib.parse import urljoin
import time

start = time.time()

# limpeza

caminho = os.path.join(os.getcwd(), "images")

if os.path.exists(caminho):
    shutil.rmtree(caminho)
    
os.makedirs(caminho, exist_ok=True)

# scraping

res = requests.get("https://tartarus.rpgclassics.com/ss2/bestiary.shtml")

soup = BeautifulSoup(res.content, "lxml")
tables = soup.find_all("table")

monster_list = {}
for table in tables[2:]:
    tds = table.find_all("td") # type:ignore
    tittle = table.find("tr") # type:ignore
    
    if tittle is None:
        continue
    
    tittle_text = tittle.text.strip().replace("\n", "").replace("/", "-")
    new_caminho = os.path.join(caminho, tittle_text)
    os.makedirs(new_caminho)
    
    c = 0
    monster_list[tittle.text] = []
    for td in tds:  
        imgs = td.find_all("img")
        # print(td)
            
        if td.text == "":
            i = td.find("img").get("src")
            monster_list[tittle.text].append([i])
            
        elif td.text != "":
            i = td.find("a").text
            monster_list[tittle.text][c].append(i)
            c += 1
            
print(monster_list)
for family in monster_list.items():
    monsters = family[1]
    for monster in monsters:
        img_url = urljoin(res.url, monster[0])

        filename = os.path.join(caminho, family[0], monster[1])
        img_data = requests.get(img_url).content
        with open(f"{filename}.gif", "wb") as f:
            f.write(img_data)
            
        with Image.open(f"{filename}.gif") as img:
            img = img.resize((img.width*4, img.height*4), Image.NEAREST)
            img.save(f"{filename}.gif")
        
        print("monstro", filename)

end = time.time()
    
print(f"Demorou {end - start:.4f} segundos para baixar todas as imagens")