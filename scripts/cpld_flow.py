#!/usr/bin/env python3
"""Fit a CoolRunner-II JEDEC file in the ISE container."""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from boards import ROOT, load_board
from project import prepare_run


def docker_cmd(run_dir):
    cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{ROOT}:/work",
        "-w",
        "/work",
    ]
    license_file = ROOT / "archive/cache/sdk/Xilinx.lic"
    if license_file.is_file():
        cmd.extend(["-v", f"{license_file}:/root/.Xilinx/Xilinx.lic:ro"])
    rel = Path("/work") / run_dir.relative_to(ROOT)
    cmd.extend([
        "--entrypoint",
        "/bin/bash",
        "xilinx-ise-hil",
        "/work/docker/ise/entrypoint.sh",
        "stdbuf",
        "-oL",
        "bash",
        "/work/scripts/ise_cpld.sh",
        str(rel),
    ])
    return cmd


def fit(board_id):
    board = load_board(board_id)
    if board.get("kind") != "cpld":
        raise SystemExit(f"{board_id} is not a CPLD board")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "reports" / board_id / stamp
    prepare_run(board_id, run_dir)
    log_path = run_dir / "build.log"
    proc = subprocess.Popen(
        docker_cmd(run_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    assert proc.stdout is not None
    with log_path.open("w") as log:
        for line in proc.stdout:
            log.write(line)
            log.flush()
            print(line, end="", flush=True)
    code = proc.wait()
    jed = run_dir / "project.jed"
    if code != 0 or not jed.is_file():
        raise SystemExit(f"CPLD fit failed, see {log_path}")
    print(jed)
    return jed


def main(argv=None):
    board = "xc2xl"
    if argv:
        board = argv[0]
    fit(board)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
