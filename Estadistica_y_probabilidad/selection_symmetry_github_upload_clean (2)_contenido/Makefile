.PHONY: all results test paper clean

all: results paper

results:
	python scripts/run_all.py

test:
	python -m unittest discover -s tests

paper:
	latexmk -pdf paper/main.tex

clean:
	latexmk -C paper/main.tex
