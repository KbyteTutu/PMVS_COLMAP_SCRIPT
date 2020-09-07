"""
2020年8月31日17:18:10

@author: Tu Kechao
"""

from cv2 import cv2
import numpy as np
import math, time, os, sys, shutil,subprocess,gzip,logging

import UtilityFunctions as Util

from PIL import Image


class BundlePMVSClass:

    # E:\OneDrive\CS800Run\Script4CS800\software\bundler\bin\KeyMatchFull.exe FeatureList.txt matches.init.txt
    # E:\OneDrive\CS800Run\Script4CS800\software\bundler\bin\bundler.exe list.txt --options_file options.txt
    siftExe = r".\software\vlfeat\bin\w32\sift.exe"
    optTxt = r".\software\bundler\bin\options.txt"
    keyMatchExePrefix = r"software\bundler\bin\KeyMatchFull.exe"
    bundleExePrefix = r"software\bundler\bin\bundler.exe"
    bundle2pmvsPrefix = r"software\bundler\bin\Bundle2PMVS.exe"
    radialPrefix = r"software\bundler\bin\RadialUndistort.exe"
    bundle2VisPrefix = r"software\bundler\bin\Bundle2Vis.exe"
    pmvsExePrefix = r"software\pmvs\bin\pmvs2.exe"

    def __init__(self,PhotosInputDir,workDir,f,useMasked):
        self.PhotosInputDir = PhotosInputDir
        self.workDir = workDir
        self.useMasked = useMasked
        self.f = f
        #准备目录
        self.maskedDir = os.path.join(self.workDir,"masked")
        self.photosDir = os.path.join(self.workDir,"photos")
        self.pmvsWorkDir = self.photosDir
        self.currentDir = os.getcwd()
        self.bundler2PmvsExecutable = os.path.join(self.currentDir,self.bundle2pmvsPrefix)
        self.RadialUndistordExecutable = os.path.join(self.currentDir,self.radialPrefix)
        self.Bundle2VisExecutable = os.path.join(self.currentDir,self.bundle2VisPrefix)
        self.pmvsExecutable = os.path.join(self.currentDir,self.pmvsExePrefix)

    def doBundle(self):
        #Run bundle
        self.prepareWorkDir()
        self.photoPreprocess(self.f)
        self.bundleAdjust()

    def prepareWorkDir(self):
        Util.mkCleanDir(self.workDir)
        Util.mkCleanDir(os.path.join(self.workDir,"masked"))
        Util.mkCleanDir(os.path.join(self.workDir,"photos"))


    def photoPreprocess(self,f):
        if self.useMasked == 1:
            self.pmvsWorkDir = self.maskedDir
        elif self.useMasked == 0:
            self.pmvsWorkDir = self.photosDir
        #分开原图和masked图，并在图片文件夹里加统计文件list.txt
        listFile = open(os.path.join(self.pmvsWorkDir,"PhotoList.txt"),"w")
        focal = f
        featureListFile = open(os.path.join(self.pmvsWorkDir,"FeatureList.txt"),"w")
        for root,dirs,files in os.walk(self.PhotosInputDir):
            cnt = 0
            for file in files:
                if "mask" in file:
                    shutil.copy(os.path.join(root,file),os.path.join(self.maskedDir,file))
                    #os.rename(os.path.join(self.maskedDir,file),) 可以重命名
                    if self.useMasked == 1:
                        (fName,_) = os.path.splitext(file)
                        self.extractFeatures(os.path.join(self.pmvsWorkDir,fName))
                        listFile.write("%s 0 %s\n" % (file,focal))
                        featureListFile.write("%s.key\n" % fName)
                        log = "No.%s feature extracted" % cnt
                        logging.info(log)
                        print(log)
                        cnt +=1
                else:
                    shutil.copy(os.path.join(root,file),os.path.join(self.photosDir,file))
                    if self.useMasked == 0:
                        self.pmvsWorkDir = self.photosDir
                        (fName,_) = os.path.splitext(file)
                        self.extractFeatures(os.path.join(self.pmvsWorkDir,fName))
                        listFile.write("%s 0 %s\n" % (file,focal))
                        featureListFile.write("%s.key\n" % fName)
                        log = "No.%s feature extracted" % cnt
                        logging.info(log)
                        print(log)
                        cnt +=1
            dirs[:] = [] #ignore the following dir
        listFile.close()
        featureListFile.close()
        #复制配置文件
        shutil.copy(self.optTxt,self.pmvsWorkDir)

    def extractFeatures(self,photoPath):
        #转换pgm文件用于抽取特征
        outputPGM = "%s.pgm" % photoPath
        temp = Image.open("%s.jpg" % photoPath)
        temp.convert("L").save(outputPGM)
        #注意此处是带着jpg加的后缀
        subprocess.call([self.siftExe,"%s.pgm"%photoPath,"-o","%s.key"%photoPath])
        # perform conversion to David Lowe's format
        vlfeatTextFile = open("%s.key" % photoPath, "r")
        loweGzipFile = gzip.open("%s.key.gz" % photoPath, "wb")
        featureStrings = vlfeatTextFile.readlines()
        numFeatures = len(featureStrings)
        # py3需要转码
        # write header
        header = "%s 128\n" % numFeatures
        loweGzipFile.write(header.encode())
        for featureString in featureStrings:
            features = featureString.split()
            # swap features[0] and features[1]
            tmp = features[0]
            features[0] = features[1]
            features[1] = tmp
            i1 = 0
            for i2 in (4,24,44,64,84,104,124,132):
                line = "%s\n" % " ".join(features[i1:i2])
                loweGzipFile.write(line.encode())
                i1 = i2
        loweGzipFile.close()
        vlfeatTextFile.close()
        # remove original SIFT file
        #清理
        os.remove(outputPGM)
        os.remove("%s.key" % photoPath)

    def bundleAdjust(self):
        Util.mkCleanDir(os.path.join(self.pmvsWorkDir,"bundle"))
        os.chdir(self.pmvsWorkDir)
        keyMatchExe = os.path.join(self.currentDir,self.keyMatchExePrefix)
        bundleExe = os.path.join(self.currentDir,self.bundleExePrefix)
        subprocess.call([keyMatchExe,"FeatureList.txt","matches.init.txt"])
        subprocess.call([bundleExe,"PhotoList.txt","--options_file","options.txt"])
        os.chdir(self.currentDir)

    def doPMVS(self):
        logging.info("\nPerforming Bundler2PMVS conversion...")
        os.chdir(self.pmvsWorkDir)
        os.mkdir("pmvs")

        # Create directory structure
        os.mkdir("pmvs/txt")
        os.mkdir("pmvs/visualize")
        os.mkdir("pmvs/models")

        #$BASE_PATH/bin32/Bundle2PMVS.exe list.txt  bundle/bundle.out
        print("Running Bundle2PMVS to generate geometry and converted camera file")
        subprocess.call([self.bundler2PmvsExecutable, "PhotoList.txt", "bundle/bundle.out"])

        # Apply radial undistortion to the images
        print("Running RadialUndistort to undistort input images")
        subprocess.call([self.RadialUndistordExecutable, "PhotoList.txt", "bundle/bundle.out", "pmvs"])

        print("Running Bundle2Vis to generate vis.dat")
        subprocess.call([self.Bundle2VisExecutable, "pmvs/bundle.rd.out", "pmvs/vis.dat"])

        os.chdir(os.path.join(self.pmvsWorkDir,"pmvs"))
        #Rename all the files to the correct name
        undistortTextFile = open("list.rd.txt", "r")
        imagesStrings = undistortTextFile.readlines()
        print("Move files in the correct directory")
        cpt = 0
        for imageString in imagesStrings:
          image = imageString.split(".")
          # sh => mv pmvs/et001.rd.jpg pmvs/visualize/00000000.jpg
          shutil.copy(image[0]+".rd.jpg", "visualize/%08d.jpg"%cpt)
          # sh => mv pmvs/00000000.txt pmvs/txt/
          shutil.copy("%08d.txt"%cpt, "txt/%08d.txt"%cpt)
          os.remove(image[0]+".rd.jpg")
          os.remove("%08d.txt"%cpt)
          cpt+=1

        undistortTextFile.close()

        os.chdir(os.path.join(self.pmvsWorkDir,"pmvs"))
        subprocess.call([self.pmvsExecutable, "./", "pmvs_options.txt"])

        logging.info("Finished!")



if __name__ == "__main__":
    ins = BundlePMVSClass(r"E:\OneDrive\CS800Run\Script4CS800\5a57542f333d180827dfc132\blended_images",r"E:\OneDrive\CS800Run\Script4CS800\workPath",789.48,1)
    ins.doBundle()
    ins.doPMVS()