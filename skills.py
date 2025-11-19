import sys
import os
import time
from pathlib import Path


def find_exe(filename):
    start = time.time()
    for driver in os.listdrives():
        for root, _, files in os.walk(driver):
            for file in files:
                if filename == file and file.endswith(".exe") and "$Recycle.Bin" not in root:
                        return os.path.join(root, file)
    end = time.time()
    print(start - end)
    return 


def find2_exe(filename):
    start = time.time()
    for driver in os.listdrives():
        print(os.system(f'where /r {driver} "{filename}"'))
    end = time.time()
    print(start - end)
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


print(find3_exe("Tanki.exe"))