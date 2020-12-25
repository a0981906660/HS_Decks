#!/usr/bin/env python
# coding: utf-8

# # Hearth Stone Decker
# 
# * https://hsreplay.net/decks/

# In[1]:


import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import pandas as pd
import numpy as np
import time
import re
import datetime
import sqlite3 as lite
import os
import random
import calendar


# In[2]:


url = "https://hsreplay.net/decks/"


# In[3]:


# Open Browser and open udn library #打開瀏覽器，但不要載入圖片
options = webdriver.ChromeOptions()
prefs = {
    'profile.default_content_setting_values': {
        'images': 2,
        #'javascript': 2
    }
}
options.add_experimental_option('prefs', prefs)
options.add_experimental_option('prefs', prefs)

# 偽裝header
user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0.3 Safari/605.1.15"
options.add_argument('--user-agent=%s' % user_agent)
# 防止 javascript detect selenium
options.add_experimental_option('excludeSwitches', ['enable-automation'])
# headless
#options.add_argument('-headless')
# Window Maximized
options.add_argument("--start-maximized")

global driver


# In[4]:


driver = webdriver.Chrome('/Users/boyie/chrome_driver/chromedriver', chrome_options=options)


# In[5]:


driver.get(url)


# # Deck Dictionary

# In[6]:


occupation_dict = {
    "Demon Hunter" : "https://hsreplay.net/decks/#playerClasses=DEMONHUNTER",
    "Druid" : "https://hsreplay.net/decks/#playerClasses=DRUID",
    "Hunter" : "https://hsreplay.net/decks/#playerClasses=HUNTER",
    "Mage" : "https://hsreplay.net/decks/#playerClasses=MAGE",
    "Paladin" : "https://hsreplay.net/decks/#playerClasses=PALADIN",
    "Priest" : "https://hsreplay.net/decks/#playerClasses=PRIEST",
    "Rogue" : "https://hsreplay.net/decks/#playerClasses=ROGUE",
    "Shaman" : "https://hsreplay.net/decks/#playerClasses=SHAMAN",
    "Warlock" : "https://hsreplay.net/decks/#playerClasses=WARLOCK",
    "Warrior" : "https://hsreplay.net/decks/#playerClasses=WARRIOR",
}


# In[7]:


occupation_alternative_keyword = {
    "Demon Hunter" : "惡魔獵人",
    "Druid" : "德",
    "Hunter" : "獵",
    "Mage" : "法",
    "Paladin" : "聖",
    "Priest" : "牧",
    "Rogue" : "賊",
    "Shaman" : "薩",
    "Warlock" : "術",
    "Warrior" : "戰",
}


# In[8]:


# 滑到網頁最下方
def scroll_down():
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


# ### 拿到牌組的其他feature
# 
# 1. Name
# 
# 2. Composition (1 or 2 cards)
# 
# 3. Card URL
# 
# 4. Overall Win Rate
# 
# 5. 合成成本 (表示土豪程度)
# 
# 6. 已遊玩的局數 (表示熱門程度)
# 
# 7. 遊戲持續時間 (表示節奏)

# ### 階段性成果QQ

# In[21]:


# Save
#np.save('Priest_deck_dict.npy', deck_dict)

# Load
#read_dictionary = np.load('DemonHunter_deck_dict.npy',allow_pickle='TRUE').item()


# # function
# 
# 寫成迴圈，對於12頁的資料都如此爬

# In[14]:


