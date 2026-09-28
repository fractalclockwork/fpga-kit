#!/bin/bash
# One-time ISE install. CentOS 6 has no usable TTY during docker build, and
# batchxsetup refuses to show the license unless the terminal is tall enough.
set -euo pipefail

if [ -z "${VNC_PASS:-}" ]; then
    echo "VNC_PASS is required" >&2
    exit 1
fi

cat > /etc/yum.repos.d/epel.repo << 'EOF'
[epel]
name=EPEL 6
baseurl=https://archives.fedoraproject.org/pub/archive/epel/6/x86_64/
enabled=1
gpgcheck=0
EOF
yum -y install tigervnc-server xterm xorg-x11-xauth \
    xorg-x11-fonts-misc xorg-x11-fonts-Type1 xdotool expect

mkdir -p /root/.vnc
printf '%s\n' "$VNC_PASS" | vncpasswd -f > /root/.vnc/passwd
chmod 600 /root/.vnc/passwd

# One xterm, no window manager. twm left the keyboard on the root window,
# so Remmina and noVNC never delivered Enter to the license pager.
cat > /root/.vnc/xstartup << 'EOF'
#!/bin/sh
unset SESSION_MANAGER
unset DBUS_SESSION_BUS_ADDRESS
xterm -geometry 100x40+0+0 \
    -xrm 'XTerm*allowSendEvents:true' \
    -e /opt/ise-scripts/run-batch.sh &
sleep 1
id=$(xdotool search --class XTerm | head -n 1 || true)
if [ -n "$id" ]; then
    xdotool windowfocus "$id" || true
fi
wait
EOF
chmod +x /root/.vnc/xstartup

rm -f /tmp/.X1-lock /tmp/.X11-unix/X1
vncserver :1 -geometry 1024x768 -depth 16
echo "VNC is listening on display :1 (port 5901)"
cat /root/.vnc/*.log || true

while [ ! -f /tmp/install-done ] && [ ! -f /tmp/install-failed ]; do
    sleep 5
done

if [ -f /tmp/install-failed ]; then
    echo "installer failed; VNC left running" >&2
    while true; do
        sleep 3600
    done
fi

mkdir -p /root/.Xilinx
if [ -f /tmp/sdk/Xilinx.lic ]; then
    cp /tmp/sdk/Xilinx.lic /root/.Xilinx/Xilinx.lic
    chmod 600 /root/.Xilinx/Xilinx.lic
fi
cp /opt/ise-scripts/entrypoint.sh /entrypoint.sh
chmod +x /entrypoint.sh
rm -rf /tmp/ise
vncserver -kill :1 || true
echo "ISE install is ready to commit"
