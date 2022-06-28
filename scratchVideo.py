import json
import os
import shutil
import hashlib
# import tkinter as tk
from tkinter import Tcl, filedialog
import zipfile
# from datetime import timedelta
import cv2
import moviepy.editor
# import numpy as np
import os
from pydub import AudioSegment
from PIL import Image
import mimetypes
import wget
import time

assets = []
project = {}
root = os.getcwd()

# The only script that worked the way I wanted it to. Original script: https://stackoverflow.com/a/49321070/17129659 Thank you so much @Bence Kővári
def getFrames(vid, output, rate=0.5, frameName='frame'):
    vidcap = cv2.VideoCapture(vid)
    frames = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    clip = moviepy.editor.VideoFileClip(vid)
    seconds = clip.duration
    print('durration: ' + str(seconds))
    time.sleep(1)
    count = 0
    frame = 0
    if not os.path.isdir(output):
        os.mkdir(output)
    success = True
    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC,frame*1000)      
        success,image = vidcap.read()
        # print(cv2.CAP_PROP_POS_MSEC)
        # print(success)

        ## Stop when last frame is identified
        # image_last = cv2.imread(output + "/" + frameName + "-%d.png" % count)
        print(frame)
        print('extracting frame ' + frameName + '-%d.png' % count)
        cv2.imwrite(output + "/" + frameName + "-%d.png" % count, image)     # save frame as PNG file
        if frame > seconds:
            break
        frame += rate
        count += 1

def getAudio(video):
    audio = moviepy.editor.AudioFileClip(video)
    filename = root + '/video/audio.mp3'
    audio.write_audiofile(filename)
    with open(filename, 'rb') as file:
        contents = file.read()
    id = genAssetId(contents)
    assets.append(['video/audio.mp3', id + '.mp3'])
    print('extracted audio')
    
    audio = AudioSegment.from_mp3(filename)

    rate = audio.frame_rate
    sampleCount = audio.frame_count()

    sound = {}

    sound['assetId'] = id
    sound['name'] = 'Audio'
    sound['dataFormat'] = 'mp3'
    sound['rate'] = rate
    sound['sampleCount']  = sampleCount
    sound['md5ext'] = id + '.mp3'

    project['targets'][1]['sounds'].append(sound)

    print('saved audio to json')


def getIds():
    costumes = project['targets'][1]['costumes']

def genAssetId(file):
    try:
        file = file.encode()
    except:
        pass
    result = hashlib.md5(file)
    id = result.hexdigest()
    return id

def getFilePath(dir):
  
    # initializing empty file paths list
    file_paths = []
  
    # crawling through directory and subdirectories
    for root, directories, files in os.walk(dir):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
  
    # returning all file paths
    return file_paths

def resizeCostume(path, size=(960,720)):
    image = cv2.imread(path)
    h,w = image.shape[:2]

    widthFactor = w/size[0]
    heightFactor = h/size[1]

    if widthFactor < heightFactor:
        newSize = (int(w/heightFactor), int(h/heightFactor))
    else:
        newSize = (int(w/widthFactor), int(h/widthFactor))

    newImage = cv2.resize(image, newSize)
    cv2.imwrite(path, newImage)

    

def export():
    try:
        os.mkdir(root + '/export')
    except:
        pass

    file = open(root + '/export/project.json', 'w+')
    json.dump(project, file, indent=2)
    file.close()

    for cst in assets:
        src = root + '/' + cst[0]
        dst = root + '/export/' + cst[1]

        shutil.copyfile(src, dst)

    file_paths = getFilePath(root + '/export')

    save_path = filedialog.asksaveasfilename(title='save project', defaultextension='*.sb3', initialfile='export.sb3', filetypes=(('scratch 3 project','*.sb3'),('zipped folder','*.zip')))
    with zipfile.ZipFile(save_path, 'w') as zip:
        for file in file_paths:
            zipname = os.path.basename(file)
            zip.write(file, zipname)
            print('added "' + zipname + '" to zip')

    zip.close()
    print('completed export')

def scanVideo(path):
    files = os.listdir(path)
    files = Tcl().call('lsort', '-dict', files)
    for f in files:
        type = f.rpartition('.')[2]
        print(mimetypes.guess_type(f))
        if not type == 'mp3':
            filepath = path + '/' + f
            resizeCostume(filepath)
            with open(filepath, 'rb') as file:
                contents = file.read()
            id = genAssetId(contents)

            img = Image.open(filepath)
            w,h = img.size

            print('adding costume: ' + f)
            costume = {}
            costume['assetId'] = id
            costume['name'] = f.rpartition('.')[0]
            costume['bitmapResolution'] = 2
            costume['md5ext'] = id + '.' + type
            costume['dataFormat'] = type
            costume['rotationCenterX'] = w/2
            costume['rotationCenterY'] = h/2
            project['targets'][1]['costumes'].append(costume)
            assets.append(['video/' + f, id + '.' + type])

    print('finished adding costumes')

def loadJson(path):
    global project
    file = open(path, 'r')
    project = json.load(file)
    file.close()

    for target in project['targets']:
        for cst in target['costumes']:
            assets.append(['project/' + cst['md5ext'], cst['md5ext']])

    print('json loaded')

def exportVideo(videoPath, fps=10, costumeName='video'):
    try:
        fps = int(fps)
    except:
        pass
    getFrames(videoPath,'video', 1/fps, costumeName)
    # exportFrames(videoPath, fps, costumeName)
    getAudio(videoPath)
    project['targets'][1]['blocks']['e']['inputs']['VALUE'][1][1] = fps
    project['targets'][1]['blocks']['h']['inputs']['STRING1'][1][1] = costumeName + '-'

def loadProject():
    try:
        print('loading project.json')
        loadJson('project/project.json')
    except:
        print('could not load project.json\ncreating project folder')
        try:
            os.mkdir('project')
        except:
            print('project folder already exists')
            pass

        url = "https://ego-lay-atman-bay.github.io/scratch-video/project/video.sb3"
        print('downloading ' + url)
        file = root + '/project/video.sb3'
        wget.download(url, file)
        print('\nsuccessfully downloaded video.sb3')

        print('extracting video.sb3')
        with zipfile.ZipFile(file, 'r') as zip:
            zip.printdir()
            zip.extractall('project')
            print('Done!')
        
        print('loading project.json')
        loadJson('project/project.json')


def main():
    try:
        print('removing /export')
        shutil.rmtree('export')
    except:
        print('failed to remove /export')
    try:
        print('removing /video')
        shutil.rmtree('video')
    except:
        print('failed to remove /video')

    loadProject()
    file = filedialog.askopenfile(mode='r', title='choose video',defaultextension='*.mp4',filetypes=(("mp4 video", "*.mp4"),("mov video", "*.mov"),("All Files","*.*")))
    fps = input('fps (longer videos should have lower fps, shorter videos are fine to have a higher fps.):\n')
    exportVideo(file.name, fps, file.name.split("/")[-1].rpartition('.')[0])
    scanVideo('video')
    export()

if __name__ == '__main__':
    main()
