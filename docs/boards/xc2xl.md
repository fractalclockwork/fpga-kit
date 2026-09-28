# XC2-XL

Digilent CPLD board, reference-manual document 500-028, revision May 11, 2004. It carries two Xilinx CPLDs: a CoolRunner-II XC2C256 in TQ144, and an XC9572XL in VQ44. ISE WebPACK 14.7 is the SDK. The fitter writes a JEDEC file. The pattern remains after power is removed.

Lessons: [logic and LUTs](../learn/01-logic-and-luts.md) for the contrast with macrocells, [JTAG](../learn/04-jtag-and-configuration.md), and [UART](../learn/05-uart.md). The heartbeat is fitted with the CPLD fitter, not the Spartan place-and-route flow.

## Specification

| Item | Value |
| --- | --- |
| CPLDs | CoolRunner-II XC2C256-TQ144 (IC2) and XC9572XL-VQ44 (IC1) |
| Clock | Socketed half-size 8-pin DIP oscillator on GCK2 of both devices. The feature list calls the included part 1.8432 MHz. The clock section calls it 1.842 MHz. Other oscillators from 32 kHz to 100 MHz fit the socket |
| Period | 542.5 ns at 1.8432 MHz |
| JTAG | 6-pin 3.3 V header J1. Digilent JTAG3, or a Xilinx Parallel-III or Parallel-IV cable, as named in the manual |
| Onboard I/O | One pushbutton on GSR of both CPLDs, and one LED on each CPLD |
| Expansion | Four 2×20 100 mil headers. A (J3), B (J4), and D (J6) are the XC2C256. C (J5) is the XC9572XL |
| Power | Wall plug J9, 5 V to 9 V DC, center-positive, at least 250 mA. Battery header J2, 2.8 V to 3.6 V. External header J8. CoolRunner core is 1.8 V |
| Size | 5.25 in × 5.25 in, with an 18×46 hole wire-wrap field |

Figure 4 in the manual warns that the IC1 and IC2 legends on the board silkscreen are swapped. The figure, and the pin tables below, treat IC2 as the XC2C256 and IC1 as the XC9572XL.

| Net | Device | Pin | Role |
| --- | --- | --- | --- |
| `clk` | XC2C256 | 38 | GCK2, net XCCLK |
| `clk` | XC9572XL | 1 | GCK2, net XLCLK |
| `btn` | XC2C256 | 143 | GSR |
| `btn` | XC9572XL | 33 | GSR |
| `led` | XC2C256 | 92 | LD2 |
| `led` | XC9572XL | 44 | LD3 |

Both devices ship with a factory pattern that flashes the LEDs at rates selected by the button. Expansion pinouts are tables 1, 2, and 3 in document 500-028. A [Breadboard 1](dbb1.md) mates with the 2×20 sockets. Connectors A (J3) and B (J4) are the pair on the XC2C256.

JTAG figure 3 draws TDI into the XC2C256 and that device's TDO into the XC9572XL. JP5, JP6, JP9, and JP10 can leave either device out of the chain. The four jumper settings in the figure are both devices, XC2C256 only, XC9572XL only, and an invalid combination.

A [JTAG-SMT2](../programmers/jtag-smt2.md) on J1 can program the XC2C256. The 2021 SMT2 manual says the module cannot target an XC9500XL, so the XC9572XL jumper setting for that path is XC2C256 only.

## SDK and manuals

- ISE WebPACK 14.7, archive id `ise-14.7-lin`. The CPLD fitter in that install is the tool. The FPGA flow (`xst` through `bitgen`) is the one the other boards use
- [Reference manual](https://digilent.com/reference/_media/xc2xl/xc2xl_rm.pdf), document 500-028, archive id `xc2xl-manual`
- [Sell sheet](https://digilent.com/reference/_media/xc2xl:xc2xl_ds.pdf), document 530-020, June 18, 2004, archive id `xc2xl-sell-sheet`
- Schematic `XC2XL.sch`, 23 Oct 2003, five sheets, archive id `xc2xl-schematic`

## PCB, Gerber, and netlist

The Digilent `xc2xl` media namespace has the six-page reference manual and the one-page sell sheet. The schematic is the five-sheet `XC2XL.sch` PDF from the old product download, archive id `xc2xl-schematic`. PCB layout, Gerber, and IPC netlist files were not in that set. Tables 1–3 of document 500-028 and the schematic are the connectivity source.

## UART on J4

The probe image walks one high along J4 pins 5 through 40, about 0.6 s on each pin at 1.8432 MHz, in that pin order. Pins 1–3 are ground, VU, and 3.3 V. Pin 4 is the button. With no clock, pin 5 stays high and pins 6–40 stay low. `LD2` flashes on its own, about 3.5 times a second, and stays on with no clock. That LED is active low: 3.3 V into the anode, then 510 Ω from the cathode into pin 92 (schematic I/O I01516). JP7 ties the oscillator output to pin 38 (`XCCLK`). JP8 ties that same output to the XC9572XL (`XLCLK`). Pin 92's driver is the VIO1 bank (pins 27, 55, 73, and 93). JP2 ties VIO1 to the 3.3 V regulator. J4 pins 5–40 are the VIO2 bank. `LD3` is on VIO2 as well.

| J4 pin | Signal | XC2C256 pin | Cable |
| --- | --- | --- | --- |
| 1 | GND | — | GND |
| 5 | `uart_rx` | 142 (B5) | converter TX |
| 6 | `uart_tx` | 140 (B6) | converter RX |

Pin 2 is VU from the wall plug, pin 3 is 3.3 V, and pin 4 is the GSR button. None of those are UART pins. Pins 140 and 142 sit on VIO2, which is 3.3 V. CoolRunner-II inputs are not 5 V tolerant: the absolute maximum on an I/O pin is 4.0 V. J4 is cabled to [Breadboard 1](dbb1.md) connector A2, pin 1 to pin 1. The silkscreen legend on that header is PA, and the pins are numbered 1–40: pin 1 is GND, pin 3 is 3.3 V, pin 5 is `uart_rx`, and pin 6 is `uart_tx`. J5 is cabled to B2 the same way. The [BSS138 level shifter](bss138.md) sits on the breadboard between those A2 pins and 5 V TTL. Its LV pin is A2 pin 3, GND is A2 pin 1, one low-side channel is A2 pin 6, and the other is A2 pin 5. HV is the TTL supply. A2 pin 2 is VU from the wall plug, 5 V to 9 V, and is not HV. A TTL TX wired straight to A2 pin 5, with no shifter, still needs a divider: 2.2 kΩ from the TTL TX to pin 5, and 3.3 kΩ from pin 5 to pin 1. That puts about 3.0 V on the pin.

The XC9572XL inputs are 5 V tolerant, and they land on J5, not J4. There is no board trace between the two CPLDs' user I/O. The JTAG-SMT2 can program the XC2C256 and cannot target the XC9572XL. CoolRunner work is stopped. The XC2C256 holds the LD2 blink JEDEC `reports/xc2xl/20260928T013200Z/project.jed` (pin 92, active low, about 3.5 Hz from the 1.8432 MHz clock). Fuse readback matched that file except one trailing bit, and LD2 stays dark. The factory blink on that device is gone. LD3 is the XC9572XL and was still running its factory pattern. The J4 UART table stays for a later breadboard test. Do not resume it until LD3 is seen flashing under the parked plan.

## Bring-up

This board is outside the FPGA stage order. `make stage` accepts `nexys3`, `spartan3e`, `spartan3`, and `vdec1`. `make cpld BOARD=xc2xl` fits a JEDEC file for the XC2C256 only. Do not write `stage.json` for this board unless a real pass happens.

## Parked: XC9572XL

Use this only if the CoolRunner stays unusable. The XC9572XL is the smaller part, and it is the fallback because its inputs are 5 V tolerant and its LED was already flashing. Do not start this until asked.

1. Leave the factory image in the XC9572XL until a blink JEDEC exists and the Bus Blaster enumerates that chip. LD3 flashing is the proof that pin 44 still drives. Erasing first throws that proof away.
2. Fit a blink for the XC9572XL only. Clock is pin 1 (`XLCLK`, JP8), the button is pin 33, and LD3 is pin 44, active low through 510 Ω. Take the speed grade from the chip marking. I/O standard is LVCMOS33. Do not reuse an XC2C256 JEDEC.
3. Program with the Bus Blaster v4.1a and `xc3sprog`, from the JEDEC file. The buffer image is the usual JTAG-key load. J1 is the 6-pin 3.3 V header; the Bus Blaster plug is the 20-pin ARM header, so TMS, TCK, TDI, TDO, ground, and 3.3 V are wired across. The chain still includes the XC2C256 unless JP5, JP6, JP9, and JP10 leave only the XC9572XL in it. Program the position whose IDCODE is the XC9572XL. Adept named that device index 1, IDCODE `49604093`.
4. The JTAG-SMT2 and `djtgcfg` do not program this family. The Bus Pirate v3.6 is not the programmer for it.
5. The pass is LD3 flashing from the new image. UART on J5 is the step after that, and only then. J5 is the 5 V-tolerant header. The breadboard BSS138 path stays parked with the CoolRunner.
