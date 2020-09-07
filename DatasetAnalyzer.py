"""
2020年9月6日22:35:24

@author: Tu Kechao
"""

from cv2 import cv2
import numpy as np
import math, time, os, sys, shutil,subprocess,gzip,logging

import UtilityFunctions as Util

class myError(Exception):
    def __init__(self,ErrorInfo):
        super().__init__(self) #初始化父类
        self.errorinfo=ErrorInfo
    def __str__(self):
        return self.errorinfo

class datasetAnalyzer:
    def __init__(self,path):
        #input the folder path of BlendedMVS dataset
        self.path = path
        self.currentDir = os.getcwd()

        if os.path.isfile(os.path.join(self.currentDir,path)):
            print("Wrong input")
            raise myError("Input is not a folder")
        if os.path.isdir(os.path.join(self.currentDir,self.path,"blended_images"))==False:
            raise myError("image missing")
        if os.path.isdir(os.path.join(self.currentDir,self.path,"cams"))==False:
            raise myError("camera info missing")
        if os.path.isdir(os.path.join(self.currentDir,self.path,"rendered_depth_maps"))==False:
            raise myError("depth maps missing")

    def getPhotoPath(self):
        return os.path.join(self.path,"blended_images")

    def getDepthMapsPath(self):
        return os.path.join(self.path,"rendered_depth_maps")

    def getCamsPath(self):
        return os.path.join(self.path,"cams")

    def getExtrinsicPara(self):
        info = self.analyzeCams()
        return np.loadtxt(info[1:5:1])

    def getIntrinsicPara(self):
        info = self.analyzeCams()
        return np.loadtxt(info[7:10:1])

    def getRadialDistortionPara(self):
        info = self.analyzeCams()
        return np.loadtxt(info[11:])

    def analyzeCams(self):
        #Need some more code,for now just analyze first file.
        camsInfoPath = os.path.join(self.getCamsPath(),"00000000_cam.txt")
        f = open(camsInfoPath)
        camsInfo = f.readlines()
        f.close()

        return camsInfo

if __name__ == "__main__":
    ins = datasetAnalyzer(r".\example\5adc6bd52430a05ecb2ffb85")
    print(ins.getExtrinsicPara())
    print(ins.getIntrinsicPara())
    print(ins.getRadialDistortionPara())






