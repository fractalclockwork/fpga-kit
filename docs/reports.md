# Reports

Runs write under `reports/`. That directory is gitignored. Nothing here starts a metrics server. The JSON and JUnit files are the records a later scraper would read.

## Stage record

`reports/<board>/stage.json` is one document updated in place. Each key under `stages` is `present`, `workflow`, or `image`.

```json
{
  "board": "nexys3",
  "stages": {
    "present": {
      "status": "pass",
      "stage": "present",
      "at": "2026-09-26T00:00:00+00:00",
      "device": "Nexys3",
      "idcode": "04002093"
    }
  }
}
```

`status` is `pass` or `fail`. A failure adds `reason`. The image stage, when it passes, also stores `bitstream` and `hil`, the UART records from that programming.

## One build directory

`reports/<board>/<YYYYMMDDTHHMMSSZ>/` is created at the start of `make build` or the image stage. The stamp is UTC.

| File | Written by | Contents |
| --- | --- | --- |
| `progress.json` | Host, while the container runs | Elapsed time, phase, ETA |
| `progress.md` | Same writer | One line: phase, elapsed seconds, ETA. The same line is printed to the terminal |
| `build.log` | Container stdout | ISE log, including `PHASE` lines |
| `map.time`, `par.time` | `time -p` around `map` and `par` | `real`, `user`, `sys` seconds |
| `build_metrics.json` | Parser, after `bitgen` | Utilization, REAL times, timing score |
| `project.bit` | `bitgen` | Bitstream `djtgcfg` programs |
| `hil.jsonl` | Host, after the UART check | One JSON object per exchange |
| `junit.xml` | Same writer | One `testcase` per exchange, or a `failure` |

`progress.json` during the run:

```json
{
  "board": "nexys3",
  "phase": "par",
  "elapsed_s": 40.5,
  "eta_s": 34.5,
  "over_budget": false,
  "phase_durations_s": {
    "xst": 12.0,
    "ngdbuild": 8.0,
    "map": 18.0
  }
}
```

`phase` is `xst`, `ngdbuild`, `map`, `par`, or `bitgen` while the tool is running, then `done` when the container exits 0. `elapsed_s` is wall time from the start of the container. `eta_s` is the remaining estimate: median still left in the current phase, plus the full medians of later phases. Medians come from `phase_seeds_s` in `boards/<id>.yaml` until a board has history, then from `phase_durations_s` in earlier `progress.json` files. `over_budget` is true once the current phase has run longer than its median. On that path `eta_s` is the overrun plus the medians of phases that have not started. The final file adds `exit_code` and sets `eta_s` to 0.

## `build_metrics.json`

```json
{
  "synthesis_metrics": {
    "synthesis_time": "4 secs",
    "utilization": {
      "slices_used": 12,
      "slice_registers_used": 10,
      "luts_used": 20,
      "ios_used": 3
    }
  },
  "place_and_route_metrics": {
    "placer_time": "2 secs",
    "router_time": "9 secs",
    "total_par_time": "12 secs",
    "timing_score": 0
  },
  "static_timing": {},
  "unix_time": {
    "map": {"real": 18.0, "user": 17.2, "sys": 0.4},
    "par": {"real": 40.0, "user": 39.1, "sys": 0.5}
  },
  "timing_ok": true
}
```

Utilization keys are filled from the `.srp` lines that exist. Spartan-6 reports slice registers and slice LUTs. Spartan-3 and Spartan-3E report slice flip-flops and 4-input LUTs. Both land in `slice_registers_used` and `luts_used`. `bram_used` appears when the report has a Block RAM line. The heartbeat does not use block RAM.

`placer_time`, `router_time`, and `total_par_time` are the ISE `Total REAL time` strings. `unix_time` is the host's `time -p` around the same steps. They measure different intervals and are not expected to match to the millisecond.

`timing_ok` is false when `timing_score` is present and not 0, or when `static_timing.setup_hold_failure` is true. `scripts/ise_build.sh` does not run `trce`, so `static_timing` is an error object unless a `.twr` was already in the run directory. The score in the `.par` is the check that stops programming. A false `timing_ok` exits before `djtgcfg`.

## UART records

`hil.jsonl` is one object per line:

```json
{"sent": "PING", "expected": "PONG", "actual": "PONG,nexys3  ,00001A3C", "fpga_cycles": 106556, "host_monotonic_ns": 123456789}
```

`fpga_cycles` is the hex field on the FPGA line, parsed as an integer. `host_monotonic_ns` is the dev-host clock at the moment the record was built. The two clocks are not locked. A difference in `fpga_cycles`, divided by `clock_hz` from `boards/<id>.yaml`, is FPGA time between two lines. The VDEC1 record uses `expected` of `VDEC1,ACK` and `sent` of null.

`junit.xml` is a single `testsuite` named `hil`. Each passing exchange is a `testcase` whose `system-out` is the same JSON object. A timeout or a cycle count that went backwards is a `testcase` with a `failure` element, and that case is not also written as a success line.

Cocotb's own JUnit file, when pytest or the simulator emits one, is `sim/results.xml` on the dev-host. That file is the simulation record. `reports/.../junit.xml` is the hardware record.
