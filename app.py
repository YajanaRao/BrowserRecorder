from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
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


driver = webdriver.Firefox()
wait = WebDriverWait(driver, 10)
isAlive = True
images = []
duration = 30


def capture_screenshot():
    global isAlive
    global element
    try:
        image = element.screenshot_as_png
        images.append(image)
    except Exception as exp:
        isAlive = False
        print("catpure_screenshot: ",exp)


def child_loop():
    global isAlive
    global element
    print("child loop")
    element = wait.until(EC.visibility_of_element_located((By.ID, 'mainContainer')))
    while isAlive:
        try:
            capture_screenshot()
            # driver.implicitly_wait(0.5) # seconds
        except Exception as exp:
            print("child looper: ",exp)
            isAlive = False




def main():
    global element
    global isAlive
    driver.get("http://18.140.53.243/projects/mapstory-mapbox-new/new/moment-render/trip-render.php?token=9bb1ee1d5d88492f976dc8ea72ccef73")
    element = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, 'splashText')))
    child_thread = threading.Thread(target=child_loop, args=())
    child_thread.start()
    print("waiting...")
    time.sleep(duration)
    print("60s wait is done")
    isAlive = False
    destory()
    print(len(images))
    
    img = cv2.imdecode(np.frombuffer(images[0],dtype=np.uint8), cv2.IMREAD_COLOR)
    height, width, layers = img.shape
    size = (width,height)
    fps = int(len(images)/duration)*2 - 1
    out = cv2.VideoWriter('project.mp4',cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
    current = cv2.imdecode(np.frombuffer(images[i], dtype=np.uint8), cv2.IMREAD_COLOR)
    next = cv2.imdecode(np.frombuffer(images[i+1], dtype=np.uint8), cv2.IMREAD_COLOR)
    img = cv2.addWeighted(current,0.3, next, 0.7,0)
                # print("image", img)
    out.write(img)
    out.release()
    print("video created")

def destory():
    try:
        driver.close()
        driver.quit()
    except Exception as exp:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        destory()
    