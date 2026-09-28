# Logic and LUTs

A lookup table stores the output of a Boolean function for every input combination. The FPGA does not wire a separate AND or OR gate for your equation. Synthesis turns the equation into a truth table and writes that table into a small memory.

## From an equation to a table

Take a 2-input function, `Y = A AND NOT B`.

| A | B | Y |
| --- | --- | --- |
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 1 |
| 1 | 1 | 0 |

Four rows is a 4-entry memory. The address is the input bits `AB`, and the stored bit is `Y`. A hardware LUT is that memory with the inputs on the address pins. A 4-input LUT has `2^4 = 16` rows. A 6-input LUT has `2^6 = 64` rows. Any function of that many inputs fits in one table, no matter how tangled the equation looks.

## What these chips actually contain

A Spartan-3 or Spartan-3E slice has two 4-input LUTs and two flip-flops. The XC3S200 on the starter board has 1,920 slices: 3,840 LUTs and 3,840 flip-flops, often counted as 4,320 logic cells in the older "gate" marketing number. The XC3S500E has 4,656 slices and 20 block RAMs of 18 Kbit.

A Spartan-6 slice has four 6-input LUTs and eight flip-flops. The XC6SLX16 on the Nexys 3 has 2,278 slices, which the synthesis report prints as slice registers and slice LUTs rather than as "4 input LUTs". One 6-input LUT can absorb logic that would have taken several 4-input LUTs on the older families. That is why the same heartbeat can report a handful of LUTs on the Nexys 3 and a different handful on the Spartan-3, and both numbers can be right.

The VDEC1 has no LUT fabric. The ADV7183B is a fixed video decoder. All of the programmable logic for that card lives in the Spartan-3E that hosts it.

The XC2-XL is the CPLD in this set. The XC2C256 and the XC9572XL implement equations in macrocells and product terms. ISE's CPLD fitter writes a JEDEC file for those parts. The slice and LUT lines in this lesson are the Spartan reports.

## Where the numbers land

After `xst`, the synthesis report (`.srp`) includes lines the bring-up parser keeps:

- `Number of Slices`
- `Number of Slice Flip Flops` on Spartan-3 and Spartan-3E, or `Number of Slice Registers` on Spartan-6
- `Number of 4 input LUTs` or `Number of Slice LUTs`
- `Number of bonded IOBs`
- `Number of Block RAM/FIFO`

A heartbeat that blinks one LED and speaks UART should stay far below the smallest part in this set, the XC3S200. If a later design's slice count climbs across runs, that `.srp` field is the one to plot. The parser writes it to `build_metrics.json` under `utilization`.

## What a LUT does not do

A LUT output updates when its inputs change. It does not remember the previous result. Memory is the flip-flop in the same slice, and it updates only on the clock. The next lesson is that clock.
