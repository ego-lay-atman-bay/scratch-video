# scratch-video
A program to import a video into scratch.

## Installation

# Installation instructions:

1. Download `scratch-video.zip` from the [releases tab](https://github.com/ego-lay-atman-bay/scratch-video/releases)
2. Unzip it into it's own folder (e.g. a folder called scratch-video)
3. Make sure you have [Python 3](https://www.python.org/downloads/) installed
4. Open your command prompt in the scratch-video folder
5. Enter
```
pip install -r requirements.txt
```
or if that doesn't work 
```
py -m pip install -r requirements.txt
```
6. And now you're all set to run scratchVideo.py

When you run it for the first time, it'll download the base project, and put it in a folder called `project`. It won't download it again, unless it detects `project.json` and `video.sb3` are missing.