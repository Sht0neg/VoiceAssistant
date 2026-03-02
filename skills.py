from datetime import datetime as dt
import re
import sys
import os
import time
from pathlib import Path
import webbrowser
from xmlrpc.client import DateTime
from datetime import datetime

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
    

async def weather():
             
    with open("psw.json") as file:
        psw = json.load(file)
        ip = requests.get("https://ifconfig.me/ip").text
        loc = requests.get(f'https://ipinfo.io/{ip}/json').json()
        weather = requests.get(f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{loc["loc"]}/{dt.now().strftime('%Y-%m-%dT%H:%M:%S')}?key={psw["weather"]}"
                               ,params={"include": "current", "unitGroup" : "metric", "lang" : "ru"})
        data = weather.json()
        with open("data.json", "w") as f:
            json.dump(data, f)
        with open("data.json") as f:
            data = json.load(f)
        result = { "temp" : data["days"][0]["temp"],
                   "feelslike" : data["days"][0]["feelslike"],
                   "windspeed" : data["days"][0]["windspeed"],
                   "desc" : data["days"][0]["description"]
                }
        return f"Температура на улице {result["temp"]}, ощущается как {result["feelslike"]}, скорость ветра {result["windspeed"]}, в целом о погоде {result["desc"]}"
    
        

def video():
    webbrowser.open("https://www.youtube.com", new=2)
    return "Открываю ютуб"

def search(data):
    webbrowser.open(f"https://www.google.com/search?q={data}", new=2)
    return "Открываю гугл"

def calc():
    os.system('calc')
    return "Открываю калькулятор"

def time():
    time = datetime.now().strftime("%H:%M")
    return f"Текущее время {time}"

def date():
    date = datetime.now().strftime("%d %B %Y")
    return f"Сегоднящняя дата {date}"

def offpc():
    os.system('shutdown \s')
    pass

def offBot():
	sys.exit()


asyncio.run(weather())