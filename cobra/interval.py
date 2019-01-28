#------------------------------------------------------------------------------------#
# interval.py: Interval data structure                                               #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

import store
from . import filter
from .filter import Logprint

#------------------------------- API ------------------------------------------------#
__all__ = ('clear', 'Interval', 'startBeforeEnd', 'startBeforeStart', 'endBeforeEnd', 'endBeforeStart', 'startAtEnd', 'startAtStart', 'endAtEnd', 'endAtStart')

#------------------------------ Closing ---------------------------------------------#
def clear():
    Interval.instances=[]

#---------------- Precedence constraints over intervals -----------------------------#

def startBeforeEnd(a, b, z=filter.ZERO): # s(a) + z <= e(b) # a, b Interval
    return(filter.supxyc(b.st, a.st, z-b.sp))

def startBeforeStart(a, b, z=filter.ZERO): # s(a) + z <= s(b) # a, b Interval
    return(filter.supxyc(b.st, a.st, z))

def endBeforeEnd(a, b, z=filter.ZERO): # e(a) + z <= e(b) # a, b Interval
    return(filter.supxyc(b.st, a.st, a.sp+z-b.sp))

def endBeforeStart(a, b, z=filter.ZERO): # e(a) + z <= s(b) # a, b Interval
    return(filter.supxyc(b.st, a.st, a.sp+z))

def startAtEnd(a, b, z=filter.ZERO): # s(a) + z <= e(b) # a, b Interval
    return(filter.equxyc(b.st, a.st, z-b.sp))

def startAtStart(a, b, z=filter.ZERO): # s(a) + z <= s(b) # a, b Interval
    return(filter.equxyc(b.st, a.st, z))

def endAtEnd(a, b, z=filter.ZERO): # e(a) + z <= e(b) # a, b Interval
    return(filter.equxyc(b.st, a.st, a.sp+z-b.sp))

def endAtStart(a, b, z=filter.ZERO): # e(a) + z <= s(b) # a, b Interval
    return(filter.equxyc(b.st, a.st, a.sp+z))

#----------------------------------- Intervals --------------------------------------#

class Interval(): # Task with a variable earliest starting time and a fixed duration
    instances = []
    def __init__(self, name, est=filter.START, sp=filter.ZERO, lct=filter.HORIZON, clas=None):
        self.key = 'Int'+name
        self.st = filter.Var('ST'+name, est, lct-sp) # est (stored)
        self.sp = sp # duration
        self.clas = clas
        self.instances.append(self)

    def delete(self):
        self.instances.remove(self)

    def est(self): return self.st.inf
    def lst(self): return self.st.sup
    def ect(self): return self.st.inf+self.sp
    def lct(self): return self.st.sup+self.sp
    def duration(self): return self.sp

    def __str__(self): return self.key+":("+str(self.st)+"):"+str(self.sp)+":"+str(self.clas)
