# Video and I2C

The VDEC1 is a carrier for the Analog Devices ADV7183B. It digitizes NTSC, PAL, or SECAM into 8-bit or 16-bit YCrCb 4:2:2, plus horizontal sync, vertical sync, and a field flag. It is not an FPGA. In this set of boards the only connector it can mate with is the Hirose FX2 plug on the Spartan-3E starter. The Nexys 3 expansion port is VHDCI. The Spartan-3 starter uses 40-pin headers. Forcing the card onto either of those will not work and can bend the connector.

## Do not mate the card until the pins are safe

The VDEC1 manual requires the host FPGA to drive the Hirose pins as a known design before the card is attached. The user LEDs on the Spartan-3E are wired to the same balls as FX2 data pins. A heartbeat that blinks LED0 is the right test with the connector empty. It is the wrong bitstream to have loaded when the decoder is plugged in, because several of those LED pins are video outputs from the ADV7183B. The VDEC1 bitstream only drives the I2C pair, and it drives them open-drain. Every other FX2 ball stays an input. Set `VDEC1_ATTACHED=1` only after that bitstream is the one you intend to load, and only then attach the card.

## 4:2:2

The decoder's three 10-bit, 54 MHz ADCs produce luma and chroma. The digital output is YCrCb 4:2:2: for every two luma samples Y there is one Cr sample and one Cb sample. A full pixel pair is four bytes in 8-bit mode (`Cb, Y0, Cr, Y1`), not three bytes of RGB and not a sample of chroma on every pixel. The 27 MHz oscillator on the VDEC1 is the decoder's clock. Pixel clocks on the connector (LLC1, LLC2) are derived from the video standard, not from the FPGA's 50 MHz oscillator. Capturing those pixels is a later design. The first test does not sample them.

## The probe

The ADV7183B does nothing useful until its I2C registers are set. The first question is only whether the chip acknowledges its address.

VDEC1 Hirose pin A7 is SDA and pin A8 is SCLK. On the Spartan-3E those balls are A4 (`FX2_IO2`) and D5 (`FX2_IO3`). The probe bit-bangs 100 kHz from the 50 MHz clock:

```text
quarter period = 50 MHz / (4 * 100 kHz) = 125 clocks
```

The sequence is a start condition, the write address `0x40` (ALSB low, 7-bit address `0x20`), and a sample of the ACK bit with SDA released. ACK is SDA low. The UART then prints `VDEC1,ACK,<cycles>` or `VDEC1,NACK,<cycles>`.

Open-drain means the FPGA may pull a line low and must otherwise let the pin float so the board pull-up can make it high. Driving SDA high as a push-pull output fights the decoder. The top-level pins are inout: drive 0, or high-Z.

A NACK with the card attached means the address, the pull-ups, or the connector seating is wrong. A NACK with the card absent is the expected result, which is why the HIL step is skipped unless `VDEC1_ATTACHED=1`.
