# Lessons

A short course for these kits. Each lesson states the idea, the equation, and where it shows up on the boards and in the ISE reports. The manuals themselves stay in the [archive](../../archive/README.md). How a run is gated, and the JSON those reports land in, is the [pipeline](../pipeline.md) and the [report catalog](../reports.md).

Clocks used in the worked numbers:

| Board | Clock |
| --- | --- |
| Spartan-3 starter | 50 MHz |
| Spartan-3E starter | 50 MHz |
| Nexys 3 | 100 MHz |
| VDEC1 | 27 MHz oscillator on the decoder |

## Course

1. [Logic and LUTs](01-logic-and-luts.md). Boolean equations, truth tables, and the difference between a 4-input LUT and a 6-input LUT. Read this before any board.
2. [Clocks and timing math](02-clocks-and-timing.md). Period, setup slack, and hold. Read this before trusting a timing score.
3. [ISE operation](03-ise-operation.md). What `xst`, `ngdbuild`, `map`, `par`, and `bitgen` consume and emit, and why `par` dominates elapsed time.
4. [JTAG and configuration](04-jtag-and-configuration.md). Scan chains, IDCODE, and why the FPGA is empty after power loss.
5. [UART](05-uart.md). Bit time, 8N1 framing, and the cycle-count field on the heartbeat line.
6. [Video and I2C](06-video-and-i2c.md). YCrCb 4:2:2 and the probe that asks the ADV7183B to ACK. Read this before mating a VDEC1.

## Which lesson applies

| Board | Lessons |
| --- | --- |
| [Nexys 3](../boards/nexys3.md) | 1, 2, 3, 4, 5 |
| [Spartan-3E starter](../boards/spartan3e.md) | 1, 2, 3, 4, 5, and 6 when a VDEC1 is attached |
| [Spartan-3 starter](../boards/spartan3.md) | 1, 2, 3, 4, 5 |
| [VDEC1](../boards/vdec1.md) | 6, plus 4 and 5 on the Spartan-3E host |
| [XC2-XL](../boards/xc2xl.md) | 1 and 4. The CPLD fitter writes a JEDEC file, so lessons 3 and 5 stay with the FPGAs |
| [Breadboard 1](../boards/dbb1.md) | The lessons for whichever host it is plugged into |
| [BSS138 shifter](../boards/bss138.md) | 5, on the XC2-XL UART |
