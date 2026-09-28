# Breadboard 1 (DBB1)

Digilent prototyping accessory, also called the Digilab breadboard. Reference-manual document 502-011, June 9, 2004. Schematic `DlabBB1.sch`, document 500-011, revision C, 30 March 2004. It is a passive board: no programmable part, no JTAG header, and no bitstream. It plugs into the 40-pin expansion headers on the [XC2-XL](xc2xl.md) and the [Spartan-3 starter](spartan3.md).

The same June 2004 sell sheet, document 530-011, also shows the wire-wrap sibling. That sibling replaces the solderless breadboard with a 540-hole wire-wrap field. The connectivity below is the breadboard.

## Specification

| Item | Value |
| --- | --- |
| Function | Pass-through breadboard for Digilab 40-pin headers |
| Breadboard | 540 tie points, symbol BB1, part EIC-501, with power and ground tracks |
| Connectors | Two host plugs and two far-side sockets, plus a test-point header and a prototype header on each side |
| Power | VDD, GND, and VU from the host. J9 is a 2-pin header, pin 1 VDD and pin 2 GND |
| Signals | Every host signal continues to the test points, the prototype header, the breadboard, and the far socket |

Document 502-011 calls the two ends the A and B connectors and the E and F connectors. The schematic draws the same parts as A1–A4 and B1–B4. A1 and B1 face the system board. A2 and B2 are the test points. A3 and B3 are the prototype headers. A4 and B4 are the far sockets, which the sell sheet labels E and F. A second expansion board can plug into A4 and B4, and another DBB1 can stack on those sockets.

UG130 lists the Digilent Breadboard (DBB1) among the boards that plug into the Spartan-3 A1, A2, and B1 headers. The XC2-XL manual lists solderless breadboards among the boards that mate with its 2×20 sockets. On that board, connectors A (J3) and B (J4) are the XC2C256 pair along one edge. Connector C is the XC9572XL and is a separate header.

On schematic symbol A1, pins 1–36 are nets A1–A36, pin 37 is VDD, pin 38 is A38, pin 39 is GND, and pin 40 is VU. Symbol B1 uses B1–B36, VDD, B38, GND, and VU in those same pin positions. A2 is wired pin-for-pin with A1, and B2 is wired pin-for-pin with B1. The host pin tables number the header differently: XC2-XL table 1 and UG130 call pin 1 GND, pin 2 VU, and pin 3 3.3 V. Line the pin-1 marks up when the board is plugged in. The schematic is the name-to-pin drawing for the breadboard itself.

## XC2-XL on A2 and B2

J4, connector B on the XC2C256, is cabled to test-point header A2. J5, connector C on the XC9572XL, is cabled to B2. Pin 1 meets pin 1 on both cables. The silkscreen legend on the A2 header is PA. The pins themselves are numbered 1–40. Pins 1–36 use that same number as the schematic net (pin 5 is net A5). Pins 37–40 keep the schematic net in the table, because those nets are VDD, A38, GND, and VU while the XC2-XL wire on the same pin is still a CPLD I/O.

The 3.3 V rail from J4 is A2 pin 3. The schematic name VDD is A2 pin 37, and that pin is XC2C256 signal B37, not 3.3 V. VU from the wall plug is A2 pin 2.

| A2 pin | Schematic net | J4 signal | XC2C256 pin |
| --- | --- | --- | --- |
| 1 | A1 | GND | — |
| 2 | A2 | VU | — |
| 3 | A3 | VDD33 | — |
| 4 | A4 | B4/GSR | 143 |
| 5 | A5 | B5, `uart_rx` | 142 |
| 6 | A6 | B6, `uart_tx` | 140 |
| 7 | A7 | B7 | 139 |
| 8 | A8 | B8 | 138 |
| 9 | A9 | B9 | 137 |
| 10 | A10 | B10 | 136 |
| 11 | A11 | B11 | 135 |
| 12 | A12 | B12 | 134 |
| 13 | A13 | B13 | 133 |
| 14 | A14 | B14 | 132 |
| 15 | A15 | B15 | 131 |
| 16 | A16 | B16 | 130 |
| 17 | A17 | B17 | 129 |
| 18 | A18 | B18 | 128 |
| 19 | A19 | B19 | 126 |
| 20 | A20 | B20 | 125 |
| 21 | A21 | B21 | 124 |
| 22 | A22 | B22 | 121 |
| 23 | A23 | B23 | 120 |
| 24 | A24 | B24 | 119 |
| 25 | A25 | B25 | 118 |
| 26 | A26 | B26 | 117 |
| 27 | A27 | B27 | 116 |
| 28 | A28 | B28 | 115 |
| 29 | A29 | B29 | 114 |
| 30 | A30 | B30 | 113 |
| 31 | A31 | B31 | 112 |
| 32 | A32 | B32 | 111 |
| 33 | A33 | B33 | 110 |
| 34 | A34 | B34 | 107 |
| 35 | A35 | B35 | 106 |
| 36 | A36 | B36 | 105 |
| 37 | VDD | B37 | 104 |
| 38 | A38 | B38 | 103 |
| 39 | GND | B39 | 102 |
| 40 | VU | B40 | 101 |

B2 is numbered 1–40 the same way for J5. Pin 1 is GND, pin 2 is VU, pin 3 is VDD33, and pin 4 onward follows connector C in XC2-XL table 1, including pin 4 as C4/LD3 and pin 32 as XLCLK. The [BSS138 shifter](bss138.md) uses A2 pins 1, 3, 5, and 6 on the XC2C256 side.

## Manuals

- [Resource center](https://digilent.com/reference/dbb1/dbb1), retired product page
- [Reference manual](https://digilent.com/reference/_media/dbb1/dbb1-rm.pdf), document 502-011, June 9, 2004, one page, archive id `dbb1-manual`
- [Schematic](https://digilent.com/reference/_media/dbb1/dbb1-sch.pdf), `DlabBB1.sch`, document 500-011, revision C, 30 March 2004, one sheet, archive id `dbb1-schematic`
- [Sell sheet](https://digilent.com/reference/_media/dbb1/dbb1-dwr1-brochure.pdf), document 530-011, June 9, 2004, one page, archive id `dbb1-sell-sheet`

Digilent reused document number 502-011 for the FX2 Breadboard manual dated September 26, 2006. The DBB1 file is the June 9, 2004 manual.

## PCB, Gerber, and netlist

The DBB1 resource center publishes the one-page reference manual, the one-page sell sheet, and the one-sheet schematic. PCB layout, Gerber, and IPC netlist files were not in that set.

## Bring-up

This board is outside the FPGA stage order. `make stage` accepts `nexys3`, `spartan3e`, `spartan3`, and `vdec1`. Bring up the host first, with its expansion headers empty. The breadboard carries host pins straight through, including the Spartan-3 configuration pins on A1, A2, and B1, so fit the host bitstream before attaching it.
