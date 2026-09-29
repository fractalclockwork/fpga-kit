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

On schematic symbol A1, pins 1–36 are nets A1–A36, pin 37 is VDD, pin 38 is A38, pin 39 is GND, and pin 40 is VU. Symbol B1 uses B1–B36, VDD, B38, GND, and VU in those same pin positions. A2 is wired pin-for-pin with A1, and B2 is wired pin-for-pin with B1. The host pin tables (XC2-XL table 1, UG130) call Digilent pin 1 GND, pin 2 VU, and pin 3 3.3 V. On the XC2-XL the ribbon to A2/B2 is end-reversed relative to those Digilent numbers — see below. The Spartan-3 starter plug map is not tone-checked yet.

## XC2-XL on A2 and B2

**Status:** Digilent socket numbering and the J4→A2 / J3→B2 ribbon map are verified with octave tones. The same ribbon habit is expected on J5→B2 once that CPLD is driven. Spartan-3 A1/A2/B1 on this breadboard is still unchecked.

J4 (connector B, XC2C256) goes to test-point header A2 (silk PA). J3 (connector A) was used on B2 (silk PB) for the far-end check; stock docs also put J5 (XC9572XL) on B2. Pins 1–36 are PAx / PBx; 37–40 are silk VDD, PA38/PB38, GND, and VV.

Digilent numbering on the XC2-XL sockets themselves is correct: J3-5 / J4-5 / J6-5 = 1 kHz, J3-7 / J4-7 = 4 kHz with pin `n` driven at `1 kHz × 2^(n−5)`.

The ribbon is **not** Digilent pin-1 to silk-1. Near end (Digilent 5/6/7):

| Digilent | Tone | A2 (J4) | B2 (PB) |
| --- | --- | --- | --- |
| 5 | 1 kHz | PA35 | PB35 |
| 6 | 2 kHz | PA36 | PB36 |
| 7 | 4 kHz | PA33 | PB34 |

Far end (Digilent 39/40/37/38 driven at 1/2/4/8 kHz) checked out on both cables:

| Digilent | Tone | A2 / B2 silk |
| --- | --- | --- |
| 39 | 1 kHz | PA1 / PB1 |
| 40 | 2 kHz | PA2 / PB2 |
| 37 | 4 kHz | PA3 / PB3 |
| 38 | 8 kHz | PA4 / PB4 |

For J4→A2 the closed form is: odd Digilent `n` → A2 `40-n`, even Digilent `n` → A2 `42-n` (pairs `(1,2)→(GND,VV)`, `(3,4)→(VDD,PA38)`, `(5,6)→(PA35,PA36)`, … `(39,40)→(PA1,PA2)`). Digilent pin 7 was PA33 on A2 and PB34 on B2 — do not assume pin 7+ is identical across the two ribbons. Rails: silk **GND** = Digilent 1, **VV** = Digilent 2 (VU), **VDD** = Digilent 3 (3.3 V). Silk PA1/PA3 are Digilent 39/37 (I/O), not those rails.

| A2 silk | Digilent J4 | J4 signal | XC2C256 pin |
| --- | --- | --- | --- |
| 39 (GND) | 1 | GND | — |
| 40 (VV) | 2 | VU | — |
| 37 (VDD) | 3 | VDD33 | — |
| 38 (PA38) | 4 | B4/GSR | 143 |
| 35 (PA35) | 5 | B5, `uart_rx` | 142 |
| 36 (PA36) | 6 | B6, `uart_tx` | 140 |
| 33 (PA33) | 7 | B7 | 139 |
| 34 (PA34) | 8 | B8 | 138 |
| 31 (PA31) | 9 | B9 | 137 |
| 32 (PA32) | 10 | B10 | 136 |
| 29 (PA29) | 11 | B11 | 135 |
| 30 (PA30) | 12 | B12 | 134 |
| 27 (PA27) | 13 | B13 | 133 |
| 28 (PA28) | 14 | B14 | 132 |
| 25 (PA25) | 15 | B15 | 131 |
| 26 (PA26) | 16 | B16 | 130 |
| 23 (PA23) | 17 | B17 | 129 |
| 24 (PA24) | 18 | B18 | 128 |
| 21 (PA21) | 19 | B19 | 126 |
| 22 (PA22) | 20 | B20 | 125 |
| 19 (PA19) | 21 | B21 | 124 |
| 20 (PA20) | 22 | B22 | 121 |
| 17 (PA17) | 23 | B23 | 120 |
| 18 (PA18) | 24 | B24 | 119 |
| 15 (PA15) | 25 | B25 | 118 |
| 16 (PA16) | 26 | B26 | 117 |
| 13 (PA13) | 27 | B27 | 116 |
| 14 (PA14) | 28 | B28 | 115 |
| 11 (PA11) | 29 | B29 | 114 |
| 12 (PA12) | 30 | B30 | 113 |
| 9 (PA9) | 31 | B31 | 112 |
| 10 (PA10) | 32 | B32 | 111 |
| 7 (PA7) | 33 | B33 | 110 |
| 8 (PA8) | 34 | B34 | 107 |
| 5 (PA5) | 35 | B35 | 106 |
| 6 (PA6) | 36 | B36 | 105 |
| 3 (PA3) | 37 | B37 | 104 |
| 4 (PA4) | 38 | B38 | 103 |
| 1 (PA1) | 39 | B39 | 102 |
| 2 (PA2) | 40 | B40 | 101 |

UART on the CoolRunner uses A2 **PA35** / **PA36**, with LV on silk **VDD** and return on silk **GND**. See [BSS138](bss138.md).

## Spartan-3 starter

UG130 puts the DBB1 on headers A1, A2, and B1. That host uses the same style of 40-pin Digilent numbering (pin 1 GND, pin 2 VU, pin 3 3.3 V), but the ribbon orientation on this bench is **not** tone-validated yet. Until it is, do not assume the XC2-XL end-reversed PA/PB table applies to the Spartan-3 plugs. Re-run the octave check (Digilent 5/6/7 and 39/40/37/38) after the board is up.

## Manuals

- [Resource center](https://digilent.com/reference/dbb1/dbb1), retired product page
- [Reference manual](https://digilent.com/reference/_media/dbb1/dbb1-rm.pdf), document 502-011, June 9, 2004, one page, archive id `dbb1-manual`
- [Schematic](https://digilent.com/reference/_media/dbb1/dbb1-sch.pdf), `DlabBB1.sch`, document 500-011, revision C, 30 March 2004, one sheet, archive id `dbb1-schematic`
- [Sell sheet](https://digilent.com/reference/_media/dbb1/dbb1-dwr1-brochure.pdf), document 530-011, June 9, 2004, one page, archive id `dbb1-sell-sheet`

Digilent reused document number 502-011 for the FX2 Breadboard manual dated September 26, 2006. The DBB1 file is the June 9, 2004 manual.

## PCB, Gerber, and netlist

The DBB1 resource center publishes the one-page reference manual, the one-page sell sheet, and the one-sheet schematic. PCB layout, Gerber, and IPC netlist files were not in that set.

## Bring-up

This board is outside the FPGA stage order. `make stage` accepts `nexys3`, `spartan3e`, `spartan3`, and `vdec1`. Bring up the host first, with its expansion headers empty. The breadboard carries host pins straight through, including the Spartan-3 configuration pins on A1, A2, and B1, so fit the host bitstream before attaching it. On the XC2-XL, use the verified end-reversed PA/PB table above for UART and probes. On the Spartan-3 starter, confirm the ribbon with tones before trusting silk numbers.
