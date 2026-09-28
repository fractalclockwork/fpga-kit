#!/bin/bash
# Headless CoolRunner-II fit. The host writes project.xst, project.prj,
# and project.ucf into the run directory before starting this script.
set -euo pipefail

RUN="${1:?run directory}"
cd "$RUN"
PART="$(tr -d '[:space:]' < part.txt)"

printf 'PHASE xst\n'
xst -intstyle ise -ifn project.xst

printf 'PHASE ngdbuild\n'
ngdbuild -intstyle ise -uc project.ucf -p "$PART" project.ngc project.ngd

printf 'PHASE cpldfit\n'
cpldfit -intstyle ise -p "$PART" -optimize density -iostd LVCMOS33 project.ngd

printf 'PHASE hprep6\n'
hprep6 -s IEEE1149 -n project -i project

printf 'PHASE done\n'
