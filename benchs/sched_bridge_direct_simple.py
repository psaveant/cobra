#------------------------------------------------------------------------------------#
# sched_bridge_direct_simple.py: Bridge benchmark                                    #
# Copyright © 2015 - 2019 Thales SA - All Rights Reserved                            #
# Author: Pierre Savéant                                                             #
# This software is released as Open Source under the terms of a 3-clause BSD license #
#------------------------------------------------------------------------------------#

from argparse import ArgumentParser
import cobra

#The problem is to find a scheduling for the construction of a 5-segment bridge (Martin Bartusch PhD Thesis, 1983) and prove that its makespan is minimal.

# See the file "Constructing\ a\ Bridge.pdf" for a full description.

#python -O -m benchs.sched_bridge_direct_simple
#Optimization completed, min(STSTOP)=104 in      586 backtracks (     578 for proof) and 0:0:0.257542

def main(root=True, verbose=0, disjStatic=2, disjChoice=1, disjSide=0, timeout=None):
    cobra.Logprint(verbose)

# tasks
    start=cobra.Interval('Start', cobra.START, 0, cobra.HORIZON)
    a1=cobra.Interval('A1', cobra.START, 4, cobra.HORIZON)
    a2=cobra.Interval('A2', cobra.START, 2, cobra.HORIZON)
    a3=cobra.Interval('A3', cobra.START, 2, cobra.HORIZON)
    a4=cobra.Interval('A4', cobra.START, 2, cobra.HORIZON)
    a5=cobra.Interval('A5', cobra.START, 2, cobra.HORIZON)
    a6=cobra.Interval('A6', cobra.START, 5, cobra.HORIZON)
    p1=cobra.Interval('P1', cobra.START, 20, cobra.HORIZON)
    p2=cobra.Interval('P2', cobra.START, 13, cobra.HORIZON)
    ue=cobra.Interval('UE', cobra.START, 10, cobra.HORIZON)
    s1=cobra.Interval('S1', cobra.START, 8, cobra.HORIZON)
    s2=cobra.Interval('S2', cobra.START, 4, cobra.HORIZON)
    s3=cobra.Interval('S3', cobra.START, 4, cobra.HORIZON)
    s4=cobra.Interval('S4', cobra.START, 4, cobra.HORIZON)
    s5=cobra.Interval('S5', cobra.START, 4, cobra.HORIZON)
    s6=cobra.Interval('S6', cobra.START, 10, cobra.HORIZON)
    b1=cobra.Interval('B1', cobra.START, 1, cobra.HORIZON)
    b2=cobra.Interval('B2', cobra.START, 1, cobra.HORIZON)
    b3=cobra.Interval('B3', cobra.START, 1, cobra.HORIZON)
    b4=cobra.Interval('B4', cobra.START, 1, cobra.HORIZON)
    b5=cobra.Interval('B5', cobra.START, 1, cobra.HORIZON)
    b6=cobra.Interval('B6', cobra.START, 1, cobra.HORIZON)
    ab1=cobra.Interval('AB1', cobra.START, 1, cobra.HORIZON)
    ab2=cobra.Interval('AB2', cobra.START, 1, cobra.HORIZON)
    ab3=cobra.Interval('AB3', cobra.START, 1, cobra.HORIZON)
    ab4=cobra.Interval('AB4', cobra.START, 1, cobra.HORIZON)
    ab5=cobra.Interval('AB5', cobra.START, 1, cobra.HORIZON)
    ab6=cobra.Interval('AB6', cobra.START, 1, cobra.HORIZON)
    m1=cobra.Interval('M1', cobra.START, 16, cobra.HORIZON)
    m2=cobra.Interval('M2', cobra.START, 8, cobra.HORIZON)
    m3=cobra.Interval('M3', cobra.START, 8, cobra.HORIZON)
    m4=cobra.Interval('M4', cobra.START, 8, cobra.HORIZON)
    m5=cobra.Interval('M5', cobra.START, 8, cobra.HORIZON)
    m6=cobra.Interval('M6', cobra.START, 20, cobra.HORIZON)
    l=cobra.Interval('L', cobra.START, 2, cobra.HORIZON)
    t1=cobra.Interval('T1', cobra.START, 12, cobra.HORIZON)
    t2=cobra.Interval('T2', cobra.START, 12, cobra.HORIZON)
    t3=cobra.Interval('T3', cobra.START, 12, cobra.HORIZON)
    t4=cobra.Interval('T4', cobra.START, 12, cobra.HORIZON)
    t5=cobra.Interval('T5', cobra.START, 12, cobra.HORIZON)
    ua=cobra.Interval('UA', cobra.START, 10, cobra.HORIZON)
    v1=cobra.Interval('V1', cobra.START, 15, cobra.HORIZON)
    v2=cobra.Interval('V2', cobra.START, 10, cobra.HORIZON)
    k1=cobra.Interval('K1', cobra.START, 0, cobra.HORIZON)
    k2=cobra.Interval('K2', cobra.START, 0, cobra.HORIZON)
    stop=cobra.Interval('STOP', cobra.START, 0, cobra.HORIZON)

