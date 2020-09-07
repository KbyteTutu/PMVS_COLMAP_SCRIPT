"""
2020年6月28日02:57:35

@author: Tu Kechao
"""

from cv2 import cv2
import numpy as np
import math
import time
import os
import shutil

def perf_time(func):
    def wrap(*args):
        start = time.time()
        result = func(*args)
        cost = time.time() - start
        print("{} used {} s".format(func.__name__, cost))
        return result
    return wrap

def L2Norm(actualValue,predictedValue):
    return np.sum(np.power((actualValue-predictedValue),2))

def loadImage(path):
    return cv2.imread(path)

def loadImageGray(path):
    return cv2.imread(path,0)

def analyzeFilePath(path):
    (filepath,tempfilename) = os.path.split(path)
    (filename,extension) = os.path.splitext(tempfilename)
    return (filename,filepath,extension)

def combinePath(path,addition,ext = ''):
    filename,filepath,extension = analyzeFilePath(path)
    if ext=='':
        ext = extension
    temppath = os.path.join(filepath,addition)
    if os.path.isdir(temppath)== False:
        os.mkdir(temppath)
    # result = filepath + "\\" + filename + addition + extension
    result = os.path.join(filepath,addition,filename+ext)
    return result

def mkCleanDir(path):
    if os.path.isdir(path):
        #先清空再创建
        shutil.rmtree(path)
        os.mkdir(path)
    else:
        os.mkdir(path)

def getRange(data):
    xmin = xmax = pmin = pwmin = data[0][0]
    ymin = ymax = pmax = pwmax = data[0][1]
    cnt =0
    for i in range(len(data)):
        Px, Py, Pphi, pw = data[i]
        if Px < xmin:
            xmin = Px
        if Py < ymin:
            ymin = Py
        if Pphi < pmin:
            pmin = Pphi
        if pw < pwmin:
            pwmin = pw
        if Px > xmax:
            xmax = Px
        if Py > ymax:
            ymax = Py
        if Pphi > pmax:
            pmax = Pphi
        if pw >pwmax:
            pwmax = pw

        cnt += cnt
    return (xmin, xmax, ymin, ymax, pmin, pmax,pwmin,pwmax,cnt)

def getContourPixel(data):
    #可以想办法优化
    imgH,imgW,_ = data.shape
    re = []
    for i in range(imgH):
        for j in range(imgW):
            if data[i,j]!=255:
                re.append((i,j))
    return re

def edgeStrength(fx,fy):
    # get edge strength
    edge = np.sqrt(np.power(fx, 2) + np.power(fy, 2))
    fx = np.maximum(fx, 1e-5)

    # get edge angle
    angle = np.arctan(fy / fx)
    # angle = np.degrees(angle)

    return edge, angle