#------------------------------------------------------------------------------------#
# benchs module: some benchmarks                                                     #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

r"""BENCHS: some benchmarks
"""
__version__ = '1.0.0'

__all__ = ('queens', 'sched_bridge_direct_simple')

__author__ = 'Pierre Savéant <pierre.saveant@thalesgroup.com>'

from .queens import queens
from sched_bridge_direct_simple import sched_bridge_direct_simple
