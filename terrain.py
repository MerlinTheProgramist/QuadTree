#! /usr/bin/env python3

import pygame as pg

from pygame import Vector2, Rect
from typing import List, Generic, TypeVar, Callable
from classes import TreeBranch

import cv2
import numpy as np
import argparse

DEBUG = False

WIDTH = 1000
HEIGHT = 1000
FPS = 60
world = None

G_FORCE = 0.5

#colors
BACKGROUND = (0,0,0)



def debug(func:Callable):
    key = False
    while not key:
        key = pg.key.get_pressed()["a"]


class FillTree(TreeBranch):
    state:bool
    max_deph:int

    rect_corners:List[Vector2]

    def __init__(self,*args,state:bool=True, max_deph:int=10):
        super().__init__(*args)
        self.state = state
        self.max_deph = max_deph

        self.rect_corners = [
            self.rect.bottomleft,
            self.rect.bottomright,
            self.rect.topleft,
            self.rect.topright
        ]

    def set_state(self, state:bool):
        self.state = state

    def rectangle_hole(self, pos:Vector2, r:int):
        # if already holled
        if(not self.state and not self.children): return

        c_dist_x = abs(pos.x - self.rect.x - self.rect.width/2);
        c_dist_y = abs(pos.y - self.rect.y - self.rect.height/2);

        # if no interraction at all
        if c_dist_x > r+self.rect.width/2 or c_dist_y > r+self.rect.height/2:
            return

        # if  fully in bounds of the rect
        if c_dist_x+self.rect.width/2 <= r and c_dist_y+self.rect.height/2 <= r:
            self.set_state(False)
            return

        # if max deph exited holl this:
        if (self.max_deph==0):
            #self.set_state(False)
            return

        if not self.children:
            # if self not the right resolution
            self.subdivide(2,state=True, max_deph=self.max_deph-1)

        # check for all children
        for child in self.children:
            child.rectangle_hole(pos,r)

    def circle_hole(self, pos:Vector2, r:int):
        """generate circle hole in terrain

        Args:
            pos (Vector2): position of the hole
            r (int): radious of the hole
        """
        global world

        # if already holled
        if(not self.state and not self.children): return

        # if max deph exited holl this:
        if (self.max_deph==0):
            return

        dist_x = abs(pos.x - self.rect.centerx)
        dist_y = abs(pos.y - self.rect.centery)

        # if no interraction at all
        if (dist_x-self.rect.w/2)**3 +(dist_y-self.rect.h/2)**3 > r**3:
            return

        # if fully in bounds of the rect
        if (dist_x+self.rect.width/2)**2 + (dist_y+self.rect.height/2)**2 <= r**2:
            self.set_state(False)
            self.children = list()
            return

        self.set_state(False)

        # subdivide if not already
        if not self.children:
            self.subdivide(2,state=True, max_deph=self.max_deph-1)

        # check for all children
        for child in self.children:
            child.circle_hole(pos,r)

        # if all children have the same state, remove them and set that state to self
        if all((c.state==self.children[0].state and (not c.children)) for c in self.children):
            self.state = self.children[0].state
            self.children = list()

    def terrain_form_img(self,img:np.ndarray):
        scale_f = self.rect.w/img.shape[1]
        sized = cv2.resize(img, (0,0), fx=scale_f, fy=scale_f, interpolation = cv2.INTER_LINEAR)

        ready = np.zeros((self.rect.w,self.rect.h,3),np.uint8)
        ready[self.rect.h - sized.shape[0]:self.rect.h, self.rect.w -  sized.shape[1]:self.rect.w ] = sized

        # cv2.imshow("sized",ready)
        # cv2.waitKey(0)

        self.terrain(ready)

    def terrain(self,img:np.ndarray):

        #print(f"{self.rect.y} {self.rect.x}, {self.rect.size}")
        #print(np.all(img[self.rect.y:self.rect.h-1, self.rect.x:self.rect.w-1]==[0,0,0]))
        # if not any is blank, if all are filled
        if self.max_deph==0 or not np.any(img[self.rect.y:self.rect.y + self.rect.h-1, self.rect.x:self.rect.x + self.rect.w-1]==[0,0,0]):
            return
        elif np.all(img[self.rect.y:self.rect.y + self.rect.h-1, self.rect.x:self.rect.x + self.rect.w-1]==[0,0,0]):
            self.set_state(False)
        else:
            self.set_state(False)
            self.subdivide(2,state=True, max_deph=self.max_deph-1)

            for c in self.children:
                c.terrain(img)



    def show(self, screen:pg.Surface):
        """Draw terrain to pygame surface

        Args:
            screen (Surface): pygame surface
        """

        if self.children:
            for child in self.children:
                child.show(screen)

        if self.state:
            pg.draw.rect(screen, (0,200,40), self.rect)
        #else:
        #    pg.draw.rect(screen, (0,0,0), self.rect)

        if DEBUG: pg.draw.rect(screen, (255,255,255), self.rect, 1)
        #super().show(screen)

class Gradade():
    render_radious:int=3
    vel:Vector2 = Vector2(0,0)
    color:tuple=(200,40,40)
    def __init__(self,pos:Vector2,vel:Vector2, explosion:int):
        self.explosion:int = explosion
        self.pos:Vector2 = pos
        self.acc:Vector2 = vel

    def step(self):
        self.vel = Vector2(0,1)*G_FORCE



def many(it, num):
    it = iter(it)
    return all(any(it) for _ in range(num))

def main(map_path=None):
    global world

    world = pg.display.set_mode([WIDTH, HEIGHT])
    terrain_sur = pg.Surface((WIDTH,HEIGHT))
    clock = pg.time.Clock()

    mapPoints = []
    mapBox = FillTree(Rect(0,0, WIDTH, HEIGHT),2, max_deph=12)

    if(map_path):
        mapBox.terrain_form_img(img=cv2.imread(map_path))

    explosion_r = 10


    rerender_terr=True
    while True:
        world.fill(BACKGROUND)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                mapBox.circle_hole(Vector2(pg.mouse.get_pos()), explosion_r)
                rerender_terr = True
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                mapBox.rectangle_hole(Vector2(pg.mouse.get_pos()), explosion_r)
                rerender_terr = True

        if rerender_terr:
            terrain_sur.fill(BACKGROUND)
            mapBox.show(terrain_sur)
            rerender_terr = False

        world.blit(terrain_sur,(0,0))

        pg.draw.circle(world, (255,0,255), pg.mouse.get_pos(), explosion_r,1)


        pg.display.flip()
        print(1000/clock.tick(FPS))


if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description='Process some integers.')
    # parser.add_argument('integers', metavar='N', type=int, nargs='+',
    #                     help='an integer for the accumulator')
    #parser.add_argument('--sum', dest='accumulate', action='store_const', const=sum, default=max,
    #                     help='sum the integers (default: find the max)')

    # args = parser.parse_args()

    main(map_path="./map1.png")
