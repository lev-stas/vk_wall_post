## VK wall post project
This project allows you to post xkcd comics in you VK group

#### Dependencies
You need python3 interpreter to run this script. It is recommended to use virtual environment for this project to avoid libraries versions conflicts. Install virtualenv library, if you don't have it, create virtual environment and activate it
```
pip install virtualenv
python -m virtualenv .venv
source .venv/bin/activate
```
Use `pip3` instead of `pip` and `python3` instead of `python` if you have both python2 and python3 versions.
All needed dependencies are listed in `requirements.txt` file. Use `pip` to install all of them
```
pip install -r requirements.txt
```
Also, you need `VK_ACCOUNT_ACCESS_TOKEN` and `VK_GROUP_ID` environment variables. You should specify them in `.env` file in the same directory `post_comics.py` is located.

#### Usage
To run this script, be sure you are in the project directory, and virtual environment is activated
```
python post_comics.py
```
After you run the script, it will create `images` folder in your project directory, download random xkcd comic book to this folder, post it on your VK group wall and delete the image from your computer.

#### Purpose of a project
This script was performed as a part of API web-services course by [Devman](https://dvmn.org/modules/)


