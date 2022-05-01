#! /usr/bin/env python3

import cv2
import numpy as np
import math as m
from classes import TreeBranch

from pygame import Rect

from typing import List
from typing import Callable

from sys import argv


def empty(x):
    pass

class ArtTree(TreeBranch):
    colour:List[int]
    depth:int
    def __init__(self,*args, depth:int=0):
        super().__init__(*args)
        self.depth = depth
        self.colour = (0,0,0)

    def update_img(self,img:np.ndarray, max_depth:int, threashold:int):

        #print(f"{self.rect.h}, {self.rect.w}, ({self.rect.y},{self.rect.x})")
        mean, diversity = cv2.meanStdDev(img[self.rect.y:self.rect.y+self.rect.h-1,self.rect.x:self.rect.x+self.rect.w-1])
        #np.array([np.std([x for x in img[:,:,y]]) for y in range(3)])

        #print("Diversity: ", diversity)

        # if out of depth then call it a day
        if(self.depth>=max_depth or np.any(diversity<=threashold)):
            self.colour = np.floor(mean.ravel())
            self.children = list()
        else:
            if not self.children:
                self.subdivide(2,depth=self.depth+1)
            for c in self.children:
                c.update_img(img,max_depth,threashold)

    def show(self,img:np.ndarray, sh:int=None, sw:int=None):
        if sh==None:
            w,h,_ = img.shape
            sh = int(self.rect.h / h)
            sw = int(self.rect.w / w)
        #print(img)
        #print(f"{self.rect.w}, {self.rect.h}")

        if not self.children:
            cv2.rectangle(img,(self.rect.x,self.rect.y),((self.rect.x+self.rect.w), (self.rect.y+self.rect.h)),self.colour,-1)
            #img[self.rect.y:self.rect.y+self.rect.h, self.rect.x:self.rect.x+self.rect.w                ] = self.colour
        else:
            for c in self.children:
                c.show(img,sh,sw)

THRESH = 50
MINSIZE = 3

imgBox = None
img = None
pixelated = None

def update_thresh(x):
    global imgBox, pixelated, THRESH, img
    THRESH = x
    imgBox.update_img(img, MINSIZE,THRESH)#,standard_deviation)
    imgBox.show(pixelated)
    print("CALC_END")
def update_depth(x):
    global imgBox, pixelated,MINSIZE,img
    MINSIZE = x
    imgBox.update_img(img, MINSIZE,THRESH)#,standard_deviation)
    imgBox.show(pixelated)
    print("CALC_END")

def main():
    global imgBox, img, pixelated

    WINDOW = "imagePixelate"
    cv2.namedWindow(WINDOW)


    img = cv2.imread(argv[1])
    pixelated = np.zeros(img.shape,dtype=np.uint8)

    imgBox = ArtTree(Rect(0,0,img.shape[1],img.shape[0]),2)

    cv2.createTrackbar("threashold",WINDOW,50,255,update_thresh)
    cv2.createTrackbar("minsize",WINDOW,3,10,update_depth)

    imgBox.update_img(img, MINSIZE,THRESH)#, standard_deviation)
    imgBox.show(pixelated)

    while(1):

        k = cv2.waitKey(1)
        if k == 27:
            break

        cv2.imshow(WINDOW,np.concatenate((img,pixelated),axis=1))
        cv2.waitKey(1)


    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
