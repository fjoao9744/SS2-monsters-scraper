# PIL

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
async def process_family(imgs, names, family, browser, session):
    tasks_images = [
        download_image(session, img, family, c)
        for c, img in enumerate(imgs)
    ]
    tasks_status = [ 
        collect_status(names[c], family, browser, c)
        for c in range(len(names))
    ]
    
    await asyncio.gather(*tasks_images, *tasks_status)
    
async def collect_status(name, family, browser, monster_num):
    print(family, name)
    async with semaphore_status:
        page_href = await name.get_attribute("href")
        url = "https://tartarus.rpgclassics.com/ss2/" + page_href.split("'")[1]
        
        monster_page = await browser.new_page()
        await monster_page.goto(url, wait_until="domcontentloaded")
        monster_page_html =await  monster_page.query_selector("tbody")
        
        lines = await monster_page_html.query_selector_all("tr > td")
        
        all_stats = [await line.inner_text() for line in lines[1:]]
        
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
        
        monster_name = await name.inner_text()
        
        monster_list[family].append({"name":monster_name, "sprite": f"{monster_num:03}.gif", "status": status})
        
        await monster_page.close()
        
        print(f"{monster_name} esta pronto!")
        
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
        
        print(f"{img} foi baixado!")

async def main():
    async with async_playwright() as pl:
        browser = await pl.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://tartarus.rpgclassics.com/ss2/bestiary.shtml", wait_until="domcontentloaded")
        
        html = await page.query_selector_all("table > tbody")
        
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            # tasks = [
            #     process_family(imgs, names, family, browser, session)
            #     for ht in html[2:]
            # ]
            
            for ht in html[2:]: # site navigation and thanks
                th_element = await ht.query_selector("tr")
                family = await th_element.inner_text()
                
                monster_list[family] = []
                os.makedirs("images\\" + family, exist_ok=True)
                
                imgs = await ht.query_selector_all("td > img[src^='monster/']")
                names = await ht.query_selector_all("td > a[href^=\"javascript:newwnd('bestiary/\"]")
                
                tasks.append(asyncio.create_task(process_family(imgs, names, family, browser, session)))
            
            await asyncio.gather(*tasks)
        
        await page.close()
        await browser.close()
        
        with open("monsters.json", "w") as f:
            json.dump(monster_list, f, indent=4)
        # print(ht.inner_html())
        
    end = time.time()

    print("Tempo de execução:", end - start, "segundos")
        
asyncio.run(main())