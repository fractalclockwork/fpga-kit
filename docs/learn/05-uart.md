# UART

The heartbeat and the host talk over an asynchronous serial line. There is no shared clock wire. Both sides agree on a bit time and recover the clock from the falling edge of the start bit.

## Bit time

```text
Tbit = 1 / baud
```

The bring-up uses 115200 baud, 8 data bits, no parity, one stop bit.

| Clock | Clocks per bit, integer | Actual bit time | Error |
| --- | --- | --- | --- |
| 50 MHz | 434 | 8.680 us | +0.16% versus 8.681 us |
| 100 MHz | 868 | 8.680 us | +0.16% |

`434 = round(50e6 / 115200)` and `868 = round(100e6 / 115200)`. The error is far inside the few percent a UART can tolerate. The Spartan-3 starter still passes through a MAX3232 level shifter on the way to the DB9. The FPGA pin is logic-level. The host needs a USB-RS232 adapter on that connector. The Nexys 3 FTDI bridge and the Spartan-3E DCE port present a USB or RS-232 connector, but the FPGA still sees the same 8N1 waveform.

## A frame

The line idles at logic 1. A frame is:

1. Start bit, logic 0.
2. Eight data bits, least significant bit first.
3. Stop bit, logic 1.

The receiver waits for the falling edge, waits half a bit, checks that the line is still 0, then samples each data bit in the middle of its window. A false start returns to idle.

## The line the host expects

The FPGA sends one text line. Fields are separated by commas.

```text
HELLO,nexys3  ,00001A2B
PONG,nexys3  ,00001A3C
```

The board field is eight characters, padded with spaces. The last field is the free-running FPGA clock counter at the moment the line was built, eight hexadecimal digits. The host strips the board name and stores both timestamps on one JSON record:

- `host_monotonic_ns`, from the dev-host clock
- `fpga_cycles`, from that hex field

Dividing a difference in `fpga_cycles` by the board clock gives FPGA time. A 100 MHz counter advances 100 cycles per microsecond. Comparing that interval with the host's monotonic clock is how a UART delay becomes visible. The two clocks are not locked. The record only lines them up at the sample.

The host sends `PING` followed by a newline. The FPGA answers with `PONG` and a newer cycle count. The same Cocotb test drives that exchange in simulation. The pytest HIL test drives it on the serial port. Simulation has to pass before `par` runs, so a broken UART never spends router time.

The VDEC1 probe uses the same UART on the Spartan-3E and a different line, `VDEC1,ACK,<cycles>` or `VDEC1,NACK,<cycles>`. That line is covered in the [video lesson](06-video-and-i2c.md).
