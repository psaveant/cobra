#------------------------------------------------------------------------------------#
# bool.py: Boolean Constraint Propagators (General Arc Consistency)                  #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

import store
from . import filter
from .filter import Logprint

__all__ = ('disjunction', 'ordering', 'Disjunction', 'clear')

def clear():
    Disjunction.instances=[]
    Guard.instances=[]
    Conjunction.instances=[]
    DisjunctionInc.instances=[]

#------------------------- Exclusive Disjunction ---------------------------#
def disjunction(c1, c2): # c1 xor c2
    d = Disjunction(c1, c2); d.link(d, 0); d.tell()
    return d

def ordering(v1, d1, v2, d2): # (v2 + d2 <= v1) or (v1 + d1 <= v2) 
    return disjunction(filter.Supxyc(v1, v2, d2), filter.Supxyc(v2, v1, d1))

class Disjunction(filter.MetaConstraint):
    instances = []
    def __init__(self, c1, c2):
        self.const = c1, c2
        self.offset = 0
        self.left = filter.UNKNOWN # stored
        self.right = filter.UNKNOWN # stored
        self.weight = self.computeWeight()
        self.proximity = self.computeProximity()
        self.active = filter.UNKNOWN # stored
        self.instances.append(self)

    def __str__(self): return "{} OR {} ({}), (l,r)=({},{})".format(self.const[0], self.const[1], "Active" if self.active == filter.TRUE else "Not active", self.left, self.right)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        if i <= self.offset:
            b = self.right
            if b != filter.UNKNOWN:
                if b == filter.FALSE:
                    self.const[0].incMin(i)
            else: self.checkLeft()
        else:
            b = self.left
            if b != filter.UNKNOWN:
                if b == filter.FALSE:
                    self.const[1].incMin(i-self.offset)
            else: self.checkRight()

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        if i <= self.offset:
            b = self.right
            if b != filter.UNKNOWN:
                if b == filter.FALSE:
                    self.const[0].decMax(i)
            else: self.checkLeft()
        else:
            b = self.left
            if b != filter.UNKNOWN:
                if b == filter.FALSE:
                    self.const[1].decMax(i-self.offset)
            else: self.checkRight()

    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        if i <= self.offset:
            b = self.right
            if b != filter.UNKNOWN:
                if b == filter.FALSE:
                    self.const[0].setVal(i)
            else: self.checkLeft()
        else:
            b = self.left
            if b != filter.UNKNOWN:
                if b == filter.FALSE:
                    self.const[1].setVal(i-self.offset)
            else: self.checkRight()

    def ask(self):
        assert(Logprint.logPrint(4, "==>ask on {!s}".format(self))==None)
        leftOK =  self.left if self.left != filter.UNKNOWN else self.const[0].ask()
        rightOK = self.right if self.right != filter.UNKNOWN else self.const[1].ask()
        if leftOK == filter.TRUE or rightOK == filter.TRUE: return filter.TRUE
        elif leftOK == filter.FALSE and rightOK == filter.FALSE: return filter.FALSE
        else: return filter.UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==>tell on {!s}".format(self))==None)
        store.assign(self, 'active', filter.TRUE)
        self.checkLeft()
        self.checkRight()

    def checkLeft(self):
        assert(Logprint.logPrint(4, "==>checkLeft on {!s}".format(self))==None)
        if self.left == filter.UNKNOWN:
            b = self.const[0].ask()
            if b != filter.UNKNOWN:
                store.assign(self, 'left', b)
                if b == filter.FALSE:
                    if self.right == filter.FALSE: raise FAIL("*** FAIL on {0} ***".format(self))
                    else:
                        store.assign(self, 'right', filter.TRUE)
                        self.const[1].tell() # Constructive disjunction
                        store.assign(self, 'active', filter.FALSE)
                else:
                    store.assign(self, 'right', filter.FALSE)
                    store.assign(self, 'active', filter.FALSE)

    def checkRight(self):
        assert(Logprint.logPrint(4, "==>checkRight on {!s}".format(self))==None)
        if self.right == filter.UNKNOWN:
            b = self.const[1].ask()
            if b != filter.UNKNOWN:
                store.assign(self, 'right', b)
                if b == filter.FALSE:
                    if self.left == filter.FALSE: raise FAIL("*** FAIL on {0} ***".format(self))
                    else:
                        store.assign(self, 'left', filter.TRUE)
                        self.const[0].tell() # Constructive disjunction
                        store.assign(self, 'active', filter.FALSE)
                else:
                    store.assign(self, 'left', filter.FALSE)
                    store.assign(self, 'active', filter.FALSE)

    def settled(self, b):
        assert(Logprint.logPrint(4, "settled: {!s} {!s}".format(self, b))==None)
        if b:
            store.assign(self, 'left', filter.TRUE) # try const1
            store.assign(self, 'right', filter.FALSE)
            store.assign(self, 'active', filter.FALSE)
            self.const[0].tell()
        else:
            store.assign(self, 'left', filter.FALSE) # try const2
            store.assign(self, 'right', filter.TRUE)
            store.assign(self, 'active', filter.FALSE)
            self.const[1].tell()

    def computeWeight(self): return self.const[0].computeWeight() + self.const[1].computeWeight()

    def computeProximity(self): return self.const[0].computeProximity() # (assumption: const[0].lv[0] == const[1].lv[1] AND const[0].lv[1] == const[1].lv[0])

Disjunction.__lt__ = lambda d1, d2 : min(d1.const[0].lv[1].inf, d1.const[1].lv[1].inf) < min(d2.const[0].lv[1].inf, d2.const[1].lv[1].inf)
