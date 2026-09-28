#!/bin/bash
# Build the CentOS 6 base, then install ISE once under VNC and commit
# xilinx-ise-hil. The saved tarball is produced by archive.py --save-image.
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

python=""
if [ -x "$root/.venv/bin/python" ]; then
    python="$root/.venv/bin/python"
else
    python=python3
fi
"$python" scripts/archive.py --require-sdk

if docker image inspect xilinx-ise-hil >/dev/null 2>&1; then
    echo "xilinx-ise-hil already exists. Remove it with docker rmi to install again."
    exit 0
fi

docker build -f docker/ise/Dockerfile -t xilinx-ise-os .

docker rm -f ise-setup ise-novnc >/dev/null 2>&1 || true
docker network create ise-install >/dev/null 2>&1 || true

vnc_pass="$("$python" -c 'import secrets,string; a=string.ascii_letters+string.digits; print("".join(secrets.choice(a) for _ in range(8)))')"
umask 077
printf '%s\n' "$vnc_pass" > /tmp/ise-vnc-pass

docker run -d --name ise-setup --network ise-install \
    -v "$root/archive/cache/sdk:/tmp/sdk:ro" \
    -v "$root/docker/ise:/opt/ise-scripts:ro" \
    -e VNC_PASS="$vnc_pass" \
    xilinx-ise-os \
    bash /opt/ise-scripts/vnc-install.sh

docker run -d --name ise-novnc --network ise-install \
    -p 127.0.0.1:6080:6080 \
    python:3.12-slim \
    bash -lc "pip install -q websockify && python - <<'PY'
import urllib.request, zipfile, io, os
url = 'https://github.com/novnc/noVNC/archive/refs/tags/v1.5.0.zip'
data = urllib.request.urlopen(url, timeout=120).read()
zipfile.ZipFile(io.BytesIO(data)).extractall('/opt')
os.execvp('websockify', ['websockify', '0.0.0.0:6080', 'ise-setup:5901', '--web', '/opt/noVNC-1.5.0'])
PY"

echo "VNC password: ${vnc_pass}"
echo "Open http://127.0.0.1:6080/vnc.html?autoconnect=1&resize=scale&password=${vnc_pass}"
echo "In the xterm, press Enter through each agreement and type Y to accept."

cleanup_novnc() { docker rm -f ise-novnc >/dev/null 2>&1 || true; }
trap cleanup_novnc EXIT

status="$(docker wait ise-setup)"
if [ "$status" != "0" ]; then
    echo "ise-setup exited ${status}" >&2
    docker logs ise-setup >&2 || true
    exit 1
fi

docker commit \
    --change 'ENTRYPOINT ["/entrypoint.sh"]' \
    --change 'WORKDIR /work' \
    ise-setup xilinx-ise-hil
docker rm ise-setup
echo "committed xilinx-ise-hil"
"$python" scripts/archive.py --save-image
