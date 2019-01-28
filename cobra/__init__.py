#------------------------------------------------------------------------------------#
# cobra module: Constraint Solver over Discrete Intervals                            #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

r"""COBRA: constraint-based scheduling
"""
__version__ = '1.0.0'

__all__ = (
'clear',
'Optimizer', 'Solution', 'validate', 'showVar',

'ZERO', 'UN', 'DEUX', 'START', 'MINSTART', 'HORIZON', 'TRUE', 'FALSE', 'UNKNOWN', 'FAIL', 'Var', 'Constraint', 'MetaConstraint', 'UnConstraint', 'ArithmConstraint', 'supxc', 'infxc', 'equxc', 'nequxc', 'nequxyc', 'supxyc', 'infxyc', 'strictsupxyc', 'strictinfxyc', 'equxyc', 'equxyzc', 'Supxc', 'Infxc', 'Equxc', 'Nequxc', 'Nequxyc', 'Supxyc', 'Infxyc', 'Equxyc', 'Equxyzc', 'Logprint',

'Interval', 'startBeforeEnd', 'startBeforeStart', 'endBeforeEnd', 'endBeforeStart', 'startAtEnd', 'startAtStart', 'endAtEnd', 'endAtStart',

'disjunction', 'ordering', 'Disjunction'
)

__author__ = 'Pierre Savéant <pierre.saveant@thalesgroup.com>'

from .solver import Optimizer, Solution, validate, showVar
from .filter import ZERO, UN, DEUX, START, HORIZON, TRUE, FALSE, UNKNOWN, FAIL, Var, Constraint, MetaConstraint, UnConstraint, ArithmConstraint, supxc, infxc, equxc, nequxc, nequxyc, supxyc, infxyc, strictsupxyc, strictinfxyc, equxyc, equxyzc, Supxc, Infxc, Equxc, Nequxc, Nequxyc, Supxyc, Infxyc, Equxyc, Equxyzc, Logprint

from .interval import Interval, startBeforeEnd, startBeforeStart, endBeforeEnd, endBeforeStart, startAtEnd, startAtStart, endAtEnd, endAtStart

from .bool import disjunction, ordering, Disjunction
import store

def clear():
    store.clear()
    filter.clear()
    interval.clear()
    bool.clear()
