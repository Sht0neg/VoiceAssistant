import sys
import os
import time
from pathlib import Path
import webbrowser
import requests
import json

def video():
     webbrowser.open("https://www.youtube.com", new=2)

def search(data):
     webbrowser.open(f"https://www.google.com/search?q={data}")

def calc():
     os.system('calc')

def find_exe(filename):
    for driver in os.listdrives():
        for root, _, files in os.walk(driver):
            for file in files:
                if filename == file and file.endswith(".exe") and "$Recycle.Bin" not in root:
                        return os.path.join(root, file)
    return 


def find3_exe(filename):
    for driver in os.listdrives():
        for file_path in Path(driver).rglob('Tanki.exe'):
            print(file_path)
    return 

def offpc():
    #os.system('shutdown \s')
    pass

def offBot():
	sys.exit()


def passive():
	pass

