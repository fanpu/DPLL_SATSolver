'''
Define your heuristics for choosing variables, and the value to assign first 
in this file
'''
import random
from lib import Assn


def choose_splitting_var(assignments, sat):
    '''
    Custom function to choose which variable to split on, this
    can be modified by user to specify their own heuristic

    The current sample implementation just chooses a variable randomly 
    from the remaining variables.

    assignments:    a map of the current variable to the current assignments
    sat:            the current SAT formula

    return: the variable to split on, this should not be assigned
    '''
    # Comment below to not use default policy that simply uses the
    # first unassigned variable
    raise NotImplementedError

    # ===================================================
    # Random strategy: uncomment to use
    # candidates = []
    # for var_, assn in assignments.items():
    #     if assn == Assn.UNKNOWN:
    #         candidates.append(var_)
    # return candidates[random.randrange(len(candidates))]
    # ===================================================

def choose_assn(var_, assignments, sat):
    '''
    Custom function to choose which truth value to try first, this
    can be modified by user to specify their own heuristic.

    The current sample implementation chooses randomly.

    var_:           unassigned variable to choose first truth assignment for
    assignments:    a map of the current assignments
    sat:            current SAT instance

    return: either Assn.TRUE or Assn.FALSE
    '''
    # Comment below to not use default policy that simply uses True
    # first followed by False
    # raise NotImplementedError

    # ===================================================
    # Random strategy: uncomment to use
    # return Assn.TRUE if random.randint(0, 1) == 1 else Assn.FALSE
    # ===================================================


    # ===================================================
    # Using the value that satisfies most of the clauses that it appears in 
    # Uncomment to use
    pos_instance = 0
    neg_instance = 0
    for clause in sat.clauses:
        for v in clause.vars:
            if v.var == var_:
                if v.isNeg():
                    neg_instance += 1
                else:
                    pos_instance += 1
    return Assn.TRUE if pos_instance >= neg_instance else Assn.FALSE
    # ===================================================

    
