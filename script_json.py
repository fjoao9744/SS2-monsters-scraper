# gerar um json

import requests
from bs4 import BeautifulSoup
import json

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
    
    tittle = tittle.text

    monster_list[tittle] = []
    for td in tds:  

        if td.text != "":
            i = td.find("a").text
            monster_list[tittle].append(i)

print(monster_list)
with open("sprites.json", "w") as f:
    json.dump(monster_list, f, indent=4)
