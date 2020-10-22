# Projects-Website
My Projects Website Guide for Installation
# 
# Installation Requirements
* Python (*Recommended minimum version:* 3.8.0 *Recommended maximum version:* 3.8.5)
* Code Dependencies
#
# **Get Started**
*In order to utilize this website, you must install python and the dependencies. You will learn how to install python then how to install the dependencies*

#### Python Installation:
*In order to install python head over to the [Python 3.5 release](https://www.python.org/downloads/release/python-385/) link and scroll down to the Files Section.
Click on "macOS 64-bit installer" if your using a Macbook but otherwise if your using a Windows computer, click on "Windows x86-64 executable installer" if your
computer has an AMD64/EMT64T/x64 otherwise click on "Windows x86 executable installer". Then once downloaded, check the checkbox which label states "Add Python 3.8 
to PATH". This is necessary for the installation of the dependencies later in the guide. after the installation, please follow this instructions carefully:*
##### For Mac Users
**Steps:**
1. open terminal

2. check if the python installation was succesful. To do this, type `python` in the terminal. If the python terminal IDE pops up then the installation was succesful.

3. Exit out of the terminal IDE through running:
```python
exit()
```

4. Run the command below in the terminal to ensure that pip was also installed (*pip is essential for installing external python modules*):
```shell
pip --version
```
If a number appeared as the result then pip is installed. If there was some type of error then check out the 
[installation document](https://pip.pypa.io/en/stable/installing/) to fix this problem. 

5. Make sure to change to the Desktop (or which ever folder you want the source code to be in, if you need further help with navigating with the terminal, check out: 
[how to use terminal for mac](https://macpaw.com/how-to/use-terminal-on-mac))

6. Install [git](https://git-scm.com/downloads) (*git will be the main source for installing the websites source code*)

7. Once git is installed, run:
```shell
git clone https://github.com/SLey3/Projects-Website.git
```
*This should have installed the project-website folder in your home directory*

8. Run the following command in the terminal:
```shell
cd Projects-Website
```

9. Now that your in the website's folder, run:
```shell
pip install -r requirements.txt
```
This will install all of the dependencies for the website
#
##### For Window Users
1. Install git at [git for windows](https://git-scm.com/download/win) (*Download will start automatically*)

2. once git is installed, there should be a git app, open it and run:
```shell
git --version
```
*This is to test whether git is installed correctly or not*

3. Run the command below in the git terminal to ensure that pip was also installed (*pip is essential for installing external python modules*):
```shell
pip --version
```
*if there was an error, following this instructions to install pip:*

3. a) Open [get-pip source code](https://bootstrap.pypa.io/get-pip.py) in a new tab in your browser
3. b) copy all of the code with `ctrl + a` + `ctrl + c`
3. c) Go back to the git terminal and navigate to the home folder (*If you don't know how to do this, check out: 
[using cd and ls in windows terminal](https://wiki.communitydata.science/Windows_terminal_navigation)
3. d) Run the following commands:
```shell
touch get-pip.py
open get-pip.py
```
3. e) paste the copied code into the file and save the file
3. f) close the file and in the git terminal run:
```shell
python get-pip.py
```
*This will install pip*
3. g) Test out `pip --version` again. If this does not work, try uninstalling python then reinstalling it.

4. In the git terminal run:
```shell 
git clone https://github.com/SLey3/Projects-Website.git
```
*Now you should have the Projects-Website folder in the home directory*

5. Run the following commands in order:
```shell
cd Projects-Webiste
pip install -r requirements.txt
```
# 

#### How to run the website
*Make sure to follow **all** of the instructions above before you activate the website.*
1. In the terminal or git terminal make sure your in the Projects-Website directory.

2. Then run:
```shell
cd src
```

3. After your in the source folder, in order to activate the website run:
```
python main.py
```
*This will activate the website*

4. The program will give you a localhost url

5. copy the localhost url and paste it in a browser

## End of Guide
