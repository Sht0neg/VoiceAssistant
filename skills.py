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
import subprocess
import asyncio


def find_exe(apps, exes):
    result = dict()
    for driver in os.listdrives():
        for root, _, files in os.walk(driver):
            for file in files:
                for name, filename in zip(apps, exes):
                    if (filename + ".exe").lower() == file.lower() and file.lower().endswith(".exe") and "$Recycle.Bin" not in root and "$PatchCache$" not in root and "WinSxS" not in root:
                        result[name[1]] = re.sub(r'Program Files[^\\]*', f'"{re.search(r'Program Files[^\\]*', 
                            os.path.join(root, file)).group(0)}"', os.path.join(root, file)) \
                            if re.search(r'Program Files[^\\]*', os.path.join(root, file)) else os.path.join(root, file)
    return result


def path_of_apps_in_json():
    apps = [["Word" , 0], ["Exel", 1], ["Powerpoint", 2], ["Telegram", 3], ["Discord", 4], ["Whatsapp", 5], ["Paint", 6], ["AnyDesk", 7], ["VirtualBox", 8], ["VMWare", 9],
            ["Steam", 10],
            ["CS", 11], ["Dota", 12], ["Valorant", 13], ["Apex", 14], ["Fortnite", 15], ["League", 16], ["PUBG", 17], ["GTA5", 18], ["MirTankov", 19], ["WOT", 20], ["Warthunder", 21],
            ["Genshin", 22], ["ZZZ", 23], ["HonkaiStarRail", 24]]
    exes = ["WINWORD", "EXCEL", "POWERPNT", "Telegram", "Discord", "WhatsApp", "mspaint", "AnyDesk", "VirtualBox",
            "vmware", "Steam",
            "cs2", "dota2", "VALORANT-Win64-Shipping", "r5apex", "FortiniteClient-Win64-Shipping", "RiotClientServices",
            "TslGame", "GTA5", "Tanki", "worldoftanks", "aces_BE", "GenshinImpact", "ZenlesZoneZero", "StarRail"]

    result = find_exe(apps, exes)
    with open("apps.json", "w") as file:
        json.dump(result, file, separators=(',\n', ': '))
    
def game(index):
    try:
        with open("apps.json") as f:
            data = json.load(f)
            subprocess.Popen(
            f'{data[str(index)]}',
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL, 
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
            )
    except Exception as e:
        pass

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
