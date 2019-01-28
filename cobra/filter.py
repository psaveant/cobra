#------------------------------------------------------------------------------------#
# filter.py: Constraint Propagators (General Arc Consistency)                        #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

import store

#------------------------------- API --------------------------------------#
__all__ = ('clear', 'ZERO', 'UN', 'DEUX', 'START', 'MINSTART', 'HORIZON', 'TRUE', 'FALSE', 'UNKNOWN', 'FAIL', 'Var', 'Constraint', 'MetaConstraint', 'UnConstraint', 'ArithmConstraint', 'supxc', 'infxc', 'equxc', 'nequxc', 'nequxyc', 'supxyc', 'infxyc', 'strictsupxyc', 'strictinfxyc', 'equxyc', 'equxyzc', 'Supxc', 'Infxc', 'Equxc', 'Nequxc', 'Nequxyc', 'Supxyc', 'Infxyc', 'Equxyc', 'Equxyzc', 'Logprint')

#---------------------------- Constants -----------------------------------#
ZERO=0
UN=1
DEUX=2

START=0
MINSTART=-1
HORIZON=1000000

FALSE, TRUE, UNKNOWN = range(3)
#------------------------------ Closing -----------------------------------#
def clear():
    for v in Var.instances:
        v.constraints=None
    Var.instances=[]

#---------------------------- Constraints -----------------------------------#

def supxc(v, cste=ZERO): # v >= cste
    c = Supxc(v, cste); c.tell(); return c

def infxc(v, cste=ZERO): # v <= cste
    c = Infxc(v, cste); c.tell(); return c

def equxc(v, cste=ZERO): # v == cste
    c = Equxc(v, cste); c.tell(); return c

def nequxc(v, cste=ZERO): # v != cste
    c = Nequxc(v, cste); c.link(); c.tell(); return c

def nequxyc(u, v, cste=ZERO): # u != v + cste
    c = Nequxyc(u, v, cste); c.link(); c.tell(); return c

def supxyc(u, v, cste=ZERO): # u >= v + cste
    c = Supxyc(u, v, cste); c.link(); c.tell(); return c

def infxyc(u, v, cste=ZERO): # u <= v + cste
    c = Infxyc(u, v, cste); c.link(); c.tell(); return c

def strictsupxyc(u, v, cste=ZERO): # u > v + cste
    return supxyc(u, v, cste + UN)

def strictinfxyc(u, v, cste=ZERO): # u < v + cste
    return supxyc(v, u, -cste + UN)

def equxyc(u, v, cste=ZERO): # u == v + cste
    c = Equxyc(u, v, cste); c.link(); c.tell(); return c

def equxyzc(u, v, w, cste=ZERO): # u + v == w + cste
    c = Equxyzc(u, v, w, cste); c.link(); c.tell(); return c

#------------------------------ Exception ---------------------------------#
class FAIL(Exception): pass

#---------------------------- Variables -----------------------------------#
class Var:
    instances = []
    def __init__(self, name, inf=START, sup=HORIZON, constraints=[]):
        assert inf <= sup
        self.name = name
        self.inf = inf # stored
        self.sup = sup # stored
        self.constraints = constraints[:]
        self.instances.append(self)

    def __str__(self): return self.name+":["+str(self.inf)+", "+str(self.sup)+"]"

    def canBeEq(self, x, z=ZERO): return self.inf + z <= x.sup and self.sup + z >= x.inf
    def isIt(self, x): return self.inf == self.sup and self.inf == x
    def canBe(self, x): return self.inf <= x and self.sup >= x
    def canNotBe(self, x): return self.inf > x or self.sup < x
    def isItMore(self, x): return self.inf >= x
    def isItLess(self, x): return self.sup <= x
    def canBeLess(self, x): return self.inf <= x
    def canNotBeLess(self, x): return self.inf > x
    def canBeMore(self, x): return self.sup >= x
    def canNotBeMore(self, x): return self.sup < x

    def isGE(self, x):
        assert(Logprint.logPrint(4, "==>{} isGE than {}".format(self, x))==None)
        if x > self.inf:
            if x > self.sup:
                raise FAIL("*** FAIL on {} is more than {} ***".format(self, x))
            else:
                store.assign(self, 'inf', x)
                if self.inf == self.sup:
                    for c in self.constraints: c[0].setVal(c[1])
                else: 
                    for c in self.constraints: c[0].incMin(c[1])

    def isLE(self, x):
        assert(Logprint.logPrint(4, "==>{} isLE than {}".format(self, x))==None)
        if x < self.sup:
            if x < self.inf:
                raise FAIL("*** FAIL on {} is less than {} ***".format(self, x))
            else:
                store.assign(self, 'sup', x)
                if self.inf == self.sup:
                    for c in self.constraints: c[0].setVal(c[1])
                else:
                    for c in self.constraints: c[0].decMax(c[1])

    def isEQ(self, x):
        assert(Logprint.logPrint(4, "==>{} is {}".format(self, x))==None)
        if self.inf > x or self.sup < x: 
            raise FAIL("*** FAIL on {} is {} ***".format(self, x))
        elif self.inf != self.sup:
            store.assign(self, 'inf', x)
            store.assign(self, 'sup', x)
            for c in self.constraints: c[0].setVal(c[1])

    def isNEQ(self, x):
        assert(Logprint.logPrint(4, "==>{} is {}".format(self, x))==None)
        if self.inf == x:
            self.isGE(x + UN)
        elif self.sup == x:
            self.isLE(x - UN)

