# VDEC1 (ADV7183B)

Digilent video decoder board, part 210-080, reference-manual document 502-046. This is a peripheral, not an FPGA. There is no Digilent SDK and no bitstream of its own. The programmable part is the [Spartan-3E starter](spartan3e.md) underneath it.

Lesson: [video and I2C](../learn/06-video-and-i2c.md). The host board also uses the JTAG and UART lessons.

## Specification

| Item | Value |
| --- | --- |
| Decoder | Analog Devices ADV7183B |
| Function | Digitizes NTSC, PAL, and SECAM to 8-bit or 16-bit YCrCb 4:2:2, plus HS, VS, and Field |
| ADCs | Three 10-bit converters at 54 MHz |
| Clock | 27 MHz on the card, period 37.037 ns |
| Inputs | Composite, S-video, and component, 75 ohm |
| Control | I2C. Write address `0x40` when ALSB is low |
| Connector | 100-pin Hirose FX2 socket |

The card mates with a host that has a Hirose FX2 plug. In this set that host is only the Spartan-3E. The Nexys 3 port is VHDCI. The Spartan-3 starter ports are 40-pin headers.

Define the FPGA pins before you attach the card. The Spartan-3E user LEDs share balls with FX2 data pins, and several of those pins are outputs from the decoder. The probe bitstream drives only SDA and SCLK, open-drain, and leaves every other FX2 ball as an input.

| VDEC1 pin | Signal | Spartan-3E ball | Spartan-3E net |
| --- | --- | --- | --- |
| A7 | SDA | A4 | FX2_IO2 |
| A8 | SCLK | D5 | FX2_IO3 |

The probe bit-bangs 100 kHz from the 50 MHz FPGA clock (125 clocks per quarter period) and prints `VDEC1,ACK,<cycles>` or `VDEC1,NACK,<cycles>` on the Spartan-3E DCE UART.

## Manuals

- [Kamami VDEC1 page](https://kamami.pl/en/retired-products/60090-vdec1.html), part 210-080, with the reference manual and schematic PDF. Archive ids `vdec1-manual` and `vdec1-schematic`
- [ADV7183B datasheet](https://www.analog.com/en/products/adv7183b.html), archive id `adv7183b-datasheet`
- No Adept device and no ISE part. The host's ISE install is the toolchain

The reference manual's own schematic figure is the connectivity drawing published with doc 502-046. A separate schematic PDF is linked from the Kamami product page.

## PCB, Gerber, and netlist

The published VDEC1 files found so far are the two-page reference manual and a schematic PDF. PCB layout, Gerber, and IPC netlist files were not in that package. The archive records zip members if a download is a zip.

## Bring-up

Leave the connector empty and bring up the Spartan-3E heartbeat first. The VDEC1 stages also wait until the Nexys 3 image stage and the Spartan-3E `present` stage have passed. When the probe bitstream is the one you will load, set `VDEC1_ATTACHED=1` and run:

```bash
make stage BOARD=vdec1 STAGE=present
make stage BOARD=vdec1 STAGE=workflow
make sim BOARD=vdec1
make hil BOARD=vdec1
```

`make hil` builds the I2C probe for `xc3s500e-4fg320`, programs JTAG index 0 of the Spartan-3E, and requires a `VDEC1,ACK` line on `HIL_SERIAL`. Without `VDEC1_ATTACHED=1` every VDEC1 stage is refused, so an empty connector is not reported as a failed decoder. The stage rules are in the [pipeline](../pipeline.md).
