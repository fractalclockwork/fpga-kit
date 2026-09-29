#!/bin/bash
# Headless CPLD fit. The host writes project.xst, project.prj,
# and project.ucf into the run directory before starting this script.
# CoolRunner-II accepts cpldfit -iostd (default LVCMOS33). XC9500XL
# rejects that switch; optional iostd.txt is ignored for that family.
set -euo pipefail

RUN="${1:?run directory}"
cd "$RUN"
PART="$(tr -d '[:space:]' < part.txt)"

printf 'PHASE xst\n'
xst -intstyle ise -ifn project.xst

printf 'PHASE ngdbuild\n'
ngdbuild -intstyle ise -uc project.ucf -p "$PART" project.ngc project.ngd

printf 'PHASE cpldfit\n'
if [[ "$PART" == *xc95* ]]; then
  cpldfit -intstyle ise -p "$PART" -optimize density project.ngd
else
  IOSTD=LVCMOS33
  if [[ -f iostd.txt ]]; then
    IOSTD="$(tr -d '[:space:]' < iostd.txt)"
  fi
  cpldfit -intstyle ise -p "$PART" -optimize density -iostd "$IOSTD" project.ngd
fi

printf 'PHASE hprep6\n'
hprep6 -s IEEE1149 -n project -i project

printf 'PHASE done\n'
