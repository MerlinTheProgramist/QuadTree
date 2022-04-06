import pygame as pg
from random import randint

from pygame import Vector2, Rect
from typing import List, Generic, TypeVar

from sys import argv
from nnfs.datasets import spiral_data
import nnfs
nnfs.init()

from classes import TreeBranch

WIDTH = 1000
HEIGHT = 1000
FPS = 60

class PointTree(TreeBranch):
    points:List[Vector2]
    max_cap:int

    def __init__(self,*args,max_cap=2):
        super().__init__(*args)
        self.points = []
        self.max_cap = max_cap
        

    def insert(self, point:Vector2)->None:
        if not self.rect.collidepoint(point):
            return

        if len(self.points) < self.max_cap:
            self.points.append(point)
            self.state = 1
            print(self.points)
        else:
            if len(self.children)==0: # if not devided
                self.subdivide(self.subdivision)

            for child in self.children:
                child.insert(point)
    
        
    def query(self,rangeRect:Rect, out:list = [])->List[Vector2]:

        # if intersects
        if self.rect.colliderect(rangeRect):
        
            # intersects
            for p in self.points:
                if rangeRect.collidepoint(p):
                    out.append(p)

            for child in self.children:
                child.query(rangeRect,out)


    def show(self, screen):
        super().show(screen)

        for p in self.points:
            pg.draw.circle(screen, (255,0,255), p, 2)

def setup(n:int):
    world = pg.display.set_mode([WIDTH, HEIGHT])
    clock = pg.time.Clock()

    boundary = PointTree(Rect(0,0, WIDTH, HEIGHT),0,n, max_cap = 2)
    
    # data = spiral_data(samples=100,classes=1)
    # print(data)
    # for p in data:
    #     print(p)
    #     boundary.insert(Vector2())
    
    
    selectPos:Vector2 = Vector2(0,0)
    selecting:bool = False
    shouting = False
    while True:
        world.fill((0,0,0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()

            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:  
                shouting = True
            elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                shouting = False
            
            # start selectBox with right button
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                selectPos.update(pg.mouse.get_pos())
                selecting = True
            elif event.type == pg.MOUSEBUTTONUP and event.button == 3:
                selecting = False

        if shouting:           
            boundary.insert(pg.mouse.get_pos())
        
        boundary.show(world)

        if selecting:
            #selection box
            pos = [min(selectPos.x,pg.mouse.get_pos()[0]),min(selectPos.y,pg.mouse.get_pos()[1])]
            size = [max(selectPos.x,pg.mouse.get_pos()[0])-pos[0],max(selectPos.y,pg.mouse.get_pos()[1])-pos[1]]
            selectBox = Rect(pos,size)
            
            pg.draw.rect(world, (255,0,255), selectBox,width=1)

            selected = []
            boundary.query(selectBox, out=selected)
            for p in selected:
                pg.draw.circle(world, (255,255,0), p, 3)

        

        

        pg.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    n = 2
    if len(argv)>=2:
        try:
            n = int(argv[1])
        except:
            print(f"using default subdivision resolution {n}") 
        print(n)
    setup(n)