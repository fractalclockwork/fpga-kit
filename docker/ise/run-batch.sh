#!/bin/bash
# Runs inside the VNC xterm. The batch file selects WebPACK and /opt/Xilinx.
set -u

echo "Extracting the ISE tarball. This takes a few minutes."
shopt -s nullglob
tars=(/tmp/sdk/*.tar /tmp/sdk/*.tar.gz)
if [ ${#tars[@]} -eq 0 ]; then
    echo "missing ISE tarball (manifest id ise-14.7-lin)" >&2
    touch /tmp/install-failed
    exec bash
fi

xsetup="$(find /tmp/ise -type f -path '*/bin/lin64/batchxsetup' 2>/dev/null | head -n 1 || true)"
if [ -z "$xsetup" ]; then
    mkdir -p /tmp/ise
    tar -xf "${tars[0]}" -C /tmp/ise
    xsetup="$(find /tmp/ise -type f -path '*/bin/lin64/batchxsetup' | head -n 1)"
fi
if [ -z "$xsetup" ]; then
    echo "batchxsetup was not inside the ISE tarball" >&2
    touch /tmp/install-failed
    exec bash
fi

echo
echo "Page through each agreement with Enter."
echo "Type Y when asked to accept. The batch file leaves cable drivers off."
echo

# The license pager reads the tty. Browser key events are not arriving,
# so expect answers Enter and Y on the installer's pty.
export TERM=xterm
export XSETUP="$xsetup"
expect << 'EOF'
set timeout 8
log_user 1
set stalls 0
spawn $env(XSETUP) --batch /opt/ise-scripts/headless-install.sh
expect {
    "vertical window size is too small" { exit 2 }
    -re {Press Enter key to continue} {
        set stalls 0
        send "\r"
        exp_continue
    }
    -re {Enter "Y" to accept or "N" to reject} {
        set stalls 0
        send "Y\r"
        exp_continue
    }
    -re {batch mode} {
        set timeout -1
        exp_continue
    }
    timeout {
        incr stalls
        if {$stalls > 40} { exit 3 }
        send "\r"
        exp_continue
    }
    eof
}
catch wait result
set code [lindex $result 3]
if {$code eq ""} { exit 0 }
exit $code
EOF
status=$?
echo "batchxsetup exit ${status}"
if [ "$status" -eq 0 ]; then
    touch /tmp/install-done
    echo "Install finished. Packaging continues on the host."
else
    touch /tmp/install-failed
    echo "Install failed. Leave this window open."
fi
exec bash