#----------------------------- Constraints --------------------------------#
class Constraint: pass

class MetaConstraint(Constraint):

    def link(self, c, i):
        j = i
        if issubclass(type(c), ArithmConstraint):
            for v in c.lv:
                j += 1
                v.constraints.append((self, j))
        elif issubclass(type(c), UnConstraint):
            j += 1
            c.v.constraints.append((self, j))
        else: # Metaconstraint
            j = self.link(c.const[0], j)
            c.offset = j - i
            j = self.link(c.const[1], j)
        return j

class UnConstraint(Constraint):
    def __init__(self, v, c=ZERO):
        self.v = v
        self.c = c

    def computeWeight(self): return abs(self.c)
    def computeProximity(self): return abs(self.c)


class ArithmConstraint(Constraint):
    def __init__(self, *lv, c=ZERO, d=ZERO):
        self.lv = lv
        self.c = c
        self.d = d

    def link(self):
        for i in range(len(self.lv)): self.lv[i].constraints.append((self, i+1))

    def computeWeight(self): return abs(self.c)
    def computeProximity(self): return abs(self.c)

#----------------------- V >= c ---------------------------------------#
class Supxc(UnConstraint):
    def __init__(self, v, c=ZERO):
        UnConstraint.__init__(self, v, c=c)

    def __str__(self): return "{} >= {}".format(self.v.name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        self.v.isGE(self.c)

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        self.v.isGE(self.c)

    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        self.v.isGE(self.c)

    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.v.inf >= self.c: return TRUE
        elif self.v.canNotBeMore(self.c): return FALSE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        self.v.isGE(self.c)

#----------------------- V <= c ---------------------------------------#
class Infxc(UnConstraint):
    def __init__(self, v, c=ZERO):
        UnConstraint.__init__(self, v, c=c)

    def __str__(self): return "{} <= {}".format(self.v.name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        self.v.isLE(self.c)

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        self.v.isLE(self.c)

    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        self.v.isLE(self.c)

    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.v.sup <= self.c: return TRUE
        elif self.v.canNotBeLess(self.c): return FALSE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        self.v.isLE(self.c)

#----------------------- V == c ---------------------------------------#
class Equxc(UnConstraint):
    def __init__(self, v, c=ZERO):
        UnConstraint.__init__(self, v, c=c)

    def __str__(self): return "{} == {}".format(self.v.name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        self.v.isEQ(self.c)

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        self.v.isEQ(self.c)

    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        self.v.isEQ(self.c)

    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.v.isIt(self.c): return TRUE
        elif self.v.canNotBe(self.c): return FALSE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        self.v.isEQ(self.c)
#----------------------- V != c ---------------------------------------#

class Nequxc(UnConstraint):
    def __init__(self, v, c=ZERO):
        UnConstraint.__init__(self, v, c=c)

    def link(self):
        self.v.constraints.append((self, 1))

    def __str__(self): return "{} != {}".format(self.v.name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        if self.v.canBeLess(self.c): self.v.isNEQ(self.c)

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        if self.v.canBeMore(self.c): self.v.isNEQ(self.c)

    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        if self.v.inf == self.c: raise FAIL("*** FAIL on {} ***".format(self))

    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.v.isIt(self.c): return FALSE
        elif self.v.canNotBe(self.c): return TRUE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        if self.v.canBe(self.c): self.v.isNEQ(self.c)

#----------------------- U != V + c ---------------------------------------#
class Nequxyc(ArithmConstraint):
    def __init__(self, u, v, c=ZERO):
        ArithmConstraint.__init__(self, u, v, c=c)

    def __str__(self): return "{0} != {1} + {2}".format(self.lv[0].name, self.lv[1].name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        if self.lv[0].inf == self.lv[0].sup: self.lv[1].isNEQ(self.lv[0].inf - self.c)
        elif self.lv[1].inf == self.lv[1].sup: self.lv[0].isNEQ(self.lv[1].inf + self.c)

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        if self.lv[0].inf == self.lv[0].sup: self.lv[1].isNEQ(self.lv[0].inf - self.c)
        elif self.lv[1].inf == self.lv[1].sup: self.lv[0].isNEQ(self.lv[1].inf + self.c)

    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        if i==1: self.lv[1].isNEQ(self.lv[0].inf - self.c)
        else: self.lv[0].isNEQ(self.lv[1].inf + self.c)

    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.lv[0].sup < self.lv[1].inf + self.c or self.lv[1].sup < self.lv[0].inf - self.c: return TRUE
        elif self.lv[0].inf == self.lv[0].sup and self.lv[1].inf == self.lv[1].sup and self.lv[0].inf == self.lv[1].inf + self.c: return FALSE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        if self.lv[0].inf == self.lv[0].sup: self.lv[1].isNEQ(self.lv[0].inf - self.c)
        elif self.lv[1].inf == self.lv[1].sup: self.lv[0].isNEQ(self.lv[1].inf + self.c)

#----------------------- U >= V + c ---------------------------------------#
class Supxyc(ArithmConstraint):
    def __init__(self, u, v, c=ZERO):
        ArithmConstraint.__init__(self, u, v, c=c)

    def __str__(self): return "{0} >= {1} + {2}".format(self.lv[0].name, self.lv[1].name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        if i==2: self.lv[0].isGE(self.lv[1].inf + self.c)

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        if i==1: self.lv[1].isLE(self.lv[0].sup - self.c)

    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        self.lv[1].isLE(self.lv[0].inf - self.c) if i==1 else self.lv[0].isGE(self.lv[1].inf + self.c)

    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.lv[0].sup < self.lv[1].inf + self.c: return FALSE
        elif self.lv[0].inf >= self.lv[1].sup + self.c: return TRUE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        self.lv[0].isGE(self.lv[1].inf + self.c)
        self.lv[1].isLE(self.lv[0].sup - self.c)

    def computeProximity(self):
        return abs(self.lv[0].inf - self.lv[1].inf)

#----------------------- U <= V + c ---------------------------------------#
class Infxyc(ArithmConstraint):
    def __init__(self, u, v, c=ZERO):
        ArithmConstraint.__init__(self, u, v, c=c)

    def __str__(self): return "{0} <= {1} + {2}".format(self.lv[0].name, self.lv[1].name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        if i==1: self.lv[1].isGE(self.lv[0].inf - self.c)

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        if i==2: self.lv[0].isLE(self.lv[1].sup + self.c)


    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        self.lv[1].isGE(self.lv[0].inf - self.c) if i==1 else self.lv[0].isLE(self.lv[1].sup + self.c)


    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.lv[1].inf >= self.lv[0].sup + self.c: return TRUE
        elif self.lv[1].sup < self.lv[0].inf + self.c : return FALSE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        self.lv[0].isLE(self.lv[1].sup + self.c)
        self.lv[1].isGE(self.lv[0].inf - self.c)

#----------------------- U == V + c ---------------------------------------#
class Equxyc(ArithmConstraint):
    def __init__(self, u, v, c=ZERO):
        ArithmConstraint.__init__(self, u, v, c=c)

    def __str__(self): return "{0} == {1} + {2}".format(self.lv[0].name, self.lv[1].name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        self.lv[1].isGE(self.lv[0].inf - self.c) if i==1 else self.lv[0].isGE(self.lv[1].inf + self.c)

    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        self.lv[1].isLE(self.lv[0].sup - self.c) if i==1 else self.lv[0].isLE(self.lv[1].sup + self.c)

    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        self.lv[1].isEQ(self.lv[0].inf - self.c) if i==1 else self.lv[0].isEQ(self.lv[1].inf + self.c)

    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.lv[0].sup < self.lv[1].inf + self.c or self.lv[0].inf > self.lv[1].sup + self.c: return FALSE
        elif self.lv[0].inf == self.lv[0].sup and self.lv[1].inf == self.lv[1].sup and self.lv[0].inf == self.lv[1].inf + self.c: return TRUE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        self.incMin(1)
        self.decMax(1)
        self.incMin(2)
        self.decMax(2)

    def computeProximity(self):
        return abs(self.lv[0].inf - self.lv[1].inf)

#----------------------- U + V == W + c ---------------------------------------#
class Equxyzc(ArithmConstraint):
    def __init__(self, u, v, w, c=ZERO):
        ArithmConstraint.__init__(self, u, v, w, c=c)

    def __str__(self): return "{} + {} == {} + {}".format(self.lv[0].name, self.lv[1].name, self.lv[2].name, self.c)

    def incMin(self, i):
        assert(Logprint.logPrint(4, "==>incMin on {!s} {!s}".format(self, i))==None)
        if i == 1:
            self.lv[2].isGE(self.lv[0].inf + self.lv[1].inf - self.c)
            self.lv[1].isLE(self.lv[2].sup + self.c - self.lv[0].inf)
        elif i == 2:
            self.lv[2].isGE(self.lv[1].inf + self.lv[0].inf - self.c)
            self.lv[0].isLE(self.lv[2].sup + self.c - self.lv[1].inf)
        else:
            self.lv[0].isGE(self.lv[2].inf + self.c - self.lv[1].sup)
            self.lv[1].isGE(self.lv[2].inf + self.c - self.lv[0].sup)
    
    def decMax(self, i):
        assert(Logprint.logPrint(4, "==>decMax on {!s} {!s}".format(self, i))==None)
        if i == 1:
            self.lv[2].isLE(self.lv[0].sup + self.lv[1].sup - self.c)
            self.lv[1].isGE(self.lv[2].inf + self.c - self.lv[0].sup)
        elif i == 2:
            self.lv[2].isLE(self.lv[1].sup + self.lv[0].sup - self.c)
            self.lv[0].isGE(self.lv[2].inf + self.c - self.lv[1].sup)
        else:
            self.lv[0].isLE(self.lv[2].sup + self.c - self.lv[1].inf)
            self.lv[1].isLE(self.lv[2].sup + self.c - self.lv[0].inf)
 
    def setVal(self, i):
        assert(Logprint.logPrint(4, "==>setVal on {!s} {!s}".format(self, i))==None)
        if i == 1:
            self.lv[1].isGE(self.lv[2].inf + self.c - self.lv[0].inf)
            self.lv[1].isLE(self.lv[2].sup + self.c - self.lv[0].inf)
            self.lv[2].isGE(self.lv[0].inf + self.lv[1].inf - self.c) 
            self.lv[2].isLE(self.lv[0].inf + self.lv[1].sup - self.c)
        elif i == 2:
            self.lv[0].isGE(self.lv[2].inf + self.c - self.lv[1].inf)
            self.lv[0].isLE(self.lv[2].sup + self.c - self.lv[1].inf)
            self.lv[2].isGE(self.lv[1].inf + self.lv[0].inf - self.c) 
            self.lv[2].isLE(self.lv[1].inf + self.lv[0].sup - self.c)
        else:
            self.lv[0].isGE(self.lv[2].inf + self.c - self.lv[1].sup)
            self.lv[0].isLE(self.lv[2].inf + self.c - self.lv[1].inf)
            self.lv[1].isGE(self.lv[2].inf + self.c - self.lv[0].sup) 
            self.lv[1].isLE(self.lv[2].inf + self.c - self.lv[0].inf)

    def ask(self):
        assert(Logprint.logPrint(4, "==>ASK on {!s}".format(self))==None)
        if self.lv[2].sup + self.c < self.lv[0].inf + self.lv[1].inf or self.lv[2].inf + self.c > self.lv[0].sup + self.lv[1].sup: return FALSE
        elif self.lv[0].inf == self.lv[0].sup and self.lv[1].inf == self.lv[1].sup and self.lv[2].inf == self.lv[2].sup and self.lv[2].inf + self.c == self.lv[0].inf + self.lv[1].inf: return TRUE
        else: return UNKNOWN

    def tell(self):
        assert(Logprint.logPrint(4, "==> TELL on {!s}".format(self))==None)
        self.lv[0].isGE(self.lv[2].inf + self.c - self.lv[1].sup)
        self.lv[0].isLE(self.lv[2].sup + self.c - self.lv[1].inf)
        self.lv[1].isGE(self.lv[2].inf + self.c - self.lv[0].sup)
        self.lv[1].isLE(self.lv[2].sup + self.c - self.lv[0].inf)
        self.lv[2].isGE(self.lv[1].inf + self.lv[0].inf - self.c) 
        self.lv[2].isLE(self.lv[1].sup + self.lv[0].sup - self.c)

class Logprint:
    logPrint = lambda *a, **k: None

    def __init__(self, verbose=0):
        if verbose > 0: Logprint.logPrint = lambda *a, **k: print(a[1], **k) if a[0] <= verbose else None
        else: Logprint.logPrint = lambda *a, **k: None



