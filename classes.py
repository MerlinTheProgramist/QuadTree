from typing import List, Generic, TypeVar
from pygame import Rect, Vector2
import pygame as pg

import math as m

T = TypeVar('T',bound='TreeBranch') # TYPE OF RECIRSION
class TreeBranch(Generic[T]):
    rect:Rect
    subdivision:int

    def __init__(self:T, rect:Rect=None,h=0,w=0, subdivision:int=2):
        
        if rect==None:
            self.rect = Rect(0,0,h,w)
        else:
            self.rect = rect

        self.children:List[T] = []
        self.subdivision = subdivision

    def subdivide(self:T,n:int=2, **class_args):
        if self.children: return

        size = Vector2(m.ceil(self.rect.w / n), m.ceil(self.rect.h / n))

        for h in range(n):
            for w in range(n):
                self.children.append(
                    # create new child the same type as self
                    type(self)(
                        Rect(
                            Vector2(
                            self.rect.x+size.x*w,
                            self.rect.y+size.y*h
                            ),
                            size
                        ),
                        self.subdivision,
                        **class_args
                    )
                )


    def show(self:T, screen):
        # if self.state==1:
        #     pg.draw.rect(screen, (0,200,0), self.rect, 0)
        # else:
        #     pg.draw.rect(screen, (0,0,0), self.rect, 0)
        pg.draw.rect(screen, (255,255,255), self.rect, 1)

        # for child in self.children:
        #     child.show(screen)
