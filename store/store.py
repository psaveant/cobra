#------------------------------------------------------------------------------------#
# store.py: Generic Trailer                                                          #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

from cobra.filter import Logprint

#------------------------------- API ------------------------------------------------#
__all__ = ('clear', 'assign', 'push', 'back', 'backtrack', 'current')

#------------------------------- Store -----------------------------------------------
#  VERBOSE=0: Quiet
#  VERBOSE=5: Trailing in Action

# Assumption: only few changes occurred in each state simultaneously.

trail = [[]]

def current(): return len(trail)-1

def clear():
    trail = [[]]

def assign(obj, att, value): # Assigns value to obj.att
    assert(Logprint.logPrint(5, "ASSIGN: {}.{}={}".format(obj, att, value))==None)
    trail[-1].append((obj, att, getattr(obj, att)))
    setattr(obj, att, value)

def push(): # Create a new world
    assert(Logprint.logPrint(5, "PUSH: {}".format(trail))==None)
    trail.append([])

def back(): # Restore the previous world
    assert(Logprint.logPrint(5, "BACK: {}".format(trail))==None)
    for obj, att, value in reversed(trail.pop(-1)): setattr(obj, att, value)

def backtrack(n): # Back to world n
    while current() > n: back()