# precedences
    cobra.endBeforeStart(start,a1)
    cobra.endBeforeStart(start,a2)
    cobra.endBeforeStart(start,a3)
    cobra.endBeforeStart(start,a4)
    cobra.endBeforeStart(start,a5)
    cobra.endBeforeStart(start,a6)
    cobra.endBeforeStart(start,ue)
    
    cobra.endBeforeStart(a1,s1)
    cobra.endBeforeStart(a2,s2)
    cobra.endBeforeStart(a5,s5)
    cobra.endBeforeStart(a6,s6)
    cobra.endBeforeStart(a3,p1)
    cobra.endBeforeStart(a4,p2)
    
    cobra.endBeforeStart(p1,s3)
    cobra.endBeforeStart(p2,s4)
    
    cobra.endBeforeStart(p1,k1)
    cobra.endBeforeStart(p2,k1)
    
    cobra.endBeforeStart(s1,b1)
    cobra.endBeforeStart(s2,b2)
    cobra.endBeforeStart(s3,b3)
    cobra.endBeforeStart(s4,b4)
    cobra.endBeforeStart(s5,b5)
    cobra.endBeforeStart(s6,b6)
    
    cobra.endBeforeStart(b1,ab1)
    cobra.endBeforeStart(b2,ab2)
    cobra.endBeforeStart(b3,ab3)
    cobra.endBeforeStart(b4,ab4)
    cobra.endBeforeStart(b5,ab5)
    cobra.endBeforeStart(b6,ab6)
    
    cobra.endBeforeStart(ab1,m1)
    cobra.endBeforeStart(ab2,m2)
    cobra.endBeforeStart(ab3,m3)
    cobra.endBeforeStart(ab4,m4)
    cobra.endBeforeStart(ab5,m5)
    cobra.endBeforeStart(ab6,m6)
    
    cobra.endBeforeStart(m1,t1)
    cobra.endBeforeStart(m2,t1)
    cobra.endBeforeStart(m2,t2)
    cobra.endBeforeStart(m3,t2)
    cobra.endBeforeStart(m3,t3)
    cobra.endBeforeStart(m4,t3)
    cobra.endBeforeStart(m4,t4)
    cobra.endBeforeStart(m5,t4)
    cobra.endBeforeStart(m5,t5)
    cobra.endBeforeStart(m6,t5)
    
    cobra.endBeforeStart(m1,k2)
    cobra.endBeforeStart(m2,k2)
    cobra.endBeforeStart(m3,k2)
    cobra.endBeforeStart(m4,k2)
    cobra.endBeforeStart(m5,k2)
    cobra.endBeforeStart(m6,k2)
     
    cobra.endBeforeStart(l,t1)
    cobra.endBeforeStart(l,t2)
    cobra.endBeforeStart(l,t3)
    cobra.endBeforeStart(l,t4)
    cobra.endBeforeStart(l,t5)
    
    cobra.endBeforeStart(t1,v1)
    cobra.endBeforeStart(t5,v2)
     
    cobra.endBeforeStart(t2,stop)
    cobra.endBeforeStart(t3,stop)
    cobra.endBeforeStart(t4,stop)
    cobra.endBeforeStart(v1,stop)
    cobra.endBeforeStart(v2,stop)
    cobra.endBeforeStart(ua,stop)
    cobra.endBeforeStart(k1,stop)
    cobra.endBeforeStart(k2,stop)

    cobra.startBeforeEnd(l, start, -30)
    cobra.startBeforeEnd(s1, a1, -3)
    cobra.startBeforeEnd(s2, a2, -3)
    cobra.startBeforeEnd(s5, a5, -3)
    cobra.startBeforeEnd(s6, a6, -3)
    cobra.startBeforeEnd(s3, p1, -3)
    cobra.startBeforeEnd(s4, p2, -3)

    cobra.endBeforeEnd(b6, s6, -4)
    cobra.endBeforeEnd(b5, s5, -4)
    cobra.endBeforeEnd(b4, s4, -4)
    cobra.endBeforeEnd(b3, s3, -4)
    cobra.endBeforeEnd(b2, s2, -4)
    cobra.endBeforeEnd(b1, s1, -4)

    cobra.startBeforeStart(ue, s1, 6)
    cobra.startBeforeStart(ue, s2, 6)
    cobra.startBeforeStart(ue, s3, 6)
    cobra.startBeforeStart(ue, s4, 6)
    cobra.startBeforeStart(ue, s5, 6)
    cobra.startBeforeStart(ue, s6, 6)

    cobra.endBeforeStart(m1, ua, -2)
    cobra.endBeforeStart(m2, ua, -2)
    cobra.endBeforeStart(m3, ua, -2)
    cobra.endBeforeStart(m4, ua, -2)
    cobra.endBeforeStart(m5, ua, -2)
    cobra.endBeforeStart(m6, ua, -2)

    cobra.endBeforeStart(start, l, 30)

