# Documentation

Board pages, lessons, the local archive, and the host-driven hardware-in-the-loop pipeline. The FPGAs are Spartan-3, Spartan-3E, and Spartan-6. The XC2-XL is a CoolRunner-II and XC9500XL CPLD board. The toolchain is Xilinx ISE WebPACK 14.7. Vivado does not support these families. USB programming of the FPGAs uses Digilent Adept 2 (`djtgcfg`).

| Topic | Page |
| --- | --- |
| Boards | [nexys3](boards/nexys3.md), [spartan3e](boards/spartan3e.md), [spartan3](boards/spartan3.md), [vdec1](boards/vdec1.md), [xc2xl](boards/xc2xl.md), [dbb1](boards/dbb1.md), [bss138](boards/bss138.md) |
| Concepts | [Lessons](learn/README.md) |
| Cached manuals and installers | [Archive](../archive/README.md) |
| Bus Blaster v4.1a | [bus-blaster-v4](programmers/bus-blaster-v4.md). Preferred external JTAG. Required for XC9500XL; programs both CPLDs on the XC2-XL |
| JTAG-SMT2 programmer | [jtag-smt2](programmers/jtag-smt2.md). Adept-compatible alternate on Digilent headers. Cannot target XC9500XL |
| Stages, container, and flash | [Pipeline](pipeline.md) |
| JSON and JUnit records | [Reports](reports.md) |

## Supported hardware

| Board id | Target | Clock | Programmer |
| --- | --- | --- | --- |
| `nexys3` | XC6SLX16-CS324 | 100 MHz | Onboard Digilent USB, `djtgcfg -d Nexys3 -i 0`. Alternate: JTAG-SMT2 on header J7, `ADEPT_DEVICE=JtagSmt2` |
| `spartan3e` | XC3S500E-4FG320 | 50 MHz | Onboard USB JTAG, or a JTAG-SMT2 on header J28. `djtgcfg` uses the name `enum` prints |
| `spartan3` | XC3S200-4FT256 | 50 MHz | External Digilent JTAG cable (`JtagHs2`) or a JTAG-SMT2, plus a USB-RS232 adapter |
| `vdec1` | ADV7183B | 27 MHz on the decoder | Daughtercard on the Spartan-3E Hirose FX2 header. The bitstream is the host FPGA's I2C probe |
| `xc2xl` | XC2C256-TQ144 and XC9572XL-VQ44 | 1.8432 MHz socket | Bus Blaster on J1 (`xc3sprog -c bbv2`). CoolRunner `-p 0`, XC9572XL `-p 1`. `make stage` does not take this id |
| `dbb1` | Passive breadboard | Host clock | Plugs into the XC2-XL A/B headers or the Spartan-3 A1, A2, and B1 headers. No bitstream. `make stage` does not take this id |
| `bss138` | Four BSS138 channels | — | Adafruit 757. Low side on the XC2-XL 3.3 V rail, high side on 5 V TTL. `make stage` does not take this id |

The VDEC1 clock is the decoder's oscillator. The probe on the Spartan-3E still runs from that board's 50 MHz clock. Pin tables, IDCODEs, and manual links are on each board page.

## Quick start

Simulation runs on the dev-host. Place-and-route runs in the container, and only after the board has passed the earlier stages. [Pipeline](pipeline.md) is the full gate list. The short path for the first board is:

```bash
make archive
make image
make stage BOARD=nexys3 STAGE=present
make stage BOARD=nexys3 STAGE=workflow
make sim BOARD=nexys3
export HIL_SERIAL=/dev/ttyUSB0
make hil BOARD=nexys3
```

`make archive` downloads public manuals and checks them against the manifest. The ISE tarball and the Adept `.deb` packages are copied into `archive/cache/sdk/` by hand. `make image` builds `xilinx-ise-hil` from those files. `make sim` is Cocotb and Icarus Verilog. `make hil` is the image stage: it simulates again, runs synthesis through `bitgen`, programs the FPGA, and reads the UART. `make build BOARD=nexys3` stops after the timing check and does not call `djtgcfg`.

The Spartan-3E, Spartan-3, and VDEC1 stages stay closed until the Nexys 3 image stage passes. Set `VDEC1_ATTACHED=1` before any VDEC1 stage.

## Lessons

Start at [docs/learn/README.md](learn/README.md).

1. [Logic and LUTs](learn/01-logic-and-luts.md)
2. [Clocks and timing math](learn/02-clocks-and-timing.md)
3. [ISE operation](learn/03-ise-operation.md)
4. [JTAG and configuration](learn/04-jtag-and-configuration.md)
5. [UART](learn/05-uart.md)
6. [Video and I2C](learn/06-video-and-i2c.md)

## Reports

Each image build writes `reports/<board>/<timestamp>/`. While `par` runs, `progress.json` carries `elapsed_s`, the current phase, and `eta_s`. After `bitgen`, `build_metrics.json` holds utilization and the timing score. The UART check appends `hil.jsonl` and `junit.xml`. Field names are in [Reports](reports.md). This repository does not run Prometheus or Grafana. Those files are the records a later dashboard would scrape.
