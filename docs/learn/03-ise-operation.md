# ISE operation

ISE WebPACK 14.7 is a chain of programs. Each one reads the previous file and writes the next. The container runs them headless, in this order.

| Step | Reads | Writes | What it decides |
| --- | --- | --- | --- |
| `xst` | Verilog, part name | `.ngc`, `.srp` | LUTs, flip-flops, and the synthesis REAL time |
| `ngdbuild` | `.ngc`, UCF | `.ngd` | Which top-level port is which package ball |
| `map` | `.ngd` | `*_map.ncd`, `.pcf` | Which slice sites can hold that logic |
| `par` | mapped `.ncd`, `.pcf` | routed `.ncd`, `.par` | Where each slice sits and which wires connect them |
| `bitgen` | routed `.ncd` | `.bit` | The configuration frames the FPGA will load |

`scripts/ise_build.sh` stops at `bitgen`. It does not run `trce`. The timing score the gate uses is the one in the `.par`. The parser still reads a `.twr` when the run directory already contains one, and a setup or hold failure in that file fails the build the same way a non-zero score does.

## Why `par` dominates

Mapping is mostly a packing problem. Routing is a search over a large graph, and the ISE router uses one CPU. A heartbeat finishes in minutes. A design that fills the XC3S200 or asks for a tight 10 ns period can sit in the router much longer, and watching `top` will show one busy core. That is the step the progress file is for.

The dev-host tails the build log and writes `reports/<board>/<timestamp>/progress.json`:

- `elapsed_s` since the flow started
- `phase`, one of `xst`, `ngdbuild`, `map`, `par`, `bitgen`
- `eta_s`, the estimated seconds still to go
- `over_budget`, set when the phase has already run longer than its median

Until a board has a history, the medians are the seeds in `boards/<id>.yaml`. After the first successful run, the median of each phase in earlier `progress.json` files replaces the seed. Time left in the current phase is the median minus the time already spent in it. Later phases contribute their full medians. If the current phase passes its median, `eta_s` becomes the overrun plus the medians of the phases that have not started, and `over_budget` is true.

## Two clocks for the same run

Unix `time -p` wraps `map` and `par` and records wall-clock seconds. ISE also prints its own strings:

- `Total REAL time to Xst completion`
- `Total REAL time to Placer completion`
- `Total REAL time to Router completion`
- `Total REAL time to PAR completion`

Those REAL lines are the tool's account of itself. `time -p` is the dev-host's account, including process startup. Both go into `build_metrics.json`. They will not match to the millisecond. A large gap means the process was stalled outside the tool, often on a cold disk cache or a container that was still paging the ISE libraries in.

## When the build is allowed to flash

`bitgen` must finish, the timing score in the `.par` must be 0, and the `.twr` must not report a setup or hold failure. Then the host may call `djtgcfg`. The lesson on [JTAG](04-jtag-and-configuration.md) is what that call does.
