# Clocks and timing math

The clock is a square wave. Its period is the time from one rising edge to the next:

```text
T = 1 / f
```

| Board | f | T |
| --- | --- | --- |
| Spartan-3 starter, pin T9 | 50 MHz | 20 ns |
| Spartan-3E starter, pin C9 | 50 MHz | 20 ns |
| Nexys 3, pin V10 | 100 MHz | 10 ns |
| VDEC1 oscillator | 27 MHz | 37.037 ns |

The VDEC1 clock belongs to the decoder chip. It is not the FPGA clock. Video samples come out of the ADV7183B against that 27 MHz domain. The Spartan-3E must treat those pins as inputs from another clock.

## Setup slack

On a rising edge the flip-flop captures its D input. The next edge must not arrive until the new value has traveled through LUT logic and routing and still meets the flip-flop's setup time.

```text
slack_setup = Tperiod - (Tco + Tlogic + Troute + Tsu)
```

- `Tco` is the clock-to-output delay of the launching flip-flop.
- `Tlogic` is the delay through LUTs.
- `Troute` is the delay of the wires `par` chose.
- `Tsu` is the setup time of the capturing flip-flop.

A positive slack means the data arrived early. A negative slack means it arrived after the deadline. At 100 MHz the whole budget is 10 ns. At 50 MHz it is 20 ns. The same logic can pass on the Spartan-3E and fail on the Nexys 3 only because the period got shorter.

## Hold

Hold time is how long the data must stay valid after the capturing edge. The hold check does not include `Tperiod`. Making the clock slower does not fix a hold violation. Hold failures come from a path that is too fast, usually a short route or a clock skew that delivers the capturing edge late. ISE repairs many of these by adding delay. A `.twr` that still reports a hold failure is a real problem, not a budget you can relax by editing the period.

## What place-and-route is deciding

Synthesis picks the LUTs. It does not know which wires the FPGA will use, so it cannot know `Troute`. `par` places the slices and then searches for routes that make every slack non-negative. That search is why the router line in the `.par` report is the long one. The timing score is zero when every constrained path has non-negative slack. A score above zero means at least one path failed. The bring-up treats a non-zero score, or a setup or hold failure in the `.twr`, as a failed build and does not program the board.

The heartbeat UCF carries an explicit period: 10 ns on the Nexys 3, 20 ns on the two Spartan-3 boards. Without that constraint the tools have no deadline, the score stays zero, and the report is not evidence that the design will run at the oscillator frequency.

## Two clocks on one board

UART bit timing and the video decoder are separate domains. Do not sample ADV7183B data with the 50 MHz oscillator unless a synchronizer or an asynchronous FIFO sits between them. The first VDEC1 test avoids that problem: it only bit-bangs I2C from the 50 MHz clock and does not capture video.
