from lib import Variable, Var, Assn
from heuristics import choose_splitting_var
import logging

class Assignment():
    '''
    Handles assignment info of variables
    '''

    def __init__(self, variables, sat):
        '''
        assignment_stack: stack of our assignments comprising
                          (assignment, variable) pairs, allowing backtracking easily.
                          Head of stack contains our current assignment.
        propagation_queue: Queue of variables that have been set to false
        '''
        self.sat = sat # For heuristics
        assignments = {}
        for var_ in variables.values():
            assignments[var_] = Assn.UNKNOWN

        self.assignment_stack = [
            (assignments, None)
        ]

        self.propagation_queue = []

    def __repr__(self):
        s = "===SAT Assignments===\n"
        for variable, assn in self.assignment_stack[-1][0].items():
            s += repr(variable) + ": " + Assn.toStr(assn) + "\n"
        return s

    def create_decision_level(self, variable: Variable, assn: Assn):
        '''
        Called when we are making a choice on an assignment that is not forced on us
        This creates a new assignment level off the old one
        '''
        assert assn != Assn.UNKNOWN, "Cannot assign unknown"
        assert self.assignment_stack[-1][0][variable] == Assn.UNKNOWN, "Cannot assign to assigned variable"

        new_assignment = self.assignment_stack[-1][0].copy()
        new_assignment[variable] = assn
        self.assignment_stack.append((new_assignment, variable))

        # Update propagation queue
        if assn == Assn.TRUE:
            self.propagation_queue.append(variable.getNeg())
            logging.debug(f"Adding {variable.getNeg()} to propagation queue")
        else:
            self.propagation_queue.append(variable.getPos())
            logging.debug(f"Adding {variable.getPos()} to propagation queue")

    def backtrack(self):
        '''
        Backtracks and restores assignment from previous level.
        We also return the variable that was used for the assignment at this level.
        '''
        assert len(self.assignment_stack) > 1, "Cannot backtrack from base layer"
        (_, var_) = self.assignment_stack.pop()
        return var_

    def assign(self, variable: Variable, assn: Assn):
        '''
        Performs an assignment that is forced on us, applied on the current
        decision level
        '''
        assert assn != Assn.UNKNOWN, "Cannot assign unknown"
        assert variable in self.assignment_stack[-1][0], "Use variable not var!"
        self.assignment_stack[-1][0][variable] = assn

        logging.debug(f"Assigning {variable} to {Assn.toStr(assn)}")

        # Update propagation queue
        if assn == Assn.TRUE:
            logging.debug(f"Adding {variable.getNeg()} to propagation queue")
            self.propagation_queue.append(variable.getNeg())
        else:
            logging.debug(f"Adding {variable.getPos()} to propagation queue")
            self.propagation_queue.append(variable.getPos())

        logging.debug(f"Propagation queue: {self.propagation_queue}")

    def num_unassigned(self):
        '''
        Returns number of unassigned variables at the current level
        '''
        num_unassigned = 0
        for assn in self.assignment_stack[-1][0].values():
            if assn == Assn.UNKNOWN:
                num_unassigned += 1

        return num_unassigned

    def get_unassigned_var(self):
        '''
        Returns the first unassigned variable that it finds
        Future extension: add better heuristics, allow users to specify their own
        '''
        try:
            var_ = choose_splitting_var(self.assignment_stack[-1][0], self.sat)
            assert self.get_assignment_val(var_.getPos()) == Assn.UNKNOWN, \
                "choose_splitting_var must return an unassigned var"
            return var_
        except NotImplementedError:
            # Default: find the first unassigned var
            for var_, assn in self.assignment_stack[-1][0].items():
                if assn == Assn.UNKNOWN:
                    return var_
                

    def get_assignment_val(self, var_: Var):
        '''
        Gets assignment value of a variable 
        If it is NOT x, then answer is negated
        '''
        var_base_val = self.assignment_stack[-1][0][var_.var]
        if var_.isNeg():
            return Assn.neg(var_base_val)
        return var_base_val

    def unit_propagation(self):
        '''
        Performs unit propagation on the current assignment

        Returns negative number if backtracking is necessary,
        else 0 on success
        '''
        while len(self.propagation_queue) > 0:
            var_ = self.propagation_queue.pop()
            logging.debug("Processing propagation queue: " + repr(var_))
            logging.debug(var_.watchingClauses())

            # Make a copy, as we are modifying this on the fly
            clauses = var_.watchingClauses().copy()
            for clause in clauses:
                # If the clause is watching some other
                # literal that is true, then we are fine
                logging.debug("Dealing with clause: " + clause.pp(self))
                if self.get_assignment_val(var_) != Assn.FALSE:
                    logging.debug(
                        "Current assignment no longer cause conflict")
                    continue

                if clause.is_watching_true(self):
                    logging.debug("Clause already satisfied")
                    continue

                # If not, we need to make the clause watch something else that is not False
                if clause.resolve_watch(var_, self) < 0:
                    logging.debug(
                        "Could not watch anything else, need to backtrack!")
                    return -1  # need to backtrack
                logging.debug("New watchlist: " + clause.pp(self))
                assert clause.is_not_just_watching_false(
                    self), "Should not be just watching false :" + clause.pp(self)
        return 0