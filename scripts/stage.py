#!/usr/bin/env python3
"""Staged bring-up. One target at a time, and only after the previous stage passed."""

import argparse
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from boards import (
    ORDER,
    STAGES,
    load_board,
    primary_image_path,
    read_stages,
    stage_passed,
    write_stage,
)
from identity import chain_has_idcode, idcode_match, parse_enum, parse_init

ROOT_HINT = "Run from the repo root so boards/ and reports/ resolve."


def now():
    return datetime.now(timezone.utc).isoformat()


def fail_record(board, stage, reason, **extra):
    record = {"status": "fail", "stage": stage, "reason": reason, "at": now()}
    record.update(extra)
    write_stage(board["id"], stage, record)
    print(reason, file=sys.stderr)
    return 1


def pass_record(board, stage, **extra):
    record = {"status": "pass", "stage": stage, "at": now()}
    record.update(extra)
    write_stage(board["id"], stage, record)
    print(json.dumps(record, indent=2))
    return 0


def gate(board_id, stage):
    if board_id not in ORDER or stage not in STAGES:
        raise SystemExit(f"unknown target {board_id} {stage}. {ROOT_HINT}")
    if stage != "present" and not stage_passed(board_id, STAGES[STAGES.index(stage) - 1]):
        previous = STAGES[STAGES.index(stage) - 1]
        raise SystemExit(
            f"{board_id} {previous} stage has not passed; refusing {stage}"
        )
    if board_id != "nexys3" and not stage_passed("nexys3", "image"):
        raise SystemExit(
            "nexys3 image stage has not passed; refusing "
            f"{board_id} {stage}"
        )
    board = load_board(board_id)
    if board_id == "vdec1" and not stage_passed("spartan3e", "present"):
        raise SystemExit("spartan3e present stage has not passed; refusing vdec1")
    if board.get("requires_env") and os.environ.get(board["requires_env"]) != "1":
        raise SystemExit(
            f"set {board['requires_env']}=1 before probing {board_id}"
        )
    return board


def adept_root():
    return Path(__file__).resolve().parents[1] / ".tools" / "adept"


def adept_prefix():
    root = adept_root()
    repo = root.parents[1]
    return [
        "docker",
        "run",
        "--rm",
        "--privileged",
        "--network",
        "host",
        "-v",
        "/dev/bus/usb:/dev/bus/usb",
        # djtgcfg receives the host path of project.bit. Mount the repo at
        # the same path so that file is visible inside this helper.
        "-v",
        f"{repo}:{repo}",
        "-v",
        "/lib:/lib:ro",
        "-v",
        "/lib64:/lib64:ro",
        "-v",
        f"{root}/usr/lib64/digilent/adept:/opt/adept:ro",
        "-v",
        f"{root}/usr/share/digilent:/usr/share/digilent:ro",
        "-v",
        f"{root}/etc/digilent-adept.conf:/etc/digilent-adept.conf:ro",
        "-v",
        f"{root}/usr/bin/djtgcfg:/tmp/djtgcfg:ro",
        "-e",
        "LD_LIBRARY_PATH=/opt/adept",
        "ubuntu:latest",
        "/tmp/djtgcfg",
    ]


def run_command(argv, usb=False):
    if argv[0] == "djtgcfg" and shutil.which("djtgcfg") is None:
        # Adept 2.27.9 needs glibc >= 2.23. The ISE image is RHEL 6 (glibc 2.12).
        if (adept_root() / "usr/bin/djtgcfg").is_file():
            argv = adept_prefix() + argv[1:]
        elif docker_image_exists():
            argv = docker_prefix(True) + argv
        else:
            raise SystemExit(
                "djtgcfg is not on PATH and the xilinx-ise-hil image is not built. "
                "Install Adept or run make image after filling archive/cache/sdk/."
            )
    completed = subprocess.run(argv, text=True, capture_output=True)
    return completed.returncode, completed.stdout + completed.stderr


