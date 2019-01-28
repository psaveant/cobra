#------------------------------------------------------------------------------------#
# store module: Generic Trailer                                                      #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

r"""STORE: Generic Trailer
"""
__version__ = '1.0.0'

__all__ = ('clear', 'assign', 'push', 'back', 'backtrack', 'current')

__author__ = 'Pierre Savéant <pierre.saveant@thalesgroup.com>'

from .store import clear, assign, push, back, backtrack, current
