#! /usr/bin/env python3

import argparse
import numpy as np
import cv2

from colr import color

import image_processing


def draw_text(image:np.ndarray, max_deph:int, threshold:int, scale:int=1):
    w,h,_ = image.shape
    art_tree = image_processing.ArtTree(None,h,w,2)

    #cv2.imshow("sda", image)
    #cv2.waitKey(1)
    art_tree.update_img(image,max_deph,threshold)

    out_img = np.zeros((w,h,3),np.uint8)
    art_tree.show(out_img)

    #cv2.imshow("img", out_img)
    #cv2.waitKey(0)

    width = int(w/scale)
    height = int(h/scale)

    WINDOW = "RESIZED"
    cv2.namedWindow(WINDOW, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW, 800, 600)
    resized = cv2.resize(out_img,(height, width),interpolation = cv2.INTER_NEAREST)

    cv2.imshow(WINDOW,resized)
    cv2.waitKey(0)

    print(resized)

    for row in resized:
        for char in row:

            print(color('██', fore=(char[2],char[1],char[0]), back=(0, 0, 0)), end='')
        print()


    input()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("image_path", help="path to image that you want to convert")
    parser.add_argument("max_deph", help="max deph of the quad tree",type=int)
    parser.add_argument("threshold", help="smaller threshold will cause more detailed output image",type=int)

    parser.add_argument("-s",'--scale',type=int,default=1)


    args = parser.parse_args()
    image = cv2.imread(args.image_path)
    draw_text(image, args.max_deph, args.threshold,args.scale)