def docker_image_exists():
    completed = subprocess.run(
        ["docker", "image", "inspect", "xilinx-ise-hil"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return completed.returncode == 0


def docker_prefix(usb):
    prefix = ["docker", "run", "--rm"]
    if usb:
        prefix.extend(["--privileged", "-v", "/dev/bus/usb:/dev/bus/usb"])
    prefix.extend(["-v", f"{os.getcwd()}:/work", "-w", "/work", "xilinx-ise-hil"])
    return prefix


def lsusb_text():
    if shutil.which("lsusb") is None:
        return ""
    completed = subprocess.run(["lsusb"], text=True, capture_output=True)
    return completed.stdout


def image_path_report(board, ready_ids):
    report = {}
    for path in board["image_paths"]:
        report[path["id"]] = "ready" if path["id"] in ready_ids else "not-run"
    return report


def adept_override():
    return os.environ.get("ADEPT_DEVICE", "").strip()


def chosen_adept_name(board, devices):
    names = [item["name"] for item in devices]
    override = adept_override()
    if override:
        return override if override in names else ""
    preferred = (board.get("adept_device") or "").strip()
    if preferred and preferred in names:
        return preferred
    if names and (board.get("accept_any_adept_name") or not preferred):
        return names[0]
    return ""


def ready_jtag_paths(board, device_name):
    if device_name == "xilinx-usb":
        return ["jtag-onboard-xilinx"]
    matched = [
        path["id"]
        for path in board.get("image_paths") or []
        if path.get("adept_device") and path["adept_device"] == device_name
    ]
    if matched:
        return matched
    if device_name and any(path["id"] == "jtag" for path in board.get("image_paths") or []):
        return ["jtag"]
    return []


def present_nexys(board, enum_text, init_text):
    devices = parse_enum(enum_text)
    names = [item["name"] for item in devices]
    name = chosen_adept_name(board, devices)
    if not name:
        expected = adept_override() or board["adept_device"]
        return fail_record(
            board,
            "present",
            f"Adept enum did not show {expected}; saw {names or 'no devices'}",
            devices=devices,
        )
    chain = parse_init(init_text)
    match = None
    for device in chain:
        if device["index"] == board["jtag_index"] and device.get("idcode"):
            if idcode_match(device["idcode"], board["idcode"]):
                match = device
    if match is None:
        return fail_record(
            board,
            "present",
            f"index {board['jtag_index']} is not an XC6SLX16 ({board['idcode']})",
            device=name,
            chain=chain,
        )
    return pass_record(
        board,
        "present",
        device=name,
        idcode=match["idcode"],
        chain=chain,
        image_paths=image_path_report(board, []),
    )


def present_adept_chain(board, enum_text, init_text, lsusb):
    devices = parse_enum(enum_text)
    chain = parse_init(init_text)
    match = None
    for device in chain:
        if device.get("index") == board["jtag_index"] and device.get("idcode"):
            if idcode_match(device["idcode"], board["idcode"]):
                match = device
    xilinx = board.get("xilinx_usb_vendor", "")
    onboard = bool(xilinx) and xilinx in lsusb.lower()
    paths = []
    if onboard:
        paths.append("jtag-onboard-xilinx")
    if match is None and not onboard:
        return fail_record(
            board,
            "present",
            f"no {board['device_name']} in the Adept chain and no onboard Xilinx USB device",
            devices=devices,
            chain=chain,
        )
    if match is None and onboard and board["id"] == "spartan3e":
        return pass_record(
            board,
            "present",
            device="xilinx-usb",
            idcode=None,
            chain=chain,
            note="Adept cannot see the onboard programmer. jtag-adept is absent.",
            image_paths=image_path_report(board, paths),
        )
    if match is None:
        return fail_record(
            board,
            "present",
            f"cable chain does not contain {board['device_name']} ({board['idcode']})",
            devices=devices,
            chain=chain,
        )
    name = chosen_adept_name(board, devices)
    if adept_override() and not name:
        return fail_record(
            board,
            "present",
            f"Adept enum did not show {adept_override()}",
            devices=devices,
            chain=chain,
        )
    if not board.get("accept_any_adept_name") and name != board.get("adept_device"):
        return fail_record(
            board,
            "present",
            f"expected Adept name {board['adept_device']}, saw {name}",
            devices=devices,
        )
    paths = ready_jtag_paths(board, name)
    if onboard and "jtag-onboard-xilinx" not in paths:
        paths.append("jtag-onboard-xilinx")
    return pass_record(
        board,
        "present",
        device=name,
        idcode=match["idcode"],
        chain=chain,
        image_paths=image_path_report(board, paths),
    )


def present_vdec1(board):
    # The type check is the ACK line after the probe image loads.
    # present only records that the operator armed the daughtercard and the host passed.
    return pass_record(
        board,
        "present",
        device="ADV7183B",
        idcode=None,
        note="Armed with VDEC1_ATTACHED=1. ACK is checked in the image stage.",
        image_paths=image_path_report(board, []),
    )


def collect_adept(board, runner):
    code, enum_text = runner(["djtgcfg", "enum"])
    if code != 0 and "Found" not in enum_text:
        return code, enum_text, ""
    devices = parse_enum(enum_text)
    device = chosen_adept_name(board, devices)
    init_text = ""
    if device:
        _, init_text = runner(["djtgcfg", "init", "-d", device])
    return code, enum_text, init_text


def run_present(board, runner):
    if board["id"] == "vdec1":
        return present_vdec1(board)
    _code, enum_text, init_text = collect_adept(board, runner)
    if board["id"] == "nexys3":
        return present_nexys(board, enum_text, init_text)
    return present_adept_chain(board, enum_text, init_text, lsusb_text())


def run_workflow(board, runner):
    if board["id"] == "vdec1":
        return pass_record(
            board,
            "workflow",
            tool="fpga-bitbang",
            device="ADV7183B",
            image_paths=image_path_report(board, []),
        )
    present = read_stages(board["id"])["stages"]["present"]
    if present.get("device") == "xilinx-usb":
        return pass_record(
            board,
            "workflow",
            tool="lsusb",
            device="xilinx-usb",
            idcode=None,
            note="Onboard Xilinx USB is present. djtgcfg prog is not used on this path.",
            image_paths=image_path_report(board, ["jtag-onboard-xilinx"]),
        )
    device = present.get("device") or board.get("adept_device")
    code, text = runner(["djtgcfg", "init", "-d", device])
    chain = parse_init(text)
    match = chain_has_idcode(chain, board["idcode"])
    if code != 0 or match is None:
        return fail_record(
            board,
            "workflow",
            f"djtgcfg init -d {device} did not show {board['idcode']}",
            device=device,
            chain=chain,
        )
    serial = {"state": "not-set"}
    port = os.environ.get("HIL_SERIAL")
    if port:
        try:
            import serial

            handle = serial.Serial(port, board["baud"], timeout=0.2)
            handle.close()
            serial = {"state": "open", "port": port, "baud": board["baud"]}
        except Exception as exc:
            serial = {"state": "error", "port": port, "error": str(exc)}
    ready = ready_jtag_paths(board, device)
    return pass_record(
        board,
        "workflow",
        tool="djtgcfg",
        device=device,
        idcode=match["idcode"],
        serial=serial,
        image_paths=image_path_report(board, ready),
    )


def jtag_programmer(board):
    """Cable name djtgcfg should open. A daughtercard has no USB programmer of its own."""
    host_id = board.get("host")
    if host_id:
        host_present = read_stages(host_id)["stages"].get("present") or {}
        name = host_present.get("device")
        if name and name != "xilinx-usb":
            return name
    present = read_stages(board["id"])["stages"].get("present") or {}
    return present.get("device") or board.get("adept_device")


def run_image(board):
    if read_stages(board["id"])["stages"].get("present", {}).get("device") == "xilinx-usb":
        return fail_record(
            board,
            "image",
            "primary Adept path is absent; onboard Xilinx USB is not driven by djtgcfg",
        )
    from flow import build_board
    from hil import run_uart_hil, write_hil_logs

    build_dir = build_board(board["id"])
    bit = build_dir / "project.bit"
    present = read_stages(board["id"])["stages"]["present"]
    device = jtag_programmer(board)
    port = os.environ.get("HIL_SERIAL")
    if not port:
        return fail_record(board, "image", "HIL_SERIAL is required for the image stage", device=device)
    expect = "VDEC1,ACK" if board["id"] == "vdec1" else f"HELLO,{board['uart_name']}"
    early = {}
    listener = None
    if expect.startswith("VDEC1"):
        # The probe prints one line as soon as configuration finishes.
        # Open the UART before djtgcfg returns, or that line is already gone.
        def listen():
            try:
                early["records"] = run_uart_hil(
                    port,
                    board["baud"],
                    board["uart_name"],
                    expect_prefix=expect,
                    timeout_s=90.0,
                )
            except Exception as exc:
                early["error"] = exc

        listener = threading.Thread(target=listen, daemon=True)
        listener.start()
        time.sleep(0.3)
    print(f"{board['id']}  program  {device}", file=sys.stderr, flush=True)
    code, text = run_command(
        ["djtgcfg", "prog", "-d", device, "-i", str(board["jtag_index"]), "-f", str(bit)],
        usb=True,
    )
    if code != 0:
        if listener is not None:
            listener.join(timeout=2)
        detail = next((line.strip() for line in reversed(text.splitlines()) if line.strip()), "")
        if detail:
            print(detail, file=sys.stderr, flush=True)
        return fail_record(board, "image", "djtgcfg prog failed", device=device, output=text[-2000:])
    print(f"{board['id']}  serial  {port}", file=sys.stderr, flush=True)
    try:
        if listener is not None:
            listener.join()
            if "error" in early:
                raise early["error"]
            records = early["records"]
        else:
            records = run_uart_hil(port, board["baud"], board["uart_name"], expect_prefix=expect)
    except Exception as exc:
        write_hil_logs(build_dir, [], failures=[str(exc)])
        return fail_record(board, "image", str(exc), device=device)
    write_hil_logs(build_dir, records)
    return pass_record(
        board,
        "image",
        device=device,
        idcode=present.get("idcode"),
        bitstream=str(bit),
        hil=records,
        image_paths=image_path_report(board, [primary_image_path(board)["id"]]),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run one bring-up stage for one board")
    parser.add_argument("--board", required=True)
    parser.add_argument("--stage", required=True, choices=STAGES)
    args = parser.parse_args(argv)
    board = gate(args.board, args.stage)
    if args.stage == "present":
        return run_present(board, run_command)
    if args.stage == "workflow":
        return run_workflow(board, run_command)
    return run_image(board)


if __name__ == "__main__":
    sys.exit(main())
