# %%
import glob
import pandas as pd
import cv2
import pytesseract

import threading
from queue import Queue

def bucket_invert(img, start_x, start_y):
    candidatos = Queue()
    candidatos.put((start_x, start_y))
    while not candidatos.empty():
        x, y = candidatos.get()
        if x < 0 or y < 0 or x >= img.shape[0] or y >= img.shape[1]:
            continue

        if img[x, y] != 0:
            continue

        img[x, y] = 255
        candidatos.put((x+1, y))
        candidatos.put((x-1, y))
        candidatos.put((x, y+1))
        candidatos.put((x, y-1))
    
    return img

def parsear_file():
    global archivos, total, parseadas

    index = 0
    hashes = {}
    while not archivos.empty():
        file = archivos.get()

        img = cv2.imread(file, cv2.IMREAD_GRAYSCALE)

        # threshold image
        # _, img = cv2.threshold(orig, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # invert image
        img = cv2.bitwise_not(img)

        img = bucket_invert(img, 0, 0)
        img = bucket_invert(img, img.shape[0]-1, 0)
        img = bucket_invert(img, 0, img.shape[1]-1)
        img = bucket_invert(img, img.shape[0]-1, img.shape[1]-1)

        # scale to 300 dpi
        img = cv2.resize(img, None, fx=10, fy=10, interpolation=cv2.INTER_CUBIC)
        
        # pass to ocr
        text = pytesseract.image_to_string(img, config="--psm 6 -c tessedit_char_whitelist=\"0123456789.\"").strip()
        print(text)
        
        index += 1
        parseadas += 1
        filename = file.split("/")[-1].split(".")[0]
        hashes[filename] = text

        if index % 10 == 0:
            print(f"Saving hashes at index {parseadas}/{total}")
            pd.DataFrame({"hash": hashes.keys(), "text": hashes.values()}).to_csv("hashes.csv", index=False,  mode="a", header=False)
            hashes = {}


try:
    hashes = set(pd.read_csv("hashes.csv")["hash"])
except Exception as e:
    print(type(e), e)
    hashes = []

archivos = Queue()
for file in glob.glob("respuestas/*.png"):
    hash_  =  file.split("/")[-1].split(".")[0]
    if hash_ in hashes:
        continue

    archivos.put(file)

parseadas = 0
total = archivos.qsize()
threads = []

print(f"Total: {total}")
for i in range(20):
    t = threading.Thread(target=parsear_file)
    t.start()
    threads.append(t)

try:
    for t in threads:
        t.join()
except KeyboardInterrupt:
    termino = True
    pass

