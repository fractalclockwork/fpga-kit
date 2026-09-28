BOARD ?= nexys3
STAGE ?= present
export BOARD
PYTHON ?= python3
ifneq ($(wildcard .venv/bin/python),)
PYTHON := .venv/bin/python
endif

.PHONY: archive archive-image image stage sim build hil check cpld

archive:
	$(PYTHON) scripts/archive.py

image:
	bash scripts/ise_vnc_image.sh

archive-image: image
	$(PYTHON) scripts/archive.py --save-image

stage:
	$(PYTHON) scripts/stage.py --board $(BOARD) --stage $(STAGE)

sim:
	PATH="$(CURDIR)/.venv/bin:$(CURDIR)/.tools/usr/bin:$$PATH" $(MAKE) -C sim clean
	PATH="$(CURDIR)/.venv/bin:$(CURDIR)/.tools/usr/bin:$$PATH" $(MAKE) -C sim BOARD=$(BOARD)

build:
	$(PYTHON) scripts/flow.py --board $(BOARD)

cpld:
	$(PYTHON) scripts/cpld_flow.py $(BOARD)

hil:
	$(PYTHON) scripts/stage.py --board $(BOARD) --stage image

check:
	$(PYTHON) -m pytest -q
	$(MAKE) sim BOARD=nexys3
	$(MAKE) sim BOARD=vdec1
