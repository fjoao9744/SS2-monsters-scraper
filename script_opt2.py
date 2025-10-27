from playwright.async_api import async_playwright
import asyncio
from PIL import Image
import aiohttp
import os
import json
import time

start = time.time()

monster_list = {}
semaphore_status = asyncio.Semaphore(10)
semaphore_images = asyncio.Semaphore(20)

os.makedirs("images", exist_ok=True)
async def process_family(imgs, names, family, browser, session, family_len):
    tasks = []
    print(f"a carregar: {family_len}")
    
    for c, monster_num in enumerate(family_len):
        tasks.append(download_image(session, imgs[c], family, monster_num))
        tasks.append(collect_status(names[c], family, browser, monster_num))
        
    await asyncio.gather(*tasks)
    
async def collect_status(name, family, browser, monster_num):
    async with semaphore_status:
        page_href = await name.get_attribute("href")
        url = "https://tartarus.rpgclassics.com/ss2/" + page_href.split("'")[1]
        
        monster_page = await browser.new_page()
        await monster_page.goto(url, wait_until="domcontentloaded")
        monster_page_html = await monster_page.query_selector("tbody")
        
        lines = await monster_page_html.query_selector_all("tr > td")
        
        all_stats = [await line.inner_text() for line in lines[1:]]
        
        # for i, stats in enumerate(all_stats):
        #     print(i, stats)
        
        index_map = { # bizarre code
            "min_lv": 0, "max_lv": 2,
            "min_exp": 1, "max_exp": 3,
            "min_hp": 4, "max_hp": 6,
            "min_mp": 5, "max_mp": 7,
            "min_atk": 8, "max_atk": 10,
            "min_def": 12, "max_def": 14,
            "min_spd": 16, "max_spd": 18,
            "min_dex": 20, "max_dex": 22,
            "min_int": 24, "max_int": 26,
            "min_vit": 29, "max_vit": 31,
            "type": 28,
            "res_fire": 9, "res_ice": 13,
            "res_thunder": 17, "res_lightness": 21,
            "res_darkness": 25, "res_death": 30,
            "description": 33
        }

        status = {campo: all_stats[idx] for campo, idx in index_map.items()}
        
        monster_name = await name.inner_text()
        
        monster_list[family].append({"name":monster_name, "sprite": f"{monster_num:03}.gif", "status": status})
        
        await monster_page.close()
        
        print(f"{monster_name}({monster_num}) esta pronto!")
        
async def download_image(session, img, family, monster_num):
    async with semaphore_images:
        img_src = await img.get_attribute("src")
        img_url = "https://tartarus.rpgclassics.com/ss2/" + img_src
        
        async with session.get(img_url) as response:
            img_data = await response.read()
        
        filename = os.path.join("images", family, f"{monster_num:03}")
        
        with open(f"{filename}.gif", "wb") as image:
            image.write(img_data)
            
        with Image.open(f"{filename}.gif") as image:
            image = image.resize((image.width*4, image.height*4), Image.NEAREST) # type:ignore
            image.save(f"{filename}.gif")
        
        print(f"{img}({monster_num}) foi baixado!")

async def main():
    async with async_playwright() as pl:
        browser = await pl.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://tartarus.rpgclassics.com/ss2/bestiary.shtml", wait_until="domcontentloaded")
        
        html = await page.query_selector_all("table > tbody")
        
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            monsters_num = 0
            for ht in html[2:]: # site navigation and thanks
                th_element = await ht.query_selector("tr")
                family = await th_element.inner_text()
                
                monster_list[family] = []
                os.makedirs("images\\" + family, exist_ok=True)
                
                imgs = await ht.query_selector_all("td > img[src^='monster/']")
                names = await ht.query_selector_all("td > a[href^=\"javascript:newwnd('bestiary/\"]")
                
                monsters_len = range(monsters_num, monsters_num + len(imgs))
                monsters_num += len(imgs)
                
                tasks.append(asyncio.create_task(process_family(imgs, names, family, browser, session, monsters_len)))
            
            await asyncio.gather(*tasks)
        
        await page.close()
        await browser.close()
        
        with open("monsters.json", "w") as f:
            json.dump(monster_list, f, indent=4)
        # print(ht.inner_html())
        
    end = time.time()

    print("Tempo de execução:", end - start, "segundos")
        
asyncio.run(main())