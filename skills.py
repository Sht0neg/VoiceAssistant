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
    #loc = requests.get('https://ipapi.co/latlong/').text
    #print(loc)
    loc = "55.785800,37.625600"

    with open("psw.json") as file:
        key = json.load(file)["weather"]
        weather = requests.get("http://api.weatherapi.com/v1/forecast.json", params={"key": key, "q": loc, "lang": "ru", "days": 2})
        data = weather.json()
        t = data["current"]["temp_c"]
        con = data["current"]["condition"]["text"]
        wind = data["current"]["wind_kph"]
        t_feel = data["current"]["feelslike_c"]

        print(data["forecast"])

    #print([loc.json()["latitude"], loc.json()["longitude"]])

def video():
     webbrowser.open("https://www.youtube.com", new=2)

def search(data):
     webbrowser.open(f"https://www.google.com/search?q={data}", new=2)

def calc():
     os.system('calc')



def offpc():
    #os.system('shutdown \s')
    pass

def offBot():
	sys.exit()


async def passive():
	print("!")

print(time.strftime("%X"))
asyncio.run(path_of_apps_in_json())
print(time.strftime("%X"))