# Imports 
import sys
import os
import subprocess
from shlex import join
from subprocess import PIPE, TimeoutExpired

# Command Utils
def update_requirements_file():
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')
    command = subprocess.Popen(["pip-compile", "requirements.in"], stdin=PIPE, stdout=PIPE, stderr=sys.stderr, encoding="utf-8")
    try:
        outs, errs = command.communicate(timeout=9)
    except TimeoutExpired:
        command.kill()
        
    print("requirements file updated")
    

def add_to_in_file(module, module_version = None):
    if module_version:
        if os.path.basename(os.getcwd()) == 'script':
            os.chdir('..')
        with open('requirements.in', 'a', encoding='utf-8') as r:
            r.write(f"\n{module}=={module_version}")
    else:
        if os.path.basename(os.getcwd()) == 'script':
            os.chdir('..')
        with open('requirements.in', 'a', encoding='utf-8') as r:
            r.write(f"\n{module}")
    update_requirements_file()
    
def uninstall_module(module):
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')
    with open('requirements.in', 'r', encoding="utf-8") as r:
        lines = r.readlines()
    with open('requirements.in', 'w', encoding="utf-8") as r:
        for line in lines:
            if line.strip('\n') != module:
                r.write(line)
    update_requirements_file()
    command = subprocess.Popen(["pip", "uninstall", module, "-y"], stdin=PIPE, stdout=PIPE, stderr=sys.stderr)
    try:
        outs, errs = command.communicate(timeout=7)
    except TimeoutExpired:
        command.kill()
    print(f"succefully uninstalled: {module}")
            
def un_install():
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')
    print("Uninstalling modules...")
    subprocess.run(['pip', 'uninstall', '-r', 'requirements.txt', '-y'], stdin=sys.stdout, stdout=sys.stdin, stderr=sys.stderr)
    print("Modules successfully uninstalled")
    
def install():
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')   
    print("Installing modules...")
    subprocess.run(['pip', 'install', '-r', 'requirements.txt', '--user', '--no-warn-script-location'], stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)   
    print("Successfully installed modules")
    

def view(in_terminal=True, in_file=False, in_vscode=False):
    if os.path.basename(os.getcwd()) == 'script':
        os.chdir('..')   
    if in_terminal:
        print("Opening file in terminal...")
        print("-----------------------------")
        with open('requirements.txt', 'r', encoding="utf-8") as r:
            lines = r.readlines()
        for line in lines:
            print(line)
    if in_file:
        print("Opening file outside of terminal...")
        if in_vscode:
            try:
                subprocess.run(["code", "requirements.txt"])
            except FileNotFoundError:
                sys.exit(os.system("code requirements.txt"))
        try:
            subprocess.run(["start", "requirements.txt"])
        except FileNotFoundError:
            sys.exit(os.system("start requirements.txt"))
   
def help():
    print("""Commands:
             update: Updates requirements.txt
             add: Adds module name and version(optional) to requirements.in | Args: ( module: Name of Module | version (optional): Version of the module ) 
             alluninstall: Uninstalls all modules
             uninstall: Uninstalls specified module and removes it from requirements.txt | Arg: (module: Name of Module)
             install: Installs all modules
             help: loads this help descriptions
             view: view requirements file | Args (-i (optional): opens requirements.txt file outside of the terminal | -v (optional | Usage: -i -v): opens requirements.txt file in vscode)
             """) 
    
# Command script
if sys.argv[1] == 'update':
    update_requirements_file()
elif sys.argv[1] == 'add':
    try:
        sys.argv[2]
    except IndexError:
        print("Module name is required")
    else:
        try:
            add_to_in_file(sys.argv[2], sys.argv[3])
        except IndexError:
            add_to_in_file(sys.argv[2])
        finally:
            print(f"{sys.argv[2]} has been added to requirements.in")
elif sys.argv[1] == 'alluninstall':
    un_install()
elif sys.argv[1] == 'uninstall':
    try:
        sys.argv[2]
    except IndexError:
        print("Module name required")
    else:
        uninstall_module(sys.argv[2])
elif sys.argv[1] == 'install':
    install()
    
elif sys.argv[1] == 'view':
    try:
        sys.argv[2]
    except IndexError:
        view()
    else:
        try:
            sys.argv[3]
        except IndexError:
            if sys.argv[2] == '-i':
                view(False, True)
            else:
                print(f"Unknown option: {sys.argv[2]}")
        else:
            if join([sys.argv[2], sys.argv[3]]) == "-i -v":
                view(False, True, True)
            else:
                print(f"Unkown option: {join([sys.argv[2], sys.argv[3]])}")
elif sys.argv[1] == 'help':
    help()
else:
    print(f"Unknown command: {sys.argv[1]}")
    