def getDeck(occupation_name = "Demon Hunter"):
    print(f">>> 現在爬的職業是：{occupation_name}")
    # 可能會出現的中文關鍵字
    alternative_keyword = occupation_alternative_keyword[occupation_name]

    # Overall_dict
    deck_dict = {}

    page_url = f"{occupation_dict[occupation_name]}"
    driver.get(page_url)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    max_page = int(soup.select(".transparent-background")[-1].text.split(" / ")[-1])
    print(f">>> 總共有 {max_page} 頁")
    
    for k in range(1,max_page+1):
        print(f">>> 現在正在爬第 {k} 頁")

        driver.implicitly_wait(10)
        time.sleep(1)
        # Load
        scroll_down()
        time.sleep(1)

        # a sub dict
        DemonHunter_deck_dict = {}

        # get keys (every 18 in 1 page, for 12 pages)
        # 需要specify不同的keyword，因為牌組名稱有中文有英文
        partial_link_elements = []
        for part in driver.find_elements_by_partial_link_text(f"{occupation_name}"):
            partial_link_elements.append(part)
        for part in driver.find_elements_by_partial_link_text(f"{alternative_keyword}"):
            partial_link_elements.append(part)
        # 開始拿牌組的key
        for deck_key in partial_link_elements:
            #print(deck_key.get_attribute("href"))
            href = deck_key.get_attribute("href")
            key = href.split("/")[-2]
            DemonHunter_deck_dict[key] = {"URL" : href}
        print(f">>> 這一頁有 {len(partial_link_elements)} 個符合關鍵字的牌組")

        soup = BeautifulSoup(driver.page_source, 'lxml')
        for i in range(0,len(partial_link_elements)):
            keyname = list(DemonHunter_deck_dict.keys())[i]

            # get deck names
            deck_name = driver.find_elements_by_css_selector(".deck-name")[i]
            DemonHunter_deck_dict[keyname]["Deck_Name"] = deck_name.text

            # Get Card Compositions
            DemonHunter_deck_dict[keyname]["Deck_Composition"] = {}
            card_list = driver.find_elements_by_css_selector("ul.card-list")[i].find_elements_by_css_selector("a")
            #Key for Cards
            card_urls = [card_url.get_attribute("href") for card_url in card_list]
            card_keys = [int(k.split("/")[-2]) for k in card_urls]

            for j in range(len(card_keys)): #從第一張卡到最後一張卡
                name_num_str = soup.select("ul.card-list")[i].select(".card-icon")[j]["aria-label"]
                card_name = name_num_str.split()[0]
                if name_num_str.split()[-1] == "★":
                    IsDuo = 0
                if name_num_str.split()[-1] == "×2":
                    IsDuo = 1
                else:
                    IsDuo = "NaN"

                DemonHunter_deck_dict[keyname]["Deck_Composition"][card_keys[j]] = {
                    "card_name" : card_name,
                    "IsDuo" : IsDuo,
                    "card_URL" : card_urls[j],
                }

            # Win Rate
            win_rate = driver.find_elements_by_css_selector(".win-rate")[i].text
            DemonHunter_deck_dict[keyname]["win_rate"] = win_rate

            # 合卡成本
            dust_cost = driver.find_elements_by_css_selector(".dust-cost")[i].text
            DemonHunter_deck_dict[keyname]["dust_cost"] = dust_cost

            # 該牌組已被使用的對場場數
            game_count = driver.find_elements_by_css_selector(".game-count")[i].text
            DemonHunter_deck_dict[keyname]["game_count"] = game_count

            # 每回比賽平均時間
            time_duration = driver.find_elements_by_css_selector(".duration")[i].text
            DemonHunter_deck_dict[keyname]["time_duration"] = time_duration

            time.sleep(1)
            # Merge to the parent dict
            deck_dict.update(DemonHunter_deck_dict)

        # Next Page
        #driver.find_element_by_xpath("""//*[@id="decks-container"]/main/div[3]/section/div[4]/nav/ul/li[8]/a""").click()
        driver.find_element_by_css_selector(".glyphicon-arrow-right").click()
        driver.implicitly_wait(5)

    return deck_dict


# ### For all occupations
# 
# run `getDeck()`

# In[ ]:


names = locals()
for key in list(occupation_dict.keys()):
    try:
        nam = "".join(key.split())
        names[f"dict_{nam}"] = getDeck(occupation_name = key)
        time_stamp = datetime.datetime.today().strftime("%Y-%m-%d_%H-%M")
        np.save(f"/Users/boyie/HS/DB/{key}/{nam}_deck_dict_{time_stamp}.npy", names[f"dict_{nam}"])
    except:
        pass

driver.close()