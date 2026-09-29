# Spartan-3 starter

The starter kit in UG130. The FPGA is an XC3S200-4FT256, a 200k-gate part, not an XC3S1000 board. ISE WebPACK 14.7 is the SDK, including EDK for a MicroBlaze that uses the onboard SRAM.

Lessons: [logic and LUTs](../learn/01-logic-and-luts.md), [clocks and timing](../learn/02-clocks-and-timing.md), [ISE operation](../learn/03-ise-operation.md), [JTAG](../learn/04-jtag-and-configuration.md), [UART](../learn/05-uart.md).

## Specification

| Item | Value |
| --- | --- |
| FPGA | XC3S200-4FT256, ISE part `xc3s200-4ft256` |
| Clock | 50 MHz Epson oscillator, ball T9, period 20 ns. An auxiliary socket lands on ball D9 |
| IDCODE | `01414093` (revision nibble ignored) |
| JTAG chain | Index 0 is the XC3S200. Index 1 is the XCF02S Platform Flash (2 Mbit). Program index 0 for the bring-up |
| Memory | 1 MB asynchronous SRAM, two ISSI IS61LV25616 devices, usable as one 256K x 32 bank or two 256K x 16 banks |
| Peripherals | VGA, PS/2, RS-232, eight LEDs, four buttons, eight switches, four-digit display |
| Expansion | Three 40-pin headers (A1, A2, B1). A [Breadboard 1](dbb1.md) plugs into these. The XC2-XL ribbon map on that page is verified; the Spartan-3 plugs are not tone-checked yet. No Hirose FX2 and no VHDCI, so a VDEC1 does not mate here |
| Programming | External JTAG header. A Digilent JTAG-USB or JTAG-HS cable, default Adept name `JtagHs2`, or a [JTAG-SMT2](../programmers/jtag-smt2.md) with `ADEPT_DEVICE=JtagSmt2` |
| Serial | DB9 through a MAX3232. The host needs a USB-RS232 adapter. FPGA TXD is ball R13, RXD is ball T13 |

115200 baud, 8N1, 434 clocks per bit.

| Net | Ball | Role |
| --- | --- | --- |
| `clk` | T9 | 50 MHz oscillator |
| `led` | K12 | LD0 |
| `uart_rx` | T13 | RXD from the level shifter |
| `uart_tx` | R13 | TXD to the level shifter |

There is also an auxiliary RS-232 pair on stake pins: RXD-A on N10 and TXD-A on T14. The bring-up uses the DB9 pair.

## SDK and manuals

- ISE WebPACK 14.7, archive id `ise-14.7-lin`
- Adept 2 for the external cable, archive ids `adept-runtime` and `adept-utilities`
- [Resource center](https://digilent.com/reference/spartan-3/spartan-3), schematic and UG130 linked from that page
- [Sell sheet](https://digilent.com/reference/_media/spartan-3:spartan3_ds.pdf), archive id `spartan3-sell-sheet`, includes the board photograph and block diagram
- UG130 v1.2, 20 June 2008, 64 pages, archive id `spartan3-ug130`. This is the board user guide. Digilent's older reference-manual PDF is UG130 v1.1, the same document. Appendix A reprints the board schematics
- Schematic `S3 Board.sch`, 22 Dec 2004, archive id `spartan3-schematic`

## PCB, Gerber, and netlist

The published set is UG130, the eight-page Digilent schematic `S3 Board.sch` (archive id `spartan3-schematic`), and the sell sheet. PCB layout, Gerber, and IPC netlist files were not in those packages. The archive lists zip members if a later download contains them.

## Bring-up

These stages stay closed until the Nexys 3 image stage has passed. See the [pipeline](../pipeline.md).

```bash
make stage BOARD=spartan3 STAGE=present
make stage BOARD=spartan3 STAGE=workflow
make hil BOARD=spartan3
```

Plug in the external JTAG cable before `present`. Point `HIL_SERIAL` at the USB-RS232 adapter on the DB9. `make sim BOARD=spartan3` runs the heartbeat suite on the dev-host.

ChipScope fits poorly in the first pass on this part. The XC3S200 is the smallest FPGA in the set, and a logic-analyzer core plus the UART would spend router time the heartbeat does not need. A later debug bitstream can add it once the UART path is known good.
