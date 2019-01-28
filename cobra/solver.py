#------------------------------------------------------------------------------------#
# solver.py: Tree Search Branch and bound                                            #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

from time import perf_counter, process_time
from collections import namedtuple
import store
from . import filter
from . import interval
from . import bool
from .filter import Logprint

#------------------------------------------------------------------------------------#
# Tree search is viewed as a recursive process, where the search space is            #
# iteratively decomposed by opening choice points and posting constraints            #
# on each branch.                                                                    #
#------------------------------------------------------------------------------------#

#-------------------------- API -----------------------------------------------------
__all__ = ('Optimizer', 'Solution', 'showVar', 'validate')

def showVar(d):
    for v in d.items(): Logprint.logPrint(2,"{}={}".format(v[0], v[1]))

def validate(vars, sol): # vars is a list, sol is a dicho
    store.push()
    try:
        for v in vars: v.isEQ(sol[v.name])
    except filter.FAIL as e: 
        Logprint.logPrint(2, e)
        Logprint.logPrint(1,"The solution is not valid:")
        showVar(sol)
        store.back()
        return False
    Logprint.logPrint(1,"The solution is valid")
    store.back()
    return True

Solution = namedtuple('Solution', ['vars', 'objname', 'objvalue', 'backtracks', 'proof', 'duration', 'completion', 'nsol'])

#------------------------------- Optimizer ------------------------------------
#  VERBOSE=0: Quiet
#  VERBOSE=2: Branching in action
#  VERBOSE=4: Look-Ahead in action
#  VERBOSE=5: Trailing in Action

#--- Heuristics -------------
#-- Static disjunction ordering -------- RAJOUTER smallest proximity
#   - no reordering (0)
#   - reverse declaration order (1)
#   - earliest time order (2)
#   - latest time order (3)

#-- Dynamic disjunction ordering --------
#   -No dynamic disjunction choice (0)
#   -Heaviest weight disjunction first (1)
#   -Largest proximity disjunction first (2)
#   -Heaviest weight first and then earliest time disjunction (3)
#   -Latest time first  =  Maximum of Minimum Earliest Starting Time (4)
#   -Smallest Proximity of Maximum of Minimum Earliest Starting Time (5) = robust (4) independent of static ordering.

#-- Disjunction side
#   -No disjunction side preferred (0)
#   -Heaviest weight disjunction side first (1)
#   -Lowest weight disjunction side first (2)
#   -Latest starting time disjunction side first (3)
#   -Earliest starting time disjunction side first (4)
#   -Latest ending time disjunction side first (5)
#   -Earliest ending time disjunction side first (6)

def mins(l, key=None, default=False):
    smallest = min(l, key=key, default=default)
    return [x for x in l if key(x)==key(smallest)]

def maxs(l, key=None, default=False):
    biggest = max(l, key=key, default=default)
    return [x for x in l if key(x)==key(biggest)]

class Optimizer:
    OBJECTIVE=None
    VARIABLES = []
    ACTIVITIES = []
    DISJUNCTIONS = []
    NONOVERLAP = []
    NONOVERLAP2 = []
    NONOVERLAP3 = []
    CUMULATIVE = []
    currentSolution = {}
    InitialBound=None
    Bound=None
    NBsol=0
    NBopt=0 # Number of optimal solutions
    NBbk=0 # Number of attempts
    NBbkTot=0
    ROOT=True
    MINI=True
    ALLSOL=False
    DISJSTATIC=2
    DISJCHOICE=1
    DISJSIDE=0
    SEARCH=0
    VARCHOICE=0

