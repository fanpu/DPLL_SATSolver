#!/usr/bin/env python3

import re
import logging
import argparse
from loader import Loader
from lib import Variable, Assn, Var, Clause, SAT, UnsatException, VARIABLES
from typing import List
from assignment import Assignment
from heuristics import choose_assn


class SATSolver():
    def __init__(self, sat):
        self.assignments = Assignment(VARIABLES, sat)
        self.sat = sat

    def check_invariants(self):
        '''
        Checking that we don't have any clause that is already unsatisfiable
        Mainly for debugging purposes
        '''
        for clause in self.sat.clauses:
            num_false = 0
            # Check not all assignments false
            for var_ in clause.vars:
                if self.assignments.get_assignment_val(var_) == Assn.FALSE:
                    num_false += 1
            assert num_false < len(clause.vars), "Invariants broken, clause:" + clause.pp(self.assignments)

            both_false = True
            # Check that watched by and watching is consistent
            for watch_idx in clause.watchlist:
                var_ = clause.vars[watch_idx]
                assert var_.watchedBy.count(clause) >= 1, "watchedBy inconsistent with watchlist"

                # Check that what we are watching is not both false
                both_false &= self.assignments.get_assignment_val(var_) == Assn.FALSE

            assert not both_false, "Cannot be watching both literals false: " + clause.pp(self.assignments)

        def check_watched_by(var_):
            for clause in var_.watchingClauses():
                var1 = clause.vars[clause.watchlist[0]] 
                var2 = clause.vars[clause.watchlist[1]] 
                assert var1 == var_ or var2 == var_, "Watchlist/watched by invariants broken"
            pass

        # Check that watched by and watching is consistent
        for variable in VARIABLES.values():
            posVar = variable.getPos()
            negVar = variable.getNeg()
            check_watched_by(posVar)
            check_watched_by(negVar)


    def dpll(self):
        while self.assignments.num_unassigned() > 0:
            if self.assignments.unit_propagation() < 0:
                print("UNSATISFIABLE")
                return

            self.check_invariants()

            # Choose a variable to assign
            var_ = self.assignments.get_unassigned_var()

            # Try setting true first
            assn = Assn.TRUE
            try:
                assn = choose_assn(var_, self.assignments.assignment_stack[-1][0], self.sat)
            except NotImplementedError:
                pass

            logging.info("Trying " + repr(var_) + ": " + Assn.toStr(assn))
            self.assignments.create_decision_level(var_, Assn.TRUE)
            logging.debug(
                f"Assignment stack size: {len(self.assignments.assignment_stack)}")

            # Backtrack until we can unit propagate without conflicts
            while self.assignments.unit_propagation() < 0:
                # If there are conflicts, backtrack and set the previous
                # variable to false
                logging.info("Backtracking...")
                if len(self.assignments.assignment_stack) <= 1:
                    # Out of options
                    print("UNSATISFIABLE")
                    return

                conflict_var = self.assignments.assignment_stack[-1][1]
                old_conflict_assn = self.assignments.get_assignment_val(conflict_var.getPos())
                assert old_conflict_assn != Assn.UNKNOWN
                new_conflict_assn = Assn.neg(old_conflict_assn)
                self.assignments.backtrack()

                logging.debug(
                    f"Assignment stack size: {len(self.assignments.assignment_stack)}")

                self.check_invariants()

                logging.info("Trying " + repr(conflict_var) + ": " + Assn.toStr(new_conflict_assn))
                self.assignments.assign(conflict_var, new_conflict_assn)

        print("SATISFIABLE")
        logging.info(self.assignments)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbosity", help="increase output verbosity", action="count")
    parser.add_argument('files', metavar='f', type=str, nargs=1,
                    help='CNF file to test for satisfiability')
    args = parser.parse_args()
    if args.verbosity == 2:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARN)

    print(args.files[0])
    sat = Loader.load_file(args.files[0])
    logging.info(sat)
    sat_solver = SATSolver(sat)
    sat_solver.dpll()