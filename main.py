from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
import sys
import time
import datetime
import threading
import cv2
import numpy as np
import glob
import io
from PIL import Image
import os, shutil
import schedule
import base64
import argparse

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

isAlive = True
images = []

parser = argparse.ArgumentParser()
parser.add_argument("--browser", help="Select browser to record")
parser.add_argument("--url", help="Website url")
parser.add_argument("--duration", help="Duration of the Execution, Default is 30 seconds", type=int)
args = parser.parse_args()

def clean_up():
    folder = os.path.join(ROOT_DIR,'Screenshots')
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def run_threaded(job_func):
    job = threading.Thread(target=job_func)
    job.start()

def save_screenshot(image):
    img = Image.open(io.BytesIO(image))
    img.save(screenshot_path())

def capture_screenshot():
    # global canvas
    try:
        image = driver.get_screenshot_as_png()
        images.append(image)

    except Exception as exp:
        pass
        # schedule.CancelJob
        print("catpure_screenshot: ",exp)
        isAlive = False
    
def looper():
    global isAlive
    while isAlive:
        try:
            schedule.run_pending()
        except Exception as exp:
            print("looper: ",exp)
            isAlive = False


def screenshot_path():
    date_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    return os.path.join(ROOT_DIR, 'Screenshots',date_string+'.png')

def main(url):
    # global canvas
    global isAlive
    driver.get(url)
    time.sleep(3)
    # canvas = driver.find_element_by_id('mainContainer')
    schedule.every(0.1).seconds.do(run_threaded, capture_screenshot)
    t = threading.Thread(target=looper, args=())
    t.start()
    print("waiting...")
    time.sleep(30)
    print("60s wait is done")
    isAlive = False
    destory()
    print(len(images))
    
    img = cv2.imdecode(np.frombuffer(images[0],dtype=np.uint8), cv2.IMREAD_COLOR)
    height, width, layers = img.shape
    size = (width,height)

    out = cv2.VideoWriter('project.mp4',cv2.VideoWriter_fourcc(*'DIVX'), 15, size)
    
    for i in range(len(images)):
        img = cv2.imdecode(np.frombuffer(images[i], dtype=np.uint8), cv2.IMREAD_COLOR)
        out.write(img)
    out.release()
    print("video created")

def destory():
    try:
        driver.close()
        driver.quit()
    except Exception as exp:
        pass
    

if args.url:
    try:
        if args.browser == "chrome":
            driver = webdriver.Chrome()
        else:
            driver = webdriver.Firefox()
        
        clean_up()
        main(args.url)
    except KeyboardInterrupt:
        destory()

else:
    print("url is required")