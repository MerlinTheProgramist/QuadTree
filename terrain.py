import pygame as pg
from random import randint

from pygame import Vector2, Rect
from typing import List, Generic, TypeVar, Callable
from classes import TreeBranch

DEBUG = True

WIDTH = 1000
HEIGHT = 1000
FPS = 60
world = None

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

        self.rect_corners = [self.rect] 

    def set_state(self, state:bool):
        self.state = state

        if not state:
            self.children = list()
            return

    def rectangle_hole(self, pos:Vector2, r:int):
        # if already holled
        if(not self.state): return
        
        c_dist_x = abs(pos.x - self.rect.x - self.rect.width/2);
        c_dist_y = abs(pos.y - self.rect.y - self.rect.height/2);

        # if no interraction at all
        if c_dist_x > r+self.rect.width/2 or c_dist_y > r+self.rect.height/2:
            return
        

        # if  fully in bounds of the circle
        if c_dist_x+self.rect.width/2 <= r and c_dist_y+self.rect.height/2 <= r:
            self.set_state(False)
            return

        # if max deph exited holl this:
        if (self.max_deph==0):
            self.set_state(False)
            return
        
        if not self.children:
            # if self not the right resolution
            self.subdivide(2,state=True, max_deph=self.max_deph-1)

        # check for all children
        for child in self.children:
            child.rectangle_hole(pos,r)

    def circle_hole(self, pos:Vector2, r:int):
        global world
        """create circular hole in terrain

        Args:
            pos (Vector2): position of the hole
            r (int): radious of the hole
        """

        # if already holled
        if(not (self.state or self.children)): return
        
        dist_x = abs(pos.x - (self.rect.x + self.rect.width/2))
        dist_y = abs(pos.y - (self.rect.y + self.rect.height/2))
        
        # if fully inside
        if (dist_x+self.rect.w/2)**2+(dist_y+self.rect.h/2)**2 < r**2:
            self.set_state(False)
            print("inside")
            #pg.draw.rect(world, (0,0,0), self.rect)
            #pg.display.flip()
            #pg.time.delay(5)
            return

        # if outside but not domain of
        elif ((dist_x-self.rect.w/2)**2+(dist_y-self.rect.h/2)**2 > r**2 and 
            not (
                (dist_x+r<self.rect.w/2) or 
                (dist_y+r<self.rect.h/2))
            ):
                print("outside")
                #pg.draw.rect(world, (0,200,40), self.rect)
                #pg.display.flip()
                #pg.time.delay(5)
                return
            
            
        print("sub")

        # if max deph exited holl this:
        if (self.max_deph==0):
            self.set_state(False)
            return
        
        # subdivide if not already
        if not self.children:
            self.subdivide(2,state=True, max_deph=self.max_deph-1)

        # check for all children
        for child in self.children:
            child.circle_hole(pos,r)

    def circle_hole_better(self, pos:Vector2, r:int)->bool:
        global world

        # if already holled
        if(not (self.state or self.children)): return
        
        dist_x = abs(pos.x - (self.rect.x + self.rect.width/2))
        dist_y = abs(pos.y - (self.rect.y + self.rect.height/2))
        
        # if fully inside
        if self.rect.width and (dist_x)**2+(dist_y)**2 < r**2:
            self.set_state(False)
            print("inside")
            #pg.draw.rect(world, (0,0,0), self.rect)
            #pg.display.flip()
            #pg.time.delay(5)
            return False

        # if outside but not domain of
        elif ((dist_x-self.rect.w/2)**2+(dist_y-self.rect.h/2)**2 > r**2 and 
            not (
                (dist_x+r<=self.rect.w/2) or 
                (dist_y+r<=self.rect.h/2))
            ):
                print("outside")
                #pg.draw.rect(world, (0,200,40), self.rect)
                #pg.display.flip()
                #pg.time.delay(5)
                return True
            
            
        print("sub")

        # if max deph exited holl this:
        if (self.max_deph==0):
            self.set_state(False)
            return False
        
        # subdivide if not already
        if not self.children:
            self.subdivide(2,state=True, max_deph=self.max_deph-1)

        # check for all children
        for child in self.children:
            self.state &= bool(child.circle_hole(pos,r))

        return self.state


    def show(self, screen:pg.Surface):
        """Draw terrain to pygame surface

        Args:
            screen (Surface): pygame surface
        """

        if self.children:
            for child in self.children:
                child.show(screen)
        else:
            if self.state:
                pg.draw.rect(screen, (0,200,40), self.rect)
            else:
                pg.draw.rect(screen, (0,0,0), self.rect)
            
            if DEBUG: pg.draw.rect(screen, (255,255,255), self.rect, 1)


        #super().show(screen)

def circle_explode(mapTiles:FillTree, pos:Vector2, r:int)->FillTree:
    mapTiles.recursiveHole(pos,r)

def many(it, num):
    it = iter(it)
    return all(any(it) for _ in range(num))

def main():
    global world

    world = pg.display.set_mode([WIDTH, HEIGHT])
    clock = pg.time.Clock()

    mapPoints = []
    mapBox = FillTree(Rect(0,0, WIDTH, HEIGHT),2, max_deph=8)
    
    explosion_r = 100

    while True:
        world.fill((0,0,0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  
                #mapPoints.append(Vector2(pg.mouse.get_pos()))
                mapBox.circle_hole(Vector2(pg.mouse.get_pos()), explosion_r)
                #mapBox.circle_hole_better(Vector2(pg.mouse.get_pos()), explosion_r)
                print("_________")
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                mapBox.rectangle_hole(Vector2(pg.mouse.get_pos()), explosion_r)
        
        mapBox.show(world)
        pg.draw.circle(world, (255,0,255), pg.mouse.get_pos(), explosion_r,1)


        pg.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    main()