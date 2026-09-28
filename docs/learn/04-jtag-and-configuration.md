# JTAG and configuration

The bitstream describes LUT contents and routing. It lives in SRAM inside the FPGA. Remove power, or pulse PROG, and that SRAM is empty. The part will not keep a design across a power cycle unless some other chip hands it a bitstream at startup. On these boards that other chip is a Platform Flash or a PCM device, and only if the mode jumpers say to load from it. JTAG programming of the FPGA itself is volatile on purpose: it is how the bring-up tests a new `.bit` without writing the flash.

## IDCODE

Every Xilinx part shifts out a 32-bit IDCODE. The top four bits are the silicon revision and change between steppings. The other 28 bits identify the family and the die. The bring-up compares those 28 bits and ignores the revision nibble.

| Board | Device at the programmed index | IDCODE with revision 0 |
| --- | --- | --- |
| Nexys 3 | XC6SLX16, index 0 | `04002093` |
| Spartan-3E starter | XC3S500E, index 0 | `01C22093` |
| Spartan-3 starter | XC3S200, index 0 | `01414093` |

`djtgcfg init` prints the chain. Confirm the index before trusting a script. The Spartan-3E chain continues through two XCF04S flashes and an XC2C64A CPLD. The Spartan-3 starter chain is the XC3S200 and then an XCF02S. Programming index 1 on that board writes the flash, not the FPGA.

## How each board is reached

Adept's name is the USB device, not the FPGA.

- Nexys 3: onboard USB2, `djtgcfg prog -d Nexys3 -i 0 -f project.bit`. Header J7 is the 6-pin JTAG port. A [JTAG-SMT2](../programmers/jtag-smt2.md) wired to J7 is the alternate. Set `ADEPT_DEVICE` to the name `djtgcfg enum` prints. The repo's name for that module is `JtagSmt2`.
- Spartan-3E: onboard USB JTAG. The Adept name depends on the firmware and is recorded in `boards/spartan3e.yaml`. UG230 calls J28 the alternate JTAG header. An external Digilent cable or a JTAG-SMT2 on that header is the fallback when the onboard Xilinx USB device does not enumerate on a current kernel. Set `ADEPT_DEVICE` to the name `djtgcfg enum` prints.
- Spartan-3 starter: no onboard USB. A Digilent JTAG-USB, JTAG-HS, or [JTAG-SMT2](../programmers/jtag-smt2.md) is required. The YAML default is the usual cable name `JtagHs2`. Override it with `ADEPT_DEVICE`. The SMT2 name in this repo is `JtagSmt2`.
- VDEC1: no JTAG port. The bitstream under test is the Spartan-3E I2C probe. The SMT2 programs that host, not the decoder.
- XC2-XL: 6-pin 3.3 V header J1. Document 500-028 draws TDI into the XC2C256 and then into the XC9572XL. JP5, JP6, JP9, and JP10 can drop either device from the chain. The programmed pattern remains after power is removed. This board is outside the FPGA stage order. The JTAG-SMT2 can program the XC2C256. The 2021 SMT2 manual says the module cannot target an XC9500XL, so the XC9572XL stays jumpered out of the chain for that path.

`djtgcfg` runs from the host Adept tree. When it is not on `PATH`, a privileged helper container mounts `/dev/bus/usb`. The ISE container does not see that bus. The USB-UART tty stays on the dev-host.

## What "done" means

After a successful program, the FPGA raises DONE and the board's DONE LED lights. The heartbeat UART line is the bring-up's evidence that the design is actually running. DONE alone only means the frames were loaded.
