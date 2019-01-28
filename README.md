
# Cobra
## A Constraint Solver over Discrete Intervals

## What is Cobra?

COBRA is a constraint solver over finite domains. When the search terminates it can proove either the unsatisfiability when the problem is overconstrained or the optimality when there is an objective function.


COBRA is compatible with Python release 3.6 or greater.


COBRA is packaged as a Python module called here minicobra.

For a performace issue it is recommanded to add the -O option of Python which will disable all assert and logging statements.

For instance, the following benchmarks can be solved with the following commands:

Bridge benchmark: python -O -m benchs.sched_bridge_direct_simple
N-Queens benchmark: python -O -m benchs.queens 8 -b

To get a more verbose run you can use the -v option which fixed the global variable VERBOSE:
*  VERBOSE=0: Quiet
*  VERBOSE=2: Branching in action
*  VERBOSE=4: Look-Ahead in action
*  VERBOSE=5: Trailing in Action

For instance on the following benchmarks:

```python
python -m benchs.sched_bridge_direct_simple -v 2
python -m benchs.queens 8 -b -v 2
```

# Applicative Programming Interface

* clear() is used for deleting all global variables so that you can run the solver many times in a same session.

* Optimizer is a class to be instantiated for each problem to solve.

* Solution is a named-tuple representing a solution (cf. the optimize() method).

* validate(vars, sol) instantiates the variables with the solution values and return True if all constraints are satisfied.

* showVar(d): shows the variables contains in the dictionnary d.

* ZER0: the null element used with the addition.

* UN: the successor of ZERO.

* DEUX: the successor of UN.

* START: the earliest time of the schedule.

* MINSTART: not used here.

* HORIZON: the latest time of the schedule.

* 'TRUE', 'FALSE', 'UNKNOWN': three-valued logic.

* FAIL: the exception raised when a domain is empty.

* Var(<name>, inf, sup): the class to instantiate to create a variable (default domain is [START, HORIZON])

* Constraint: the class to inherit to create a constraint.

* MetaConstraint: the class to inherit to create a Boolean reified constraint. 

* UnConstraint: the class to inherit to create an unary constraint.

* ArithmConstraint: the class to inherit to create an arithmetic constraint.

* supxc, infxc, equxc, nequxc, nequxyc, supxyc, infxyc, strictsupxyc, strictinfxyc, equxyc, equxyzc: a bunch of arithmetic constraints.

* Supxc, Infxc, Equxc, Nequxc, Nequxyc, Supxyc, Infxyc, Equxyc, Equxyzc: the classes to use inside Boolean constraints.

* Logprint: the class which host the logPrint() function dependent of a verbosity level. (For performance issue it is recommanded to put it in an assert staetement).

* disjunction: the Boolean exclusive (and constructive) disjunction. BEWARE: the reifed constraints appearing in the metaconstraint MUST BE DENOTED with their class name (with a capital letter). (cf. the ordering constraint).

* Disjunction: the class to use for reified constraints inside Boolean constraints.

* ordering: the disjunctive constraint for task scheduling: ordering(v1, d1, v2, d2) <=> (v2 + d2 <= v1) or (v1 + d1 <= v2) .

* Interval(<name>, <start>, <duration>, <end>): the class to instantiate to create a task with a variable earliest starting time and a fixed duration; The default task is [START, HORIZON] with a ZERO duration. <start> is a variable, but duration and end are fixed.

* startBeforeEnd, startBeforeStart, endBeforeEnd, endBeforeStart, startAtEnd, startAtStart, endAtEnd, endAtStart: a bunch of precedence constraints over intervals.


# Optimizer Class


The init arguments are the following:

* objective: either the objective variable or None for a satisfaction problem (default).

* search 
          ** 0: Disjunctive Search (default)
          ** 1: Unused
          ** 2: Enumeration on variables
          ** 3: Dichotomic search

* mini: True if minimizing (default)

* bound: an upper bound for minimization and a lower for maximization.

* incBound: the bound increment (default UN for minimization and *UN for maximization).

* root: when True restarts from the root of the search tree, when False carry chronological backtracking. For satisfaction problem the semantics is True for one solution only and False for all solutions.

* disjStatic: heuritic in the disjunctive enumeration: static ordering of the disjunctions:
          ** 0: no reordering
	  ** 1: reverse declaration order
	  ** 2: earliest time first (default)
	  ** 3: latest time first
	  ** 4: smallest proximity

* disjChoice: heuritic in the disjunctive enumeration: dynamic disjunction choice:
          ** 0: implementation order
	  ** 1:heaviest weight first
	  ** 2: largest proximity first
	  ** 3: heaviest weight first and then earliest time
	  ** 4: latest time first
	  ** 5: smallest proximity of maximum of minimum Earliest Starting Time


* disjSide: heuritic in the disjunctive enumeration: disjunction side choice:
          ** 0: implementation order
	  ** 1: heaviest weight disjunction side first
	  ** 2: lowest weight disjunction side first
	  ** 3: latest starting time disjunction side first
	  ** 4: earliest starting time disjunction side first
	  ** 5: latest ending time disjunction side first
	  ** 6: earliest ending time disjunction side first

* varChoice: heuritic in variable enumeration:
          ** 0: implementation order
	  ** 1: minimum domain first (First-Fail principle)



To solve a problem you have to call the method optimize() of your instance of Optimizer wich return a Solution named-tuple.

Solution = namedtuple('Solution', ['vars', 'objname', 'objvalue', 'backtracks', 'proof', 'duration', 'completion', 'nsol']).

* vars is False (None) when there is no solution and a dictionnary which gives the value of each variable (with their name as the key).
* objname is the name of the objective variable.
* objvalue the value of the objective.
* backtracks: the total number of attempts in the enumeration.
* proof: the number of attempts for completing the search and proves the optimum.
* duration: runtime.
* completion  True if the serch tree is completed.
* nsol: the total number of solutions.

The search might be interrupted from the keyboard by a CTRL-C.
