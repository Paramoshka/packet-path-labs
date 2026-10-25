LAB ?=
TOPO := $(firstword $(wildcard labs/$(LAB)/*.clab.yml))

.PHONY: list up down inspect check

list:
	@find labs -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | sort

up:
	@test -n "$(LAB)" || (echo "usage: make up LAB=04-ebgp-basics"; exit 1)
	@test -n "$(TOPO)" || (echo "topology not found for $(LAB)"; exit 1)
	sudo containerlab deploy -t $(TOPO)

down:
	@test -n "$(LAB)" || (echo "usage: make down LAB=04-ebgp-basics"; exit 1)
	@test -n "$(TOPO)" || (echo "topology not found for $(LAB)"; exit 1)
	sudo containerlab destroy -t $(TOPO)

inspect:
	@test -n "$(LAB)" || (echo "usage: make inspect LAB=04-ebgp-basics"; exit 1)
	@test -n "$(TOPO)" || (echo "topology not found for $(LAB)"; exit 1)
	containerlab inspect -t $(TOPO)

check:
	python3 scripts/validate_labs.py
	python3 -m unittest discover -s scripts -p 'test_*.py'
