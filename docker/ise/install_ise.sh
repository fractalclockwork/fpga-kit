#!/bin/bash
set -euo pipefail

shopt -s nullglob
tars=(/tmp/sdk/*.tar /tmp/sdk/*.tar.gz)
debs=(/tmp/sdk/*.deb)

if [ ${#tars[@]} -eq 0 ]; then
    echo "missing ISE tarball (manifest id ise-14.7-lin)" >&2
    exit 1
fi
if [ ${#debs[@]} -eq 0 ]; then
    echo "missing Adept packages (manifest ids adept-runtime, adept-utilities)" >&2
    exit 1
fi

# The installer expects bash. RHEL 6 already uses bash for /bin/sh.
ln -sf /bin/bash /bin/sh
unset QT_PLUGIN_PATH

mkdir -p /tmp/ise
tar -xf "${tars[0]}" -C /tmp/ise
xsetup="$(find /tmp/ise -type f -path '*/bin/lin64/batchxsetup' | head -n 1)"
if [ -z "$xsetup" ]; then
    xsetup="$(find /tmp/ise -type f -name batchxsetup | head -n 1)"
fi
if [ -z "$xsetup" ]; then
    echo "batchxsetup was not inside the ISE tarball" >&2
    exit 1
fi
# batchxsetup draws the EULA on a terminal and exits if TERM is unset or
# the window is too short to show it. expect supplies a tall pty and answers Y.
if ! command -v expect >/dev/null 2>&1; then
    yum -y install expect
fi
export TERM=xterm
export XSETUP="$xsetup"
expect <<'EOF'
set timeout -1
set stty_init "rows 80 cols 160"
log_user 1
spawn $env(XSETUP) --batch /tmp/headless-install.sh
expect {
    "vertical window size is too small" { exit 2 }
    -re {Press Enter key to continue} {
        send "\r"
        exp_continue
    }
    -re {Enter "Y" to accept or "N" to reject} {
        send "Y\r"
        exp_continue
    }
    eof
}
catch wait result
exit [lindex $result 3]
EOF
# Adept 2.27.9 needs glibc >= 2.23. RHEL 6 has glibc 2.12, so these debs
# stay in the cache for the host djtgcfg tree and are not installed here.
if command -v dpkg >/dev/null 2>&1; then
    dpkg -i "${debs[@]}"
else
    echo "leaving Adept debs uninstalled; djtgcfg runs outside this image" >&2
fi
rm -rf /tmp/ise /tmp/sdk
