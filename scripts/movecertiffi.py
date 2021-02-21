#  Imports
import os
import shutil

# script
if __name__ == '__main__':
    if os.path.basename(os.getcwd()) == "scripts":
        os.chdir('..')
    file_list = ["key.pem", "cert.pem"]
    for file in file_list:
        shutil.move(file, 'scripts', shutil.copytree)