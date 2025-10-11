from playwright.sync_api import sync_playwright
from PIL import Image
import requests
import os
import json

monster_list = {}

os.makedirs("images", exist_ok=True)

with sync_playwright() as pl:
    browser = pl.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://tartarus.rpgclassics.com/ss2/bestiary.shtml")
    
    html = page.query_selector_all("table > tbody")
    
    monster_num = 0
    
    for ht in html[2:]: # site navigation and thanks
        
        family = ht.query_selector("tr").inner_text()
        monster_list[family] = []
        os.makedirs("images\\" + family, exist_ok=True)
        
        imgs = ht.query_selector_all("td > img[src^='monster/']")
        names = ht.query_selector_all("td > a[href^=\"javascript:newwnd('bestiary/\"]")

        for c in range(len(names)):
            
            img = imgs[c].get_attribute("src")
            name = names[c].inner_text()
            
            """
            imgs = ht.query_selector_all("td > img[src^='monster/']")
            for img in imgs:
                img_url = img.get_attribute("src")
                print(img_url)
                
            names = ht.query_selector_all("td > a")
            for name in names:
                print(name.inner_text())
            """
            
            img_url = "https://tartarus.rpgclassics.com/ss2/" + img
            
            img_data = requests.get(img_url).content
            
            filename = os.path.join("images", family, f"{monster_num:03}")
            
            with open(f"{filename}.gif", "wb") as image:
                image.write(img_data)
                
            with Image.open(f"{filename}.gif") as image:
                image = image.resize((image.width*4, image.height*4), Image.NEAREST) # type:ignore
                image.save(f"{filename}.gif")
                
            print(f"{name} foi baixado!")
            
            with page.expect_popup() as popup:
                names[c].click()
                
            monster_page = popup.value
            monster_page.wait_for_load_state("networkidle")
            monster_page_html = monster_page.query_selector("tbody")
            
            lines = monster_page_html.query_selector_all("tr > td")
            
            all_stats = []
            for line in lines[1:]:
                all_stats.append(line.inner_text())
            
            # for i, stats in enumerate(all_stats):
            #     print(i, stats)
            
            status = {
                "min_lv": all_stats[0],
                "max_lv": all_stats[2],
                
                "min_exp": all_stats[1],
                "max_exp": all_stats[3],
                
                "min_hp": all_stats[4],
                "max_hp": all_stats[6],
                
                "min_mp": all_stats[5],
                "max_mp": all_stats[7],
                
                "min_atk": all_stats[8],
                "max_atk": all_stats[10],
                
                "min_def": all_stats[12],
                "max_def": all_stats[14],
                
                "min_spd": all_stats[16],
                "max_spd": all_stats[18],
                
                "min_dex": all_stats[20],
                "max_dex": all_stats[22],
                
                "min_int": all_stats[24],
                "max_int": all_stats[26],
                
                "min_vit": all_stats[29],
                "max_vit": all_stats[31],
                
                "type": all_stats[28],
                
                "res_fire": all_stats[9],
                
                "res_ice": all_stats[13],
                
                "res_thunder": all_stats[17],
                
                "res_lightness": all_stats[21],
                
                "res_darkness": all_stats[25],
                
                "res_death": all_stats[30],
                
                "description": all_stats[33]
            }
            
            monster_page.close()
            
            monster_list[family].append({"name":name, "sprite": f"{monster_num:03}.gif", "status": status})
            monster_num += 1
            
            print(f"{name} esta pronto!")
            
        # print(ht.inner_html())
    
    page.close()
    
with open("monsters.json", "w") as f:
    json.dump(monster_list, f, indent=4)