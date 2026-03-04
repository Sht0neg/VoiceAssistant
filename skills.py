from datetime import datetime as dt
import re
import sys
import os
import time
from pathlib import Path
import webbrowser
from xmlrpc.client import DateTime

import requests
import json
import asyncio


async def find_exe(apps, exes):
    result = dict()
    for driver in os.listdrives():
        for root, _, files in os.walk(driver):
            for file in files:
                for name, filename in zip(apps, exes):
                    if (filename + ".exe").lower() == file.lower() and file.lower().endswith(".exe") and "$Recycle.Bin" not in root:
                        result[name] = re.sub(r'Program Files[^\\]*', f'"{re.search(r'Program Files[^\\]*', 
                            os.path.join(root, file)).group(0)}"', os.path.join(root, file)) \
                            if re.search(r'Program Files[^\\]*', os.path.join(root, file)) else os.path.join(root, file)
    return result


async def path_of_apps_in_json():
    apps = ["Word", "Exel", "Powerpoint", "Telegram", "Discord", "Whatsapp", "Paint", "AnyDesk", "VirtualBox", "VMWare",
            "Steam",
            "CS", "Dota", "Valorant", "Apex", "Fortnite", "League", "PUBG", "GTA5", "MirTankov", "WOT", "Warthunder",
            "Genshin", "ZZZ", "HonkaiStarRail"]
    exes = ["WINWORD", "EXCEL", "POWERPNT", "Telegram", "Discord", "WhatsApp", "mspaint", "AnyDesk", "VirtualBox",
            "vmware", "Steam",
            "cs2", "dota2", "VALORANT-Win64-Shipping", "r5apex", "FortiniteClient-Win64-Shipping", "RiotClientServices",
            "TslGame", "GTA5", "Tanki", "worldoftanks", "aces_BE", "GenshinImpact", "ZenlesZoneZero", "StarRail"]

    result = await find_exe(apps, exes)
    with open("apps.json", "w") as file:
        json.dump(result, file, separators=(',\n', ': '))
    

def weather():
             
    with open("psw.json") as file:
        psw = json.load(file)
        ip = requests.get("https://ifconfig.me/ip").text
        loc = requests.get(f'https://ipinfo.io/{ip}/json').json()
        weather = requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{loc["loc"]}/{dt.now().strftime('%Y-%m-%dT%H:%M:%S')}?key={psw["weather"]}"
                               ,params={"include": "current", "unitGroup" : "metric", "lang" : "ru"})
        data = weather.json()
        with open("data.json", "w") as f:
            json.dump(data, f)
    
def video():
    webbrowser.open("https://www.youtube.com", new=2)

def video_search(text):
    webbrowser.open(f"https://www.youtube.com/results?search_query={text}", new=2)

def browser():
    webbrowser.open(f"https://www.google.com", new=2)

def search(text):
    webbrowser.open(f"https://www.google.com/search?q={text}", new=2)

def calc():
     os.system('calc')


def offpc():
    #os.system('shutdown \s')
    pass

def offBot():
	sys.exit()

def passive():
	pass
