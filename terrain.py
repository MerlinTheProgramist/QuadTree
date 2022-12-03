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

    update_req:bool

    def __init__(self,*args,state:bool=True, max_deph:int=10):
        super().__init__(*args)
        self.max_deph = max_deph

        self.rect_corners = [
            self.rect.bottomleft,
            self.rect.bottomright,
            self.rect.topleft,
            self.rect.topright
        ]

        self.set_state(state)

    def set_state(self, state:bool):
        self.state = state
        self.update_req = True

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
            self.children = list()
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

    def circle_hole(self, pos:Vector2, r:int,*_, screen:pg.Surface=None):
        """generate circle hole in terrain

        Args:
            pos (Vector2): position of the hole
            r (int): radious of the hole
        """
        global world


        #DEBBUGING
        if DEBUG and screen:
            pg.draw.rect(screen, (255,0,255), self.rect, width=2)

        # if already holled
        if(not self.state and not self.children): 
            return

        
        # if max deph exited holl this:
        if (self.max_deph==0):
            self.set_state(False)
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
            child.circle_hole(pos,r, screen=screen)

        # if all children have the same state, remove them and set that state to self
        if all((c.state==self.children[0].state and (not c.children)) for c in self.children):
            self.state = self.children[0].state
            #self.update_req = True
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

        if not self.update_req:
            return
            
        self.update_req=False

        if not self.children:
            if self.state:
                pg.draw.rect(screen, (0,200,40), self.rect)
                return
            else: 
                pg.draw.rect(screen, BACKGROUND, self.rect)
        else:
            for child in self.children:
                child.show(screen)

        #if DEBUG: pg.draw.rect(screen, (255,255,255), self.rect, 1)
        #super().show(screen)

class Granade():
    render_radious:int=3
    vel:Vector2 = Vector2(0,0)
    color:tuple=(200,40,40)
    def __init__(self,pos:Vector2,vel:Vector2, explosion:int, time_s:float):
        self.explosion:int = explosion
        self.pos:Vector2 = pos
        self.acc:Vector2 = vel

        self.time_s = time_s

    def step(self):
        self.vel += Vector2(0,1)*G_FORCE;
        self.pos += vel;
        
        if(collisin()):
            self.pos-=vel;
            vel=vel*-0.5;
    
    def collisin(self)->bool:
        if():
            pass         
            

def many(it, num):
    it = iter(it)
    return all(any(it) for _ in range(num))

def main(fg_path:str, *_, scale=1, bg:pg.Surface=None):
    global world
 

    world = pg.display.set_mode([WIDTH, HEIGHT])
    terrain_sur = pg.Surface((WIDTH,HEIGHT))
    clock = pg.time.Clock()
    
    # if no background passed, generate blue background
    if bg==None:
        bg = pg.Surface((WIDTH,HEIGHT)); bg.fill([20,50,200])
    fg = pg.image.load(fg_path);fg.convert()

    mapBox = FillTree(Rect(0,0, WIDTH, HEIGHT),2, max_deph=10)    
    mapBox.terrain_form_img(img= cv2.resize(cv2.imread(fg_path),(0,0), fx=scale,fy=scale) )

    explosion_r = 10

    #rerender_terr=True
    while True:
        world.blit(bg,(0,0))
        
        mapBox.show(terrain_sur)
        

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

            elif event.type == pg.MOUSEBUTTONDOWN:# and event.button == 1:
                mapBox.circle_hole(Vector2(pg.mouse.get_pos()), explosion_r, screen=terrain_sur)
                print("Granede!")
                #rerender_terr = True
            # elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            #     mapBox.rectangle_hole(Vector2(pg.mouse.get_pos()), explosion_r)
                #rerender_terr = True

        
        #rerender_terr = False
        world.fill(BACKGROUND)
        world.blit(terrain_sur,(0,0))
        #terrain_sur.fill(BACKGROUND)

        pg.draw.circle(world, (255,0,255), pg.mouse.get_pos(), explosion_r,1)


        pg.display.flip()
        print(1000/clock.tick(FPS))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Make Terrain Map')
    parser.add_argument('fg',type=str, help="path to imgae file from will generate map, where black (0,0,0) is background")
    parser.add_argument('-bg', type=str, help="path to image of background, Default is blue sky")

    args = parser.parse_args()

    main(fg_path=args.fg, scale=2)
