"""For reading in DIMACS file format

DIMACS file format:

Lines that start with c are comments:
c This line is a comment.

Problem line, which says this is a CNF problem with 3 vars and 4 clauses:
p cnf 3 4

The clauses are then listed. 0 marks the end of each clause. 
Positive numbers indicate positive occurrence, negative numbes
represent negated occurrence.

"""
import re
import logging
from lib import Variable, Assn, Var, Clause, SAT, VarFactory, VARIABLES


class Loader():
    @staticmethod
    def load(s):
        """Loads a SAT expression
        """
        VARIABLES = {}
        clauses = []

        lines = s.split('\n')

        pComment = re.compile(r'c.*')
        pStats = re.compile(r'p\s*cnf\s*(\d*)\s*(\d*)')
        pEnd = re.compile(r'%')  # Some testcases are terminated by %\n0

        while len(lines) > 0:
            line = lines.pop(0)

            # Only deal with lines that aren't comments
            if not pComment.match(line):
                e = pEnd.match(line)
                if e:
                    break

                m = pStats.match(line)

                if not m:
                    nums = line.rstrip('\n').split(' ')
                    l = []
                    for lit in nums:
                        if lit != '':
                            if int(lit) == 0:
                                continue
                            num = abs(int(lit))
                            neg = False
                            if int(lit) < 0:
                                neg = True
                            l.append(VarFactory.get_var(num, neg))

                    if len(l) > 0:
                        # Use set to dedupe
                        clauses.append(Clause(l))
                else:
                    logging.info(f"CNF with {m[1]} variables and {m[2]} clauses")

        return SAT(clauses)

    @staticmethod
    def load_file(location):
        """Loads a CNF from a file."""
        with open(location) as f:
            s = f.read()

        return Loader.load(s)
