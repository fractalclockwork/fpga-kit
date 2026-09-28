#!/bin/bash
set -e
unset LANG
unset QT_PLUGIN_PATH
# settings64.sh treats $1 as the install prefix. Docker passes the command
# in $1, so clear the positional parameters while the script is sourced.
ise_args=("$@")
set --
# shellcheck disable=SC1091
. /opt/Xilinx/14.7/ISE_DS/settings64.sh
set -- "${ise_args[@]}"

# System directories first, then the paths settings64.sh added, so awk is
# the system binary. RHEL 6 keeps its libraries in lib64.
system_libs="/usr/lib64:/lib64:/usr/lib:/lib"
if [ -n "${LD_LIBRARY_PATH:-}" ]; then
    LD_LIBRARY_PATH="${system_libs}:${LD_LIBRARY_PATH}"
else
    LD_LIBRARY_PATH="${system_libs}"
fi
export LD_LIBRARY_PATH

shopt -s nullglob
licenses=("${HOME}/.Xilinx/"*.lic)
if [ "${#licenses[@]}" -gt 0 ]; then
    export XILINXD_LICENSE_FILE="${licenses[0]}"
fi

cd /work
exec "$@"