# search=0 : Disjunctive Search
# search=1 : SetTimes Search (Asap)
# search=2 : Enumerate on variables
# search=3 : Dichotomic search

    def __init__(self, objective=None, search=0, mini=True, bound=None, incBound=None, root=True, disjStatic=2, disjChoice=1, disjSide=0, varChoice=0):
        self.OBJECTIVE=objective
        self.SEARCH=search
        self.VARIABLES=filter.Var.instances
        if interval != None:self.ACTIVITIES=interval.Interval.instances
        if bool != None: self.DISJUNCTIONS=bool.Disjunction.instances
        Logprint.logPrint(2, "#disjunctions = {}".format(len(self.DISJUNCTIONS)))
        self.MINI=mini
        self.ROOT=root
        self.DISJSTATIC=disjStatic
        self.DISJCHOICE=disjChoice
        self.DISJSIDE=disjSide
        self.VARCHOICE=varChoice

        if not objective: # Decision problem
            self.enforceBound = lambda: None
            self.enforceBB = lambda: None
            self.newBound = lambda: None
            self.ALLSOL = False
            if root: # Means here only one solution
                self.ALLSOL = False
            else:
                self.ALLSOL = True
        else:
            if mini: # Minimizing
                if bound: self.InitialBound = min(bound, self.OBJECTIVE.sup)
                else: self.InitialBound = self.OBJECTIVE.sup
                if incBound: self.incBound = incBound
                else: self.incBound = filter.UN
                self.enforceBound = lambda: self.OBJECTIVE.isLE(self.Bound)
                self.newBound = lambda: min(self.Bound, self.OBJECTIVE.inf) - self.incBound
            else: # Maximizing
                if bound: self.InitialBound = max(bound, self.OBJECTIVE.inf)
                else: self.InitialBound = self.OBJECTIVE.inf
                if incBound: self.incBound = incBound
                else: self.incBound = -filter.UN
                self.enforceBound = lambda: self.OBJECTIVE.isGE(self.Bound)
                self.newBound = lambda: max(self.Bound, self.OBJECTIVE.sup) + self.incBound
            if root: # Restart from root
                self.ALLSOL = False
                self.enforceBB = lambda: None
            else: # Chronological Backtracking
                self.ALLSOL = True
                self.enforceBB = lambda: self.enforceBound()

        if disjChoice==0: # implementation order
            self.nextDisjunction = lambda: next((d for d in self.DISJUNCTIONS if d.active == filter.TRUE and (d.left == filter.UNKNOWN or d.right == filter.UNKNOWN)), False)
        elif disjChoice==1: # heaviest weight first
            self.nextDisjunction = lambda: max((d for d in self.DISJUNCTIONS if d.active == filter.TRUE and (d.left == filter.UNKNOWN or d.right == filter.UNKNOWN)), key=lambda x: x.weight, default=False)
        elif disjChoice==2: # largest proximity first
            self.nextDisjunction = lambda: max((d for d in self.DISJUNCTIONS if d.active == filter.TRUE and (d.left == filter.UNKNOWN or d.right == filter.UNKNOWN)), key=lambda x: x.proximity, default=False)
        elif disjChoice==3: # heaviest weight first and then earliest time
            self.nextDisjunction = lambda: min((d for d in maxs([d for d in self.DISJUNCTIONS if d.active == filter.TRUE and (d.left == filter.UNKNOWN or d.right == filter.UNKNOWN)], key=lambda x: x.weight, default=False)), key=lambda d: min(d.const[0].lv[1].inf, d.const[1].lv[1].inf), default=False)
        elif disjChoice==4: # latest time first = Maximum of Minimum Earliest Starting Time
            self.nextDisjunction = lambda: max((d for d in self.DISJUNCTIONS if d.active == filter.TRUE and (d.left == filter.UNKNOWN or d.right == filter.UNKNOWN)), key=lambda d: min(d.const[0].lv[1].inf, d.const[1].lv[1].inf), default=False)
        elif disjChoice==5: # Smallest Proximity of Maximum of Minimum Earliest Starting Time
            self.nextDisjunction = lambda: minProxMaxMinEST(self.DISJUNCTIONS)

        if disjSide==0: # declaration side
            self.leftFirst = lambda d: True
        elif disjSide==1: # highest weight first
            self.leftFirst = lambda d: d.const[0].computeWeight() >= d.const[1].computeWeight()
        elif disjSide==2: # lowest weight first
            self.leftFirst = lambda d: d.const[1].computeWeight() >= d.const[0].computeWeight()
        elif disjSide==3: # latest starting first
            self.leftFirst = lambda d: d.const[0].lv[1].inf >= d.const[1].lv[1].inf
        elif disjSide==4: # earliest starting first
            self.leftFirst = lambda d: d.const[0].lv[1].inf <= d.const[1].lv[1].inf
        elif disjSide==5: # latest ending first
            self.leftFirst = lambda d: d.const[0].lv[1].inf + d.const[0].computeWeight() >= d.const[1].lv[1].inf + d.const[1].computeWeight()
        elif disjSide==6: # earliest ending first
            self.leftFirst = lambda d: d.const[0].lv[1].inf + d.const[0].computeWeight() <= d.const[1].lv[1].inf + d.const[1].computeWeight()

        if varChoice==0: # implementation order
            self.nextVar = lambda: next((v for v in self.VARIABLES if v.inf != v.sup), False)
        elif varChoice==1: # minimum domain first
            self.nextVar = lambda: min((v for v in self.VARIABLES if v.inf != v.sup), key=lambda x: x.sup - x.inf, default=False)

    def saveSolution(self):
        for v in self.VARIABLES:
            self.currentSolution[v.name] = v.inf

    def nbSol(self): return self.NBsol

    def disjunctions(self): return "Current Disjunctions={}".format(self.DISJUNCTIONS)
    def showDisj(self):
        for d in self.DISJUNCTIONS: print("{!s}({!s},{!s})".format(d, d.left, d.right))

    def variables(self): return "Current Variables={}".format(self.VARIABLES)

    def optimize(self, timeout=None):
        user_start = process_time()
        self.NBsol = self.NBopt = self.NBbk = self.NBbkTot = 0
        self.currentSolution.clear()
        if self.OBJECTIVE:
            self.Bound = self.InitialBound
            if self.DISJSTATIC==0: # no reordering
                pass
            elif self.DISJSTATIC==1: # reverse declaration order
                self.DISJUNCTIONS.reverse()
            elif self.DISJSTATIC==2: # earliest time order
                self.DISJUNCTIONS=sorted(self.DISJUNCTIONS, key=lambda d: min(d.const[0].lv[1].inf, d.const[1].lv[1].inf), reverse=False)
            elif self.DISJSTATIC==3: # latest time order
                self.DISJUNCTIONS=sorted(self.DISJUNCTIONS, key=lambda d: min(d.const[0].lv[1].inf, d.const[1].lv[1].inf), reverse=True)
            elif self.DISJSTATIC==4: # smallest proximity
                self.DISJUNCTIONS=sorted(self.DISJUNCTIONS, key=lambda d: d.proximity)
            Logprint.logPrint(2, "-{} {} with initial bound at {} and increment at {}".format("Minimizing" if self.MINI else "Maximizing", self.OBJECTIVE.name, self.Bound, self.incBound))
            Logprint.logPrint(2, "-Restarting from root" if self.ROOT else "-Chronological backtracking")

        if self.SEARCH == 0: # Disjunctive Search
            Logprint.logPrint(2, "-Disjunctive Search")
            if self.DISJSTATIC==0: Logprint.logPrint(2, "   -No static disjunction reordering")
            elif self.DISJSTATIC==1: Logprint.logPrint(2, "   -Static disjunction reverse declaration order")
            elif self.DISJSTATIC==2: Logprint.logPrint(2, "   -Static disjunction earliest time order")
            elif self.DISJSTATIC==3: Logprint.logPrint(2, "   -Static disjunction latest time order")
            elif self.DISJSTATIC==4: Logprint.logPrint(2, "   -Static disjunction smallest proximity")

            if self.DISJCHOICE==0: Logprint.logPrint(2, "   -No dynamic disjunction choice")
            elif self.DISJCHOICE==1: Logprint.logPrint(2, "   -Heaviest weight disjunction first")
            elif self.DISJCHOICE==2: Logprint.logPrint(2, "   -Largest proximity disjunction first")
            elif self.DISJCHOICE==3: Logprint.logPrint(2, "   -heaviest weight first and then earliest time disjunction")
            elif self.DISJCHOICE==4: Logprint.logPrint(2, "   -latest time first (maximum of minimum Earliest Starting Time)")
            elif self.DISJCHOICE==5: Logprint.logPrint(2, "   -smallest proximity of maximum of minimum Earliest Starting Time")

            if self.DISJSIDE==0: Logprint.logPrint(2, "   -No disjunction side preferred")
            elif self.DISJSIDE==1: Logprint.logPrint(2, "   -Heaviest weight disjunction side first")
            elif self.DISJSIDE==2: Logprint.logPrint(2, "   -Lowest weight disjunction side first")
            elif self.DISJSIDE==3: Logprint.logPrint(2, "   -Latest starting time disjunction side first")
            elif self.DISJSIDE==4: Logprint.logPrint(2, "   -Earliest starting time disjunction side first")
            elif self.DISJSIDE==5: Logprint.logPrint(2, "   -Latest ending time disjunction side first")
            elif self.DISJSIDE==6: Logprint.logPrint(2, "   -Earliest ending time disjunction side first")
        elif self.SEARCH == 1:
            pass
        elif self.SEARCH == 2 or self.SEARCH == 3:
            if self.SEARCH == 2: # -Enumeration on variables
                Logprint.logPrint(2, "-Enumeration on variables")
            else: # self.SEARCH == 3: # -Dichotomic search
                Logprint.logPrint(2, "-Dichotomic search")
            if self.VARCHOICE==0: Logprint.logPrint(2, "   -no variable order")
            elif self.VARCHOICE==1: Logprint.logPrint(2, "   -minimum domain first variable order")
        else:
            pass
        try:
            w = store.current() # In case of interruption
            completion = self.solve()
            store.backtrack(w) # In case of interruption
        except KeyboardInterrupt: 
            store.backtrack(w) # In case of interruption
            completion = False
        self.NBbkTot += self.NBbk
        user_end = process_time() # perf_counter()
        if self.OBJECTIVE: Logprint.logPrint(2, "======****===== Optimization {} ({}), {} in {} backtracks ({} for proof) and {}".format("completed" if completion else "interrupted", self.NBopt, "{}".format("{}({})={}".format("min" if self.MINI else "max", self.OBJECTIVE.name, self.currentSolution.get(self.OBJECTIVE.name)) if self.currentSolution else "no solution found") if self.OBJECTIVE else "" if self.currentSolution else "no solution found", self.NBbkTot, self.NBbk if completion else 0, durationPrettyPrint(user_start, user_end)))
        return Solution(self.currentSolution,
                        self.OBJECTIVE.name if self.OBJECTIVE else None,
                        self.currentSolution.get(self.OBJECTIVE.name) if self.OBJECTIVE else None,
                        self.NBbkTot,
                        self.NBbk if completion else 0,
                        durationPrettyPrint(user_start, user_end),
                        completion,
                        self.NBsol)

    def solve(self):
        store.push()
        try:
            while True:
                assert(Logprint.logPrint(2, "======****====> Looking for a solution {}".format("at {}={}".format(self.OBJECTIVE.name, self.Bound) if self.OBJECTIVE else ""))==None)
                self.enforceBound()
                if self.SEARCH == 0: self.search()
                elif self.SEARCH == 1: pass
                elif self.SEARCH == 2: self.enumerate()
                elif self.SEARCH == 3: self.dicho()
                else: pass
                if not self.OBJECTIVE: raise filter.FAIL
        except filter.FAIL: pass
        store.back()
        if self.OBJECTIVE: Logprint.logPrint(2, "<=====****===== Optimum proved in {} backtracks".format(self.NBbk))
        return True

    def enumerate(self): # Branch and Bound on variables. Depth-first search. With exception.
        x = self.nextVar()
        if x:
            v = x.inf
            store.push()
            try:
                assert(Logprint.logPrint(2, "==> Try {} = {}".format(x.name, v))==None)
                x.isEQ(v)
                self.enumerate()
            except filter.FAIL:
                store.back()
                self.NBbk +=1
                x.isGE(v+filter.UN)
                self.enforceBB()
                self.enumerate()
            else:
                store.back()
        else:
            self.NBsol += 1
            assert(Logprint.logPrint(2, "<=====****===== Found solution n°{} in {} backtracks{}".format(self.NBsol, self.NBbk, " at {}={}".format(self.OBJECTIVE.name, self.OBJECTIVE.inf if self.MINI else self.OBJECTIVE.sup) if self.OBJECTIVE else ""))==None)
            self.saveSolution()
            self.Bound = self.newBound()
            self.NBbkTot += self.NBbk; self.NBbk = 0
            if self.ALLSOL: raise filter.FAIL

    def dicho(self): # Branch and Bound on variables. Dichotomic search. With exception.
        x = self.nextVar()
        if x:
            mid = (x.inf+x.sup)//filter.DEUX
            store.push()
            try:
                assert(Logprint.logPrint(2, "==> Try {} <= {}".format(x.name, mid))==None)
                x.isLE(mid)
                self.dicho()
            except filter.FAIL:
                store.back()
                self.NBbk +=1
                self.enforceBB()
                store.push()
                try: 
                    assert(Logprint.logPrint(2, "==> Try {} > {}".format(x.name, mid))==None)
                    x.isGE(mid+filter.UN)
                    self.dicho()
                except filter.FAIL:
                    store.back()
                    self.NBbk +=1
                    raise filter.FAIL
                else: store.back()
            else: store.back()
        else:
            self.NBsol += 1
            assert(Logprint.logPrint(2, "<=====****===== Found solution n°{} in {} backtracks{}".format(self.NBsol, self.NBbk, " at {}={}".format(self.OBJECTIVE.name, self.OBJECTIVE.inf if self.MINI else self.OBJECTIVE.sup) if self.OBJECTIVE else ""))==None)
            self.saveSolution()
            self.Bound = self.newBound()
            self.NBbkTot += self.NBbk; self.NBbk = 0
            if self.ALLSOL: raise filter.FAIL

    def search(self): # Branch and Bound on disjunctions with exception.
        d=self.nextDisjunction()
        if d:
            left=self.leftFirst(d)
            store.push()
            try: 
                d.settled(left)
                self.search()
            except filter.FAIL:
                store.back()
                self.NBbk +=1
                self.enforceBB()
                store.push()
                try: 
                    d.settled(not(left))
                    self.search()
                except filter.FAIL:
                    store.back()
                    self.NBbk +=1
                    raise filter.FAIL
                else: store.back()
            else: store.back()
        else:
            self.NBsol += 1
            assert(Logprint.logPrint(2, "<=====****===== Found solution n°{} in {} backtracks{}".format(self.NBsol, self.NBbk, " at {}={}".format(self.OBJECTIVE.name, self.OBJECTIVE.inf if self.MINI else self.OBJECTIVE.sup) if self.OBJECTIVE else ""))==None)
            self.saveSolution()
            self.Bound = self.newBound()
            self.NBbkTot += self.NBbk; self.NBbk = 0
            if self.ALLSOL: raise filter.FAIL

def durationPrettyPrint(start, end):
    intsecs = end - start
    hours, seconds = divmod(intsecs, 3600)
    intsecs -= hours * 3600
    mins, seconds = divmod(intsecs, 60)
    intsecs -= mins * 60
    return "{0:n}:{1:n}:{2:n}".format(hours, mins, intsecs)
