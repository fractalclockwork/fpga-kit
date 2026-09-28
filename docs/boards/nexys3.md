# Nexys 3

Spartan-6 trainer board, retired. The FPGA is an XC6SLX16-CS324. ISE WebPACK 14.7 is the SDK, including EDK when a design grows a MicroBlaze. USB programming is Adept 2.

Lessons: [logic and LUTs](../learn/01-logic-and-luts.md), [clocks and timing](../learn/02-clocks-and-timing.md), [ISE operation](../learn/03-ise-operation.md), [JTAG](../learn/04-jtag-and-configuration.md), [UART](../learn/05-uart.md).

## Specification

| Item | Value |
| --- | --- |
| FPGA | XC6SLX16-CS324, ISE part `xc6slx16-3csg324` |
| Clock | 100 MHz, ball V10, period 10 ns |
| IDCODE | `04002093` (revision nibble ignored) |
| Program | `djtgcfg prog -d Nexys3 -i 0 -f project.bit`. Header J7 is the alternate 6-pin JTAG port for a [JTAG-SMT2](../programmers/jtag-smt2.md) |
| Memory | 16 MB CellularRAM, 16 MB SPI PCM, 16 MB parallel PCM |
| Peripherals | 10/100 Ethernet, 8-bit VGA, USB-UART, USB-HID, eight LEDs, eight switches, five buttons, four-digit display |
| Expansion | 68-pin VHDCI and Pmod ports. This is not a Hirose FX2 host, so a VDEC1 does not mate here |
| Configuration | Volatile over JTAG. BPI or SPI PCM can reload the FPGA at power-on when J8 says so |

The onboard USB-UART is an FTDI bridge. FPGA receive is ball N17 (the FTDI TXD net). FPGA transmit is ball N18. The heartbeat uses 115200 baud, 8N1, and 868 clocks per bit.

| Net | Ball | Role |
| --- | --- | --- |
| `clk` | V10 | 100 MHz oscillator |
| `led` | U16 | LD0, on when high |
| `uart_rx` | N17 | Data from the host |
| `uart_tx` | N18 | Data to the host |

## SDK and manuals

- [ISE WebPACK 14.7](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools/archive-ise.html), archive id `ise-14.7-lin` (manual drop, AMD account)
- [Adept 2](https://digilent.com/reference/software/adept/start), archive ids `adept-runtime` and `adept-utilities`
- [JTAG-SMT2](../programmers/jtag-smt2.md), archive ids `jtag-smt2-manual` and `jtag-smt2-manual-2021`. Set `ADEPT_DEVICE=JtagSmt2` when that module is wired to J7
- [Reference center](https://digilent.com/reference/programmable-logic/nexys-3/start)
- [Reference manual](https://digilent.com/reference/programmable-logic/nexys-3/reference-manual), archive id `nexys3-manual`
- [Schematic Rev B](https://digilent.com/reference/_media/reference/programmable-logic/nexys-3/nexys3_sch.pdf), archive id `nexys3-schematic`
- Product photo on the reference center, archive id `nexys3-photo` when the fetch succeeds

## PCB, Gerber, and netlist

The published schematic package checked for this board is a PDF, not a fabrication zip. PCB layout, Gerber, and IPC netlist files were not in that package. `make archive` records zip members in `archive/cache/status.json` if a later download is a zip, and this page should then link those cached files. Until then the Rev B schematic PDF is the connectivity source. The pin table above is the bring-up subset, taken from the reference manual and the master UCF.

## Bring-up

This board is the first target. Later boards stay closed until its image stage passes. The stage list is in the [pipeline](../pipeline.md).

`present`, `workflow`, and `image` passed on 27 Sep 2026. `djtgcfg` reported device `Nexys3`, serial `210182482566`, and index 0 as `XC6SLX16` IDCODE `44002093` (masked IDCODE `04002093`). The JTAG path is `ready`. BPI, SPI, and the USB stick are `not-run`. `HIL_SERIAL` was unset when workflow ran, so that stage recorded the UART as `not-set`. The image bitstream is the one named in `reports/nexys3/stage.json`.

```bash
make stage BOARD=nexys3 STAGE=present
make stage BOARD=nexys3 STAGE=workflow
make sim BOARD=nexys3
export HIL_SERIAL=/dev/ttyUSB0
make hil BOARD=nexys3
```

`make sim` runs the Cocotb heartbeat on the dev-host. `make build BOARD=nexys3` runs ISE after `workflow` has passed, writes `progress.json` while `par` runs, and stops on `build_metrics.json` without programming. `make hil` is the image stage. It expects `HELLO,nexys3` and a `PONG` on `HIL_SERIAL`. Report fields are in [reports](../reports.md).

ChipScope can be compiled into a later debug bitstream for this Spartan-6. It is not in the heartbeat. It adds cores and router time, and the first test only needs the UART line.
