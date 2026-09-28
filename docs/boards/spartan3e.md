# Spartan-3E starter

Xilinx starter kit manufactured with Digilent, retired. The FPGA on the standard kit is an XC3S500E-4FG320. ISE WebPACK 14.7 is the SDK, including EDK for MicroBlaze. This is the Hirose FX2 host for the [VDEC1](vdec1.md).

Lessons: [logic and LUTs](../learn/01-logic-and-luts.md), [clocks and timing](../learn/02-clocks-and-timing.md), [ISE operation](../learn/03-ise-operation.md), [JTAG](../learn/04-jtag-and-configuration.md), [UART](../learn/05-uart.md). Read [video and I2C](../learn/06-video-and-i2c.md) before attaching a VDEC1.

## Specification

| Item | Value |
| --- | --- |
| FPGA | XC3S500E-4FG320, ISE part `xc3s500e-4fg320` |
| Clock | 50 MHz, ball C9, period 20 ns |
| IDCODE | `01C22093` (revision nibble ignored) |
| JTAG chain | FPGA, two XCF04S Platform Flashes, XC2C64A CPLD. Program index 0 |
| Memory | 64 MB DDR SDRAM, parallel NOR StrataFlash, SPI flash |
| Peripherals | 10/100 Ethernet (LAN83C185), VGA, PS/2, SPI DAC, SPI ADC, two RS-232 ports |
| Expansion | Hirose FX2 (J3) plus a 100 mil header |
| USB | Onboard USB JTAG on a factory board. Header J28 is the alternate JTAG header. A [JTAG-SMT2](../programmers/jtag-smt2.md) on J28 uses `ADEPT_DEVICE=JtagSmt2`. This unit's USB port does not work; see below |

The DCE RS-232 port is the one the host adapter uses. FPGA transmit is ball M14 (`RS232_DCE_TXD`). FPGA receive is ball R7 (`RS232_DCE_RXD`). 115200 baud, 8N1, 434 clocks per bit.

| Net | Ball | Role |
| --- | --- | --- |
| `clk` | C9 | 50 MHz oscillator |
| `led` | F12 | LD0. Also FX2_IO20. Do not load this bitstream with a VDEC1 mated |
| `uart_rx` | R7 | DCE receive |
| `uart_tx` | M14 | DCE transmit |

FX2 pins used only by the VDEC1 probe are in [that board's page](vdec1.md).

## SDK and manuals

- ISE WebPACK 14.7, archive id `ise-14.7-lin`
- Adept 2, archive ids `adept-runtime` and `adept-utilities`, when the cable or the onboard USB speaks Adept
- [Reference center](https://digilent.com/reference/programmable-logic/spartan-3e/start)
- [UG230 user guide](https://digilent.com/reference/_media/reference/programmable-logic/spartan-3e/s3estarter_ug.pdf), archive id `spartan3e-ug230`. The guide includes the board photograph and schematic sheets
- [Schematic Rev D](https://digilent.com/reference/_media/s3e:spartan-3e_sch.pdf), archive id `spartan3e-schematic`

## PCB, Gerber, and netlist

The published packages checked for this board are PDFs (UG230 and schematic Rev D), not a fabrication zip. PCB layout, Gerber, and IPC netlist files were not in those packages. The archive records zip members if a download is a zip. Until then schematic Rev D and UG230 appendix A are the connectivity source.

## This unit

The onboard USB download port on this board does not program the FPGA. It enumerates (`03fd:000d` from the bootloader, `03fd:0008` after the embedded-cable firmware) and does not return a JTAG chain. Bring-up uses an external Digilent cable on J28.

The working theory is that the XC2C64A held factory control logic and that image has been overwritten. Schematic Rev D leaves the USB controller itself off the drawing (sheet 3 is the proprietary USB page). The CPLD is the last device in the scan chain, and its TDO returns to the USB side through the 74LVC1G125. A user image in that part can still drive configuration and JTAG nets. The UG230 package and schematic in the archive do not include a binary for it, so there is nothing here to reload. Leave the USB port unused.

## Bring-up

These stages stay closed until the Nexys 3 image stage has passed. See the [pipeline](../pipeline.md).

```bash
make stage BOARD=spartan3e STAGE=present
make stage BOARD=spartan3e STAGE=workflow
make hil BOARD=spartan3e
```

The HIL serial device is the DCE port, in `HIL_SERIAL`. `make sim BOARD=spartan3e` runs the same heartbeat suite as the other FPGA boards. The VDEC1 probe is a different bitstream: `make hil BOARD=vdec1` with `VDEC1_ATTACHED=1`. If `present` records only the onboard Xilinx USB programmer, the image stage will not call `djtgcfg` on that path.

ChipScope is available in ISE for this family and is left for a later debug bitstream. The XC3S500E can hold it. The heartbeat does not.