# resources
    Resource = {}
    Resource['crane']=[t1,t2,t3,t4,t5]
    Resource['bricklaying']=[m1,m2,m3,m4,m5,m6]
    Resource['carpentry']=[s1,s2,s3,s4,s5,s6]
    Resource['excavator']=[a1,a2,a3,a4,a5,a6]
    Resource['piledriver']=[p1,p2]
    Resource['concretemixer']=[b1,b2,b3,b4,b5,b6]
    Resource['caterpillar']=[v1,v2]

# NonOverlaping constraint
    for key, tasks in Resource.items(): 
        for i, t1 in enumerate(tasks[:-1]):
            for t2 in tasks[i+1:]:
                cobra.ordering(t2.st, t2.sp, t1.st, t1.sp)

# Solve
    optimizer = cobra.Optimizer(stop.st, 0, mini=True, root=root, disjStatic=disjStatic, disjChoice=disjChoice, disjSide=disjSide)
    sol = optimizer.optimize(timeout)
    print("python -O -m benchs.sched_bridge_direct -x {} -y {} -z {}".format(disjStatic, disjChoice, disjSide))
    print("Optimization {}, {} in {:>8} backtracks ({:>8} for proof) and {}".format("completed" if sol.completion else "interrupted", "min({})={}".format(sol.objname, sol.objvalue) if sol.vars else "no solution found", sol.backtracks, sol.proof, sol.duration))
    cobra.showVar(sol.vars)

if __name__ == "__main__":
    parser = ArgumentParser(description='Bridge Benchmark')
    parser.add_argument("-b", "--branchANDbound", help="-b=Branch and Bound, default=Root", action='store_true', default=False)
    parser.add_argument("-v", "--verbose", type=int, choices=[0, 2, 3, 4, 5], help="0=quiet, 2=search progression, 4=constraint propagation, 5=trailing", default=0)
    parser.add_argument("-x", "--disjStatic", type=int, choices=[0, 1, 2, 3, 4], help="0=no reordering, 1=reverse declaration order, 2=earliest time first, 3=latest time first, 4=smallest proximity", default=1)
    parser.add_argument("-y", "--disjChoice", type=int, choices=[0, 1, 2, 3, 4, 5], help="0=implementation order, 1=heaviest weight first, 2=largest proximity first, 3=heaviest weight first and then earliest time, 4=latest time first, 5=smallest proximity of maximum of minimum Earliest Starting Time", default=4)
    parser.add_argument("-z", "--disjSide", type=int, choices=[0, 1, 2, 3, 4, 5, 6], help="0=declaration side, 1=highest weight first, 2=lowest weight first, 3=latest time first, 4=earliest time first, 5=latest ending time first, 6=earliest ending time first", default=0)
    parser.add_argument("-t", "--timeout", help="Budget time in seconds (or fractions thereof)", type=float, default=None)
    args = parser.parse_args()
    main(root=not(args.branchANDbound), verbose=args.verbose, disjStatic=args.disjStatic, disjChoice=args.disjChoice, disjSide=args.disjSide, timeout=args.timeout)
