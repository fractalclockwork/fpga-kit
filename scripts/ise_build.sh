#!/bin/bash
# Headless ISE flow. The host writes project.xst, project.prj, and project.ucf
# into the run directory before starting this script.
set -euo pipefail

RUN="${1:?run directory}"
cd "$RUN"
PART="$(tr -d '[:space:]' < part.txt)"

printf 'PHASE xst\n'
xst -intstyle ise -ifn project.xst

printf 'PHASE ngdbuild\n'
ngdbuild -intstyle ise -uc project.ucf -p "$PART" project.ngc project.ngd

printf 'PHASE map\n'
/usr/bin/time -p -o map.time map -intstyle ise -p "$PART" -w -o project_map.ncd project.ngd project.pcf

printf 'PHASE par\n'
/usr/bin/time -p -o par.time par -w -intstyle ise project_map.ncd project.ncd project.pcf

printf 'PHASE bitgen\n'
bitgen -w -g Binary:no -g StartupClk:JtagClk project.ncd project.bit

printf 'PHASE done\n'
