# Bus Blaster v4.1a

Dangerous Prototypes high-speed JTAG debugger, hardware revision v4.1a. The design overview, last modified 21 March 2014, is archive id `bus-blaster-v41a-manual`. The one-sheet drawing, title `BusBlasterv4.1a`, dated 21 March 2014 at 4:19:50 PM, is archive id `bus-blaster-v41a-schematic`. Both are CC BY-SA.

An FT2232H speaks high-speed USB. A CoolRunner-II XC2C64A in VQ100 is the buffer between that chip, at 3.3 V, and a target whose JTAG bank is 1.5 V to 3.3 V. The buffer image is what makes the cable look like a JTAGkey, a KT-link, or another FT2232 debugger to OpenOCD and urJTAG. This is the preferred external JTAG cable on this bench: it is required for XC9500XL, and it programs both CPLDs on the [XC2-XL](../boards/xc2xl.md). Digilent Adept (`djtgcfg`) does not drive it; use `xc3sprog -c bbv2`. The [JTAG-SMT2](jtag-smt2.md) remains an Adept alternate on Digilent headers but cannot target XC9500XL.

## Specification

| Item | Value |
| --- | --- |
| USB | FT2232H (U2), LQFP-64, mini-B jack. 12 MHz crystal, 27 pF load capacitors. 93LC46B EEPROM (U6) |
| Buffer | XC2C64A CoolRunner-II (U3), VQ100. Core is 1.8 V from the FT2232H. I/O banks split between the FT2232H at 3.3 V and the target |
| Target I/O | 1.5 V to 3.3 V on VTG. 5 V on that pin is outside the range the design overview allows |
| Series resistors | 82 Ω on the JTAG header signals |
| Level switch | Two 4066 analog switches (U4, U5) steer the FT2232H secondary channel |
| Regulator | LD1117-3.3 (U1), SOT-223 |
| Board | DP9056, 90 mm × 56 mm. Schematic sheet 1 of 1. Document number and revision fields are blank |
| Header | Shrouded 2×10, 0.1 in, ARM JTAG order |
| Extra I/O | JP1 and JP2, each 1×13, carry spare CPLD pins |

The manufacturing page's urJTAG scan of the buffer prints IDCODE `06E5C093`, the XC2C64A. v4 buffer logic does not run on a v2 or v3 board, and a v2 or v3 image does not run on v4. The usual load for this cable is the JTAGkey buffer.

## 20-pin header

Pin 1 is V_TARGET. R7, 0 Ω, joins that net to VTG. C22, 4.7 µF, sits on the target side. D1 is marked do not populate. Even pins from 4 through 20 are ground.

| Pin | Signal | Pin | Signal |
| --- | --- | --- | --- |
| 1 | V_TARGET | 2 | VTG |
| 3 | TRST | 4 | GND |
| 5 | TDI | 6 | GND |
| 7 | TMS | 8 | GND |
| 9 | TCK | 10 | GND |
| 11 | RTCK | 12 | GND |
| 13 | TDO | 14 | GND |
| 15 | TSRST | 16 | GND |
| 17 | DBGRQ | 18 | GND |
| 19 | DBGACK | 20 | GND |

With the JTAGkey buffer, the FT2232H pins on the main channel are TCK on ADBUS0, TDI on ADBUS1, TDO on ADBUS2, TMS on ADBUS3, and RTCK on ADBUS7. ADBUS4 is the output-enable for those drivers. TRST, TSRST, DBGRQ, and DBGACK are buffer pins. The design overview lists them as reset output, bidirectional reset, debug request, and debug acknowledge.

## JP4 and MODE

JP4 is 1×2. Pin 1 is the onboard 3.3 V rail. The schematic note calls that position Bus-Pwr 3.3V. Pin 2 is VTG. The note calls the open position Self-Pwr 1.5~3.3V. A jumper ties the buffer supply, and pin 1 through R7, to the Bus Blaster's 3.3 V. The design overview prints 200 mA as the maximum into the target in the CPLD section, and 100 mA at 3.3 V in the pinout section. With the jumper off, the target feeds pin 1 and the buffer follows that rail.

