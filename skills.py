import sys
import os


def find_exe(filename):
    for driver in os.listdrives():
        for root, _, files in os.walk(driver):
            for file in files:
                if filename == file and file.endswith(".exe") and "$Recycle.Bin" not in root:
                        return os.path.join(root, file)
    return 
            

def offpc():
    os.system('shutdown \s')

def offBot():
	sys.exit()


def passive():
	pass


find_exe("VirtualBox.exe")