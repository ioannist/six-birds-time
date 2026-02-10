.PHONY: test smoke paper

test:
	cd python && pytest

smoke:
	cd python && python scripts/_smoke_artifact.py

paper-tables:
	python python/scripts/paper/make_paper_tables.py

paper:
	python scripts/build_time_paper.py
