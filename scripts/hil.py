#!/usr/bin/env python3
"""Host UART check after a primary image transfer."""

import argparse
import json
import time
import xml.sax.saxutils as xml_escape
from pathlib import Path


def hil_record(sent, expected, actual, fpga_cycles, host_monotonic_ns):
    return {
        "sent": sent,
        "expected": expected,
        "actual": actual,
        "fpga_cycles": fpga_cycles,
        "host_monotonic_ns": host_monotonic_ns,
    }


def parse_line(line, uart_name):
    parts = [item.strip() for item in line.strip().split(",")]
    if len(parts) < 2:
        return None
    cycles = None
    if len(parts) >= 3:
        try:
            cycles = int(parts[-1], 16)
        except ValueError:
            cycles = None
    return {"tag": parts[0], "name": parts[1], "fpga_cycles": cycles, "raw": line.strip()}


def run_uart_hil(port, baud, uart_name, expect_prefix, timeout_s=5.0, opener=None):
    if opener is None:
        import serial

        opener = lambda: serial.Serial(port, baud, timeout=0.2)
    handle = opener()
    records = []
    deadline = time.monotonic() + timeout_s
    hello = None
    try:
        if not str(expect_prefix).startswith("VDEC1"):
            while time.monotonic() < deadline and hello is None:
                raw = handle.readline().decode("ascii", errors="replace").lstrip("\x00")
                parsed = parse_line(raw, uart_name)
                if parsed and parsed["raw"].startswith("HELLO") and uart_name in parsed["raw"]:
                    hello = parsed
            if hello is None:
                raise TimeoutError(f"no HELLO line for {uart_name} on {port}")
        if str(expect_prefix).startswith("HELLO"):
            handle.write(b"PING\n")
            pong = None
            while time.monotonic() < deadline and pong is None:
                raw = handle.readline().decode("ascii", errors="replace").lstrip("\x00")
                parsed = parse_line(raw, uart_name)
                if parsed and parsed["tag"] == "PONG":
                    pong = parsed
            if pong is None:
                raise TimeoutError("no PONG after PING")
            if hello and pong["fpga_cycles"] is not None and hello["fpga_cycles"] is not None:
                if pong["fpga_cycles"] < hello["fpga_cycles"]:
                    raise AssertionError("FPGA cycle count went backwards")
            records.append(
                hil_record(
                    "PING",
                    "PONG",
                    pong["raw"],
                    pong["fpga_cycles"],
                    time.monotonic_ns(),
                )
            )
        else:
            ack = None
            while time.monotonic() < deadline and ack is None:
                raw = handle.readline().decode("ascii", errors="replace").lstrip("\x00")
                if raw.startswith("VDEC1,ACK"):
                    ack = parse_line(raw, uart_name)
            if ack is None:
                raise TimeoutError("VDEC1 did not ACK")
            records.append(
                hil_record(
                    None,
                    "VDEC1,ACK",
                    ack["raw"],
                    ack["fpga_cycles"],
                    time.monotonic_ns(),
                )
            )
    finally:
        handle.close()
    return records


def write_hil_logs(directory, records, failures=None):
    """JSON lines plus JUnit XML for one image-stage UART exchange."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "hil.jsonl").write_text("".join(json.dumps(record) + "\n" for record in records))
    failures = failures or []
    cases = []
    for record in records:
        name = xml_escape.escape(str(record.get("expected") or "vector"))
        body = xml_escape.escape(json.dumps(record))
        cases.append(
            f'  <testcase classname="hil" name="{name}">\n'
            f"    <system-out>{body}</system-out>\n"
            f"  </testcase>"
        )
    for message in failures:
        text = xml_escape.escape(str(message))
        cases.append(
            f'  <testcase classname="hil" name="hil">\n'
            f'    <failure message="{text}">{text}</failure>\n'
            f"  </testcase>"
        )
    document = (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        f'<testsuite name="hil" tests="{len(cases)}" failures="{len(failures)}">\n'
        + "\n".join(cases)
        + "\n</testsuite>\n"
    )
    (directory / "junit.xml").write_text(document)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Read a heartbeat from a serial port")
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=115200)
    parser.add_argument("--name", required=True)
    parser.add_argument("--expect", default=None)
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    expect = args.expect or f"HELLO,{args.name}"
    records = run_uart_hil(args.port, args.baud, args.name, expect)
    text = json.dumps(records, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
