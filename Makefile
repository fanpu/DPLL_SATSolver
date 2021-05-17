.PHONY: setup
setup: 
	@echo "Fetching test files"
	mkdir -p testcases/sat
	mkdir -p testcases/unsat
	wget https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf50-218.tar.gz -P testcases/sat/
	wget https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uuf50-218.tar.gz -P testcases/unsat/
	cd testcases/sat && tar xf uf50-218.tar.gz && cd ../unsat && tar xf uuf50-218.tar.gz

.PHONY: sat
sat:
	@echo "Testing satisfiable CNFs"
	ls testcases/sat | xargs printf -- 'testcases/sat/%s\n' | xargs -L 1 ./sat.py

.PHONY: unsat
unsat:
	@echo "Testing unsatisfiable CNFs"
	ls testcases/unsat | xargs printf -- 'testcases/unsat/%s\n' | xargs -L 1 ./sat.py

.PHONY: clean
clean:
	rm -rf ./testcases
