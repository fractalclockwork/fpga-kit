#!/usr/bin/env python3
"""Run the ISE container and write elapsed-time progress."""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from boards import ROOT, load_board, stage_passed
from parse_ise_reports import build_report
from progress import PHASES, estimate, format_status
from project import prepare_run


def history_for(board_id):
    samples = {phase: [] for phase in PHASES}
    root = ROOT / "reports" / board_id
    if not root.is_dir():
        return samples
    for path in root.glob("*/progress.json"):
        try:
            document = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        for phase, seconds in (document.get("phase_durations_s") or {}).items():
            if phase in samples and isinstance(seconds, (int, float)):
                samples[phase].append(seconds)
    return samples


def write_progress(path, payload):
    path.write_text(json.dumps(payload, indent=2) + "\n")
    summary = format_status(
        payload["board"],
        payload["phase"],
        payload["elapsed_s"],
        payload["eta_s"],
        payload.get("over_budget"),
    )
    (path.parent / "progress.md").write_text(summary + "\n")
    return summary


def last_tool_error(log_path):
    last = None
    for line in log_path.read_text(errors="replace").splitlines():
        if "ERROR:" in line:
            last = line.strip()
    return last


def stream_build(run_dir, board):
    log_path = run_dir / "build.log"
    progress_path = run_dir / "progress.json"
    seeds = board["phase_seeds_s"]
    history = history_for(board["id"])
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
    # The image entrypoint sources settings64.sh while $1 is still Docker's
    # command, and that script treats $1 as the install prefix. Use the repo
    # entrypoint, which clears positional parameters before sourcing it.
    cmd.extend([
        "--entrypoint",
        "/bin/bash",
        "xilinx-ise-hil",
        "/work/docker/ise/entrypoint.sh",
        "stdbuf",
        "-oL",
        "bash",
        "/work/scripts/ise_build.sh",
        str(Path("/work") / run_dir.relative_to(ROOT)),
    ])
    start = time.monotonic()
    phase = "xst"
    phase_started = start
    durations = {}
    announced = {"phase": None, "at": 0.0}

    def echo(payload):
        now = time.monotonic()
        changed = payload["phase"] != announced["phase"]
        if not changed and now - announced["at"] < 5:
            return
        announced["phase"] = payload["phase"]
        announced["at"] = now
        print(
            format_status(
                payload["board"],
                payload["phase"],
                payload["elapsed_s"],
                payload["eta_s"],
                payload.get("over_budget"),
            ),
            file=sys.stderr,
            flush=True,
        )

    def snapshot(current):
        elapsed_total = time.monotonic() - start
        elapsed_phase = time.monotonic() - phase_started
        if current in PHASES:
            eta, over = estimate(seeds, history, current, elapsed_phase)
        else:
            eta, over = 0, False
        return {
            "board": board["id"],
            "phase": current,
            "elapsed_s": round(elapsed_total, 3),
            "eta_s": round(eta, 3),
            "over_budget": over,
            "phase_durations_s": {key: round(value, 3) for key, value in durations.items()},
        }

    echo(snapshot(phase))
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    log = log_path.open("w")
    assert proc.stdout is not None
    for line in proc.stdout:
        log.write(line)
        log.flush()
        text = line.strip()
        if text.startswith("PHASE "):
            new_phase = text.split()[1]
            if phase in PHASES:
                durations[phase] = time.monotonic() - phase_started
            phase = new_phase
            phase_started = time.monotonic()
        if phase not in PHASES:
            continue
        payload = snapshot(phase)
        write_progress(progress_path, payload)
        echo(payload)
    code = proc.wait()
    log.close()
    if phase in PHASES:
        durations[phase] = time.monotonic() - phase_started
    payload = snapshot("done" if code == 0 else phase)
    payload["eta_s"] = 0
    payload["over_budget"] = False
    payload["exit_code"] = code
    write_progress(progress_path, payload)
    echo(payload)
    if code != 0:
        error = last_tool_error(log_path)
        if error:
            print(error, file=sys.stderr, flush=True)
        raise SystemExit(f"ISE build failed, see {log_path}")
    return progress_path


def find_report(run_dir, suffix):
    matches = list(run_dir.glob(f"*{suffix}"))
    return matches[0] if matches else run_dir / f"project{suffix}"


def require_sim(board_id):
    """Cocotb must pass before the container is allowed to place and route."""
    sim_board = "vdec1" if board_id == "vdec1" else "nexys3"
    env = os.environ.copy()
    extra = [ROOT / ".venv" / "bin", ROOT / ".tools" / "usr" / "bin"]
    prefix = [str(path) for path in extra if path.is_dir()]
    if prefix:
        env["PATH"] = os.pathsep.join(prefix + [env.get("PATH", "")])
    result = subprocess.run(["make", "sim", f"BOARD={sim_board}"], cwd=ROOT, env=env)
    if result.returncode != 0:
        raise SystemExit("simulation failed; refusing place-and-route")


def build_board(board_id, require_gate=True):
    if require_gate and not stage_passed(board_id, "workflow"):
        raise SystemExit(f"{board_id} workflow stage has not passed; refusing the image build")
    board = load_board(board_id)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = ROOT / "reports" / board_id / stamp
    prepare_run(board_id, run_dir)
    if os.environ.get("FPGA_KIT_SKIP_DOCKER") == "1":
        return run_dir
    require_sim(board_id)
    if subprocess.run(
        ["docker", "image", "inspect", "xilinx-ise-hil"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    ).returncode != 0:
        raise SystemExit("container image xilinx-ise-hil is not built. Run make image after caching the SDK.")
    stream_build(run_dir, board)
    report = build_report(
        str(find_report(run_dir, ".srp")),
        str(find_report(run_dir, ".par")),
        str(find_report(run_dir, ".twr")),
        str(run_dir / "map.time"),
        str(run_dir / "par.time"),
    )
    metrics = run_dir / "build_metrics.json"
    metrics.write_text(json.dumps(report, indent=4) + "\n")
    if not report["timing_ok"]:
        raise SystemExit(f"timing check failed, see {metrics}")
    return run_dir


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build one board in the ISE container")
    parser.add_argument("--board", required=True)
    args = parser.parse_args(argv)
    print(build_board(args.board))
    return 0


if __name__ == "__main__":
    sys.exit(main())
