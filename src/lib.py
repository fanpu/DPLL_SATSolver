from enum import Enum
from typing import List
import logging

# Global map of all variables defined
VARIABLES = {}


class UnsatException(Exception):
    pass


class Assn(Enum):
    '''
    Represents the value of assignment
    '''
    UNKNOWN = -1
    FALSE = 0
    TRUE = 1

    @staticmethod
    def toStr(assn):
        if assn == Assn.UNKNOWN:
            return "U"
        elif assn == Assn.FALSE:
            return "F"
        elif assn == Assn.TRUE:
            return "T"

    @staticmethod
    def neg(assn):
        if assn == Assn.UNKNOWN:
            return Assn.UNKNOWN
        elif assn == Assn.FALSE:
            return Assn.TRUE
        elif assn == Assn.TRUE:
            return Assn.FALSE


class Var():
    '''
    Represents either x or NOT x, where x is a Variable
    This is what actually appears in a clause. 
    Var are singletons, and new Vars should only be instantiated
    with VarFactory

    self.neg: Whether the literal is x or not x
    self.var: base variable
    '''

    def __init__(self, var_, neg=False):
        self.neg = neg
        self.var = var_
        self.watchedBy = []

    def __repr__(self):
        if self.neg:
          return "¬" + repr(self.var)
        return repr(self.var)

    def addWatchedBy(self, clause):
        if clause not in self.watchedBy:
          self.watchedBy.append(clause)

    def removeWatchedBy(self, clause):
        self.watchedBy.remove(clause)

    def isNeg(self):
        return self.neg

    def watchingClauses(self):
        return self.watchedBy


class Variable():
    '''
    Represents an abstract variable, i.e x
    This does not contain info on whether it is negated, 
    that falls under the domain of Var.

    So normally, we have a relationship that looks like this:

                  ----- Var (x)
    Variable (x) /
                 \------Var (NOT x)

    Variables are singletons, and is implicitly created
    by VarFactory when instantiating Vars.

    label: the label of the variable
    '''

    def __init__(self, label: int):
        assert label not in VARIABLES
        self.label = label
        VARIABLES[label] = self
        self.pos = Var(self, False)
        self.neg = Var(self, True)

    def __repr__(self):
        return 'x' + str(self.label)

    def getPos(self):
        '''Get positive representation, i.e x
        '''
        return self.pos

    def getNeg(self):
        '''Get negative representation, i.e not x
        '''
        return self.neg


class VarFactory():
    '''
    Factory for getting singleton vars
    '''
    @staticmethod
    def get_var(label: int, neg: bool):
        if label in VARIABLES:
            return VARIABLES[label].getNeg() if neg else VARIABLES[label].getPos()
        var_ = Variable(label)
        return var_.getNeg() if neg else var_.getPos()


class Clause():
    '''
    A CNF clause
    '''
    def __init__(self, variables: List[Var]):
        self.vars = variables
        assert len(self.vars) >= 2  # Temporary assumption

        # Initialize watchlist on first two indices
        # Watchlist contains index of variables watched
        self.watchlist = [0, 1]
        self.vars[0].addWatchedBy(self)
        self.vars[1].addWatchedBy(self)

    def __repr__(self):
        l = []
        for idx, var in enumerate(self.vars):
            if idx in self.watchlist:
                l.append(repr(var) + "*")
            else:
                l.append(repr(var))

        v = " ∨ ".join(l)
        return f"({v})"

    def pp(self, assignment):
        '''
        Pretty print with current assignment info
        '''
        l = []
        for idx, var in enumerate(self.vars):
            assn = Assn.toStr(assignment.get_assignment_val(var))
            if idx in self.watchlist:
                l.append(repr(var) + f"{assn}*")
            else:
                l.append(repr(var) + f"{assn}")

        v = " ∨ ".join(l)
        return f"({v})"

    def is_watching_true(self, assignment):
        '''
        Returns if at least one of the variables that this clause is watching is true
        '''
        var1 = self.vars[self.watchlist[0]]
        var2 = self.vars[self.watchlist[1]]
        return assignment.get_assignment_val(var1) == Assn.TRUE or \
            assignment.get_assignment_val(var2) == Assn.TRUE

    def is_not_just_watching_false(self, assignment):
        '''
        Returns if at least one of the variables that this clause is watching is non-false
        '''
        var1 = self.vars[self.watchlist[0]]
        var2 = self.vars[self.watchlist[1]]
        return assignment.get_assignment_val(var1) != Assn.FALSE or \
            assignment.get_assignment_val(var2) != Assn.FALSE

    def resolve_watch(self, var_to_change: Var, assignment):
        '''
        Called when both literals being watched is false
        This function tries to find another literal to watch instead of var_to_change

        If it succeeds, returns 0
        Else returns negative int
        '''
        logging.debug("Resolving clause " + self.pp(assignment) +
                      " due to " + repr(var_to_change))

        # Find index in watchlist
        to_change_wl_idx = 0 if self.vars[self.watchlist[0]
                                          ] == var_to_change else 1
        other_wl_idx = 1 - to_change_wl_idx
        to_change_var_idx = self.watchlist[to_change_wl_idx]
        other_var_idx = self.watchlist[other_wl_idx]

        new_idx = -1  # new idx to watch
        for idx, var in enumerate(self.vars):
            if idx == to_change_var_idx or idx == other_var_idx:
                continue

            # Check if not false
            if assignment.get_assignment_val(var) != Assn.FALSE:
                new_idx = idx
                break

        # If not possible to find any other index to watch because everything else is false, then the other literal being watched must be false
        if new_idx == -1:
            other_watched_var = self.vars[other_var_idx]
            if assignment.get_assignment_val(other_watched_var) == Assn.FALSE:
                # If already assigned to false, we have a contradiction, need
                # to backtrack
                return -1

            # Else we force it to the value that makes it true
            assn_val = Assn.FALSE if other_watched_var.isNeg() else Assn.TRUE
            assignment.assign(other_watched_var.var, assn_val)
        else:
            # Else watch the indeterminate/truthy thing we found
            self.watchlist[to_change_wl_idx] = new_idx
            var_to_change.removeWatchedBy(self)
            self.vars[new_idx].addWatchedBy(self)

        logging.debug(f"New wl: {self.watchlist}")
        assert self.watchlist[0] != self.watchlist[1]

        return 0


class SAT():
    '''
    A SAT formula in CNF form
    '''

    def __init__(self, clauses):
        self.clauses = clauses

    def __repr__(self):
        return " ∧ ".join([repr(c) for c in self.clauses])

