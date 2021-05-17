.PHONY: setup
setup: 
	@echo "Fetching test files"
	mkdir -p dat/sat
	mkdir -p dat/unsat
	wget https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uf50-218.tar.gz -P dat/sat/
	wget https://www.cs.ubc.ca/~hoos/SATLIB/Benchmarks/SAT/RND3SAT/uuf50-218.tar.gz -P dat/unsat/
	cd dat/sat && tar xf uf50-218.tar.gz && cd ../unsat && tar xf uuf50-218.tar.gz && cd ../..
	rm dat/sat/uf50-218.tar.gz
	mv dat/unsat/UUF50.218.1000/* dat/unsat
	rmdir dat/unsat/UUF50.218.1000
	rm dat/unsat/uuf50-218.tar.gz


.PHONY: sat
sat:
	@echo "Testing satisfiable CNFs"
	ls dat/sat | xargs printf -- 'dat/sat/%s\n' | xargs -L 1 ./src/sat.py

.PHONY: unsat
unsat:
	@echo "Testing unsatisfiable CNFs"
	ls dat/unsat | xargs printf -- 'dat/unsat/%s\n' | xargs -L 1 ./src/sat.py

.PHONY: clean
clean:
	rm -rf ./dat
