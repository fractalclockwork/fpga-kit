# JTAG-SMT2

Digilent programming module for Xilinx parts, document 502-251, revision D. The February 19, 2026 edition is archive id `jtag-smt2-manual`. The February 25, 2021 edition is archive id `jtag-smt2-manual-2021` and is the copy that still lists which devices the module can target. Xilinx iMPACT, ChipScope, and EDK drive it, and so does Digilent Adept. `djtgcfg` is the bring-up's Adept programmer.

On this bench the preferred external JTAG cable is the [Bus Blaster v4.1a](bus-blaster-v4.md), because that cable is required for XC9500XL. The SMT2 remains an Adept-compatible alternate on Digilent headers (`ADEPT_DEVICE=JtagSmt2`) when a stage still uses `djtgcfg`. It cannot target a 9500 or 9500XL CPLD.

The SMT2 is a surface-mount module with a micro-AB USB port. The stand-alone cable built from the same circuit is the JTAG-HS2. Pad 11, Vdd, is a 3.3 V supply from the host board (2.97 V to 3.63 V). Pad 9, VREF, sets the JTAG signal level and may be 1.65 V to 5.5 V. On these boards the JTAG bank is 3.3 V, so Vdd and VREF both tie to that 3.3 V rail.

The cable on this bench is a Huasheng boxed pod of that circuit, not the 11-pad module. Its headers, the status LED, and the 27 Sep 2026 green-light reading are under [Bench cable](#bench-cable). Adept still names it `JtagSmt2`.

| Pad | Signal |
| --- | --- |
| 1 | GND |
| 2 | TCK |
| 3 | TDI |
| 4 | TMS |
| 5 | GPIO0 |
| 6 | GPIO1 |
| 7 | GPIO2 |
| 8 | TDO |
| 9 | VREF |
| 10 | GND |
| 11 | Vdd, 3.3 V |

GPIO2 is the Zynq `PS_SRST_B` pin when Xilinx tools expect it. None of these boards is a Zynq, so GPIO0–GPIO2 stay open.

## What it can program

The 2021 edition's supported-target list includes Xilinx FPGAs, CoolRunner-II CPLDs, and Platform Flash ISP PROMs. The same page says the module cannot target a Xilinx 9500 or 9500XL CPLD. That is why this bench prefers the [Bus Blaster](bus-blaster-v4.md) for the [XC2-XL](../boards/xc2xl.md): one cable reaches both the XC2C256 and the XC9572XL. Do not use the SMT2 on that board going forward. The 2026 edition no longer prints the supported-target list.

Adept's device name is the token `djtgcfg enum` prints. This repo's alternate path uses `JtagSmt2`. If enum prints a different token, set `ADEPT_DEVICE` to that token. `present` initializes that device, and the image stage programs the name `present` recorded.

```bash
export ADEPT_DEVICE=JtagSmt2
make stage BOARD=nexys3 STAGE=present
```

Leave `ADEPT_DEVICE` unset to keep the board's onboard port or its default cable.

## Where it lands on each board

| Board | Header | What the module loads |
| --- | --- | --- |
| [Nexys 3](../boards/nexys3.md) | J7, 6-pin | Index 0, the XC6SLX16. Onboard USB remains the primary path |
| [Spartan-3E](../boards/spartan3e.md) | J28, the alternate JTAG header in UG230 | Index 0, the XC3S500E. The VDEC1 has no JTAG port; this still programs the host FPGA |
| [Spartan-3](../boards/spartan3.md) | The board's external JTAG header | Index 0, the XC3S200. Index 1 is the XCF02S |
| [XC2-XL](../boards/xc2xl.md) | J1 | Not used going forward. Prefer the [Bus Blaster](bus-blaster-v4.md) for both CPLDs |

Nexys 3 schematic Rev B labels J7 as pin 1 TMS, pin 2 TDI, pin 3 TDO, pin 4 TCK, pin 5 GND, pin 6 VCC3V3. Those nets are not in SMT2 pad order. Wire TMS to TMS, TCK to TCK, TDI to TDI, TDO to TDO, GND to GND, and both Vdd and VREF to pin 6.

## Bench cable

The unit on the bench is a Huasheng Technology USB pod. The case reads "Xilinx JTAG Programming Cable USB", "High-Speed", model **JTAG SMT2**. A reading of JTAP-SMT2 is this same unit. The back label reads Huasheng Technology, `http://www.hseda.com`, made in China. The company is Wuhan Huasheng Taike (武汉华升泰克电子技术有限责任公司); the board silkscreen is HST.

Huasheng did not publish a PDF file. The manual is the eighteen detail plates on [HS2/SMT2/DLC9G/DLC10](http://www.hseda.com/product/download_cable/Xilinx-HS2/Xilinx-HS2.html), saved in that page order as archive id `jtag-smt2-hseda`. The row is manual because the page is HTML, so `make archive` hashes the cached PDF and does not try to download it again. Schematics are issued only after a purchase is registered on their after-sale page. The pod is the Digilent JTAG-SMT2 circuit in a box with a USB-B jack, so the 11-pad table above does not describe this connector. `djtgcfg` still sees a Digilent SMT2. Their iMPACT screenshot names the cable `JtagSmt2/210251A08870` with TCK at 30 MHz, and the dialog selection is "Digilent USB JTAG Cable".

On 27 Sep 2026 the status LED is green. Their sheet says orange means the USB plug is on the PC, and green means the JTAG plug is on a powered target.

The case is marked USB bus power, 5 V at 0.15 A, and **1.5 V < VREF < 5.0 VDC**. The Digilent table they reprint says 1.8 V to 5 V. Their own paragraph says a redesigned front end works down to 1.2 V and adds interface protection. The case label is the limit printed on this pod. These boards' JTAG banks are 3.3 V, which sits inside all three ranges.

They list ISE 13.1 and later, including ISE 14.1, and current Vivado, on Windows XP through 11 and on Linux. The driver they point at is the Digilent installer already in the tools: `ISE/bin/nt64/digilent/install_digilent.exe`, and `data/xicom/cable_drivers/nt64/digilent/install_digilent.exe` under Vivado. Claimed targets are Xilinx FPGAs, Zynq-7000, Artix-7, CoolRunner and CoolRunner-II, Platform Flash, and selected SPI and BPI PROMs. That list includes XC9500. The Digilent 2021 manual this page already uses says the SMT2 cannot target a 9500 or 9500XL, so the XC9572XL on the XC2-XL stays jumpered out.

Huasheng sells several pods under that one page. This bench unit is the SMT2 row.

| Model | Speed they print | Software they print |
| --- | --- | --- |
| SMT2 | 30 MHz | ISE 14.1 through current Vivado. Their pick for large devices |
| HS2 | 30 MHz | ISE 13.2 and later |
| HS3 | 30 MHz | ISE 14.1 and later |
| DLC9G | Slower than SMT2, same as DLC10 | ISE 6.2 through current Vivado. CY7C68013 plus XC2C256, firmware can update itself |
| DLC10 | Same as DLC9G | ISE 6.2 through current Vivado. No self-update. They say it does not support Artix-7 or Zynq |

Their copied feature row for JTAG-SMT2 marks 4-wire JTAG, 2-wire JTAG, Zynq `PS_SRST`, SPI, and Digilent Adept as supported, with an onboard USB connector.

Pin 1 is the pin with the triangle. The pod's shrouded header matches J4. The blue adapter fans that header out to J6 and J5. A keyed shell blocks a reversed ribbon. The 6-pin Dupont lead in the kit has no pin order on the images, so a 6-pin board header is still wired by signal name.

**Pod output, and J4, 2×7, 2.0 mm**

| Pin | Signal | Pin | Signal |
| --- | --- | --- | --- |
| 1 | GND | 2 | VREF |
| 3 | GND | 4 | TMS |
| 5 | GND | 6 | TCK |
| 7 | GND | 8 | TDO |
| 9 | GND | 10 | TDI |
| 11 | GND | 12 | NC |
| 13 | GND | 14 | INIT |

**J6, 2×5, 2.54 mm**

| Pin | Signal | Pin | Signal |
| --- | --- | --- | --- |
| 1 | TCK | 2 | GND |
| 3 | TDO | 4 | VREF |
| 5 | TMS | 6 | NC |
| 7 | NC | 8 | NC |
| 9 | TDI | 10 | GND |

**J5, 1×8, 2.54 mm**

| Pin | Signal |
| --- | --- |
| 1 | VREF |
| 2 | GND |
| 3 | TCK |
| 4 | TDO |
| 5 | TDI |
| 6 | TMS |
| 7 | NC |
| 8 | INIT |

The full kit is the pod, one USB 2.0 cable, a 10-pin 2.54 mm ribbon, a 14-pin 2.54 mm ribbon, a 14-pin 2.0 mm ribbon, a 7-wire 2.54 mm flying lead, a 6-pin single-row Dupont lead, and the adapter. Official Xilinx boards use a narrow Molex 14-pin 2.0 mm socket. That needs their separate ribbon: wide 14-pin 2.0 mm on the adapter, narrow Molex on the board. Their photos show the 14-pin 2.0 mm lead on a Spartan-6 XC6SLX16, the 10-pin 2.54 mm lead on an XC95144, and the 6-pin and flying leads on an XC6SLX9.

## Manuals

- [Reference manual, February 19, 2026](https://digilent.com/reference/_media/programmers/jtag-smt2/jtag-smt2_rm.pdf), archive id `jtag-smt2-manual`
- [Reference manual, February 25, 2021](https://digilent.com/reference/_media/reference/programmers/jtag-smt2/jtag-smt2_rm.pdf), archive id `jtag-smt2-manual-2021`, supported-target list on the last page
- Huasheng product-page plates, archive id `jtag-smt2-hseda`

A separate schematic PDF was not in the `jtag-smt2` media namespace. The pad table and the land pattern in document 502-251 are the connectivity source for the surface-mount module. The bench pod's connectivity source is archive id `jtag-smt2-hseda`.
