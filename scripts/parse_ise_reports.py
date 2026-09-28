#!/usr/bin/env python3
"""Parse Xilinx ISE 14.7 .srp, .par, and .twr reports."""

import argparse
import json
import os
import re
import sys


def parse_srp(filepath):
    metrics = {"synthesis_time": None, "utilization": {}}
    if not os.path.exists(filepath):
        return {"error": f"File {filepath} not found."}
    content = open(filepath, "r", errors="replace").read()
    synth_time = re.search(r"Total REAL time to Xst completion:\s*(.*)", content)
    if synth_time:
        metrics["synthesis_time"] = synth_time.group(1).strip()
    patterns = {
        "slices_used": r"Number of Slices:\s+(\d+)",
        "slice_registers_used": r"Number of Slice (?:Flip Flops|Registers):\s+(\d+)",
        "luts_used": r"Number of (?:4 input |Slice )?LUTs:\s+(\d+)",
        "ios_used": r"Number of bonded IOBs:\s+(\d+)",
        "bram_used": r"Number of Block RAM/FIFO:\s+(\d+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            metrics["utilization"][key] = int(match.group(1))
    return metrics


def parse_par(filepath):
    metrics = {
        "placer_time": None,
        "router_time": None,
        "total_par_time": None,
        "timing_score": None,
    }
    if not os.path.exists(filepath):
        return {"error": f"File {filepath} not found."}
    content = open(filepath, "r", errors="replace").read()
    placer = re.search(r"Total REAL time to Placer completion:\s*(.*)", content)
    if placer:
        metrics["placer_time"] = placer.group(1).strip()
    router = re.search(r"Total REAL time to Router completion:\s*(.*)", content)
    if router:
        metrics["router_time"] = router.group(1).strip()
    par_total = re.search(r"Total REAL time to PAR completion:\s*(.*)", content)
    if par_total:
        metrics["total_par_time"] = par_total.group(1).strip()
    timing_score = re.search(r"Timing Score:\s*(\d+)", content)
    if timing_score:
        metrics["timing_score"] = int(timing_score.group(1))
    return metrics


def parse_twr(filepath):
    if not filepath or not os.path.exists(filepath):
        return {"error": f"File {filepath} not found."}
    content = open(filepath, "r", errors="replace").read()
    failed = False
    if re.search(r"constraints were not met", content, re.IGNORECASE):
        failed = True
    for match in re.finditer(r"(\d+)\s+timing error", content, re.IGNORECASE):
        if int(match.group(1)) > 0:
            failed = True
    if re.search(r"(\d+)\s+(setup|hold)\s+violation", content, re.IGNORECASE):
        count = re.search(r"(\d+)\s+(setup|hold)\s+violation", content, re.IGNORECASE)
        if count and int(count.group(1)) > 0:
            failed = True
    return {
        "constraints_met": (not failed) and ("All constraints were met" in content or not failed),
        "setup_hold_failure": failed,
    }


def parse_unix_time(filepath):
    if not filepath or not os.path.exists(filepath):
        return None
    values = {}
    for line in open(filepath, "r", errors="replace"):
        parts = line.split()
        if len(parts) == 2 and parts[0] in ("real", "user", "sys"):
            values[parts[0]] = float(parts[1])
    return values or None


def timing_failed(report):
    par = report.get("place_and_route_metrics") or {}
    twr = report.get("static_timing") or {}
    if par.get("timing_score") not in (None, 0):
        return True
    if twr.get("setup_hold_failure"):
        return True
    return False


def build_report(srp_file, par_file, twr_file=None, map_time=None, par_time=None):
    report = {
        "synthesis_metrics": parse_srp(srp_file),
        "place_and_route_metrics": parse_par(par_file),
        "static_timing": parse_twr(twr_file) if twr_file else {},
        "unix_time": {
            "map": parse_unix_time(map_time) if map_time else None,
            "par": parse_unix_time(par_time) if par_time else None,
        },
    }
    report["timing_ok"] = not timing_failed(report)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description="Parse ISE .srp and .par reports")
    parser.add_argument("srp")
    parser.add_argument("par")
    parser.add_argument("--twr")
    parser.add_argument("--map-time")
    parser.add_argument("--par-time")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    report = build_report(args.srp, args.par, args.twr, args.map_time, args.par_time)
    text = json.dumps(report, indent=4)
    if args.out:
        open(args.out, "w").write(text + "\n")
    else:
        print(text)
    return 0 if report["timing_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