MODE is 1×3. The center pin is 3.3 V. The schematic note names the two ends Normal and Update Buffer, and each end has a 10 kΩ pull-down. Update Buffer connects the FT2232H secondary channel to the XC2C64A JTAG port so the host can load a new buffer. Normal connects that channel to the CPLD pins used for the serial-wire viewer UART. v2 and v3 used the secondary channel only for buffer updates. v4 added the 4066 pair so the same channel can carry viewer traffic after the jumper moves back to Normal.

## Digilent 6-pin JTAG

These boards' external headers use Digilent's 6-pin 3.3 V order. Document 500-028 and the XC2-XL schematic label that connector J1. The Nexys 3 schematic labels the same order on J7. Digilent and Xilinx name that plug for the Digilent JTAG3 and the Parallel-III or Parallel-IV cable. The Bus Blaster plug is the 20-pin ARM header above. The pin numbers do not match. Wire by signal name.

| Digilent pin | Signal | Bus Blaster pin |
| --- | --- | --- |
| 1 | TMS | 7 |
| 2 | TDI | 5 |
| 3 | TDO | 13 |
| 4 | TCK | 9 |
| 5 | GND | 4 |
| 6 | VCC 3.3 V | 1 |

That table is the cable used on the XC2-XL. Imaging that board confirmed it: both CPLDs answered, and JEDEC loads wrote correctly. Any even Bus Blaster pin from 4 through 20 is ground; pin 4 is the usual pick. Leave TRST, RTCK, TSRST, DBGRQ, and DBGACK open. Those nets are not on the Digilent six-pin header.

JP4 is in the Bus-Pwr position so Bus Blaster pin 1 is the onboard 3.3 V rail into Digilent pin 6. That rail sets the buffer level and feeds the board's JTAG VCC pin. MODE stays on Normal. The buffer image is the usual JTAGkey load.

With JP4 open, Digilent pin 6 has to feed Bus Blaster pin 1 from the board's 3.3 V instead. The Self-Pwr range is still 1.5 V to 3.3 V.

## XC2-XL

On the [XC2-XL](../boards/xc2xl.md) J1 uses the Digilent 6-pin table above. That wiring is confirmed: with both devices in the chain, `xc3sprog -c bbv2` sees the XC2C256 at `-p 0` (IDCODE `06d4c093`) and the XC9572XL at `-p 1` (IDCODE `49604093`), and JEDEC loads write. Use this cable for both parts. Do not use the JTAG-SMT2 on this board going forward: the 2021 SMT2 manual says that module cannot target an XC9500XL, so a second cable would still be required for the XL.

## Manuals

- [Bus Blaster v4 design overview](http://dangerousprototypes.com/docs/Bus_Blaster_v4_design_overview), last modified 21 March 2014, archive id `bus-blaster-v41a-manual`. The live host answers 403. The [Wayback Machine](https://web.archive.org/web/20251028154626/http://dangerousprototypes.com/docs/Bus_Blaster_v4_design_overview) holds the page as HTML, captured 28 October 2025, and has no PDF of it. The cached file is that capture printed to PDF, with the figures from the same crawl. The row is manual, so `make archive` hashes it and does not fetch it again
- Schematic `BusBlasterv4.1a`, sheet 1 of 1, 21 March 2014, archive id `bus-blaster-v41a-schematic`. Wayback stores the drawing as a PNG, captured 13 January 2025. The cached file is a one-page PDF of the full-resolution sheet `BusBlasterv4.1a.sch.png` from the hardware repository, the same drawing. The row is manual
- [Bus Blaster project page](http://dangerousprototypes.com/docs/Bus_Blaster), the page the design overview calls the manual. It covers v1 through v4
- [Hardware repository](https://github.com/DangerousPrototypes/Bus_Blaster), CC BY-SA

## PCB and Gerber

The GitHub tree publishes `hardware/BusBlasterv4.1a-gerber.zip`. The members are `BusBlasterv4.1a.GBL`, `.GBO`, `.GBS`, `.GTL`, `.GTO`, `.GTS`, and `.TXT`. An IPC netlist is not in that zip. The Eagle board file `BusBlasterv4.1a.brd` sits next to the schematic and is not cached. The one-sheet drawing is the connectivity source.
