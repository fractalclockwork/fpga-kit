import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, ClockCycles

CLKS = 4


async def read_byte(dut):
    await FallingEdge(dut.uart_tx)
    await ClockCycles(dut.clk, 6)
    value = 0
    for _index in range(8):
        value |= int(dut.uart_tx.value) << _index
        await ClockCycles(dut.clk, CLKS)
    return value


async def read_line(dut):
    chars = bytearray()
    while True:
        byte = await read_byte(dut)
        if byte == 0x0A:
            return chars.decode("ascii")
        chars.append(byte)
        if len(chars) > 80:
            raise AssertionError(f"unterminated UART line {chars!r}")


async def write_byte(dut, byte):
    dut.uart_rx.value = 0
    await ClockCycles(dut.clk, CLKS)
    for index in range(8):
        dut.uart_rx.value = (byte >> index) & 1
        await ClockCycles(dut.clk, CLKS)
    dut.uart_rx.value = 1
    await ClockCycles(dut.clk, CLKS)


def cycles_of(line):
    return int(line.strip().split(",")[-1], 16)


@cocotb.test()
async def hello_then_pong(dut):
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    dut.rst.value = 1
    dut.uart_rx.value = 1
    await ClockCycles(dut.clk, 4)
    dut.rst.value = 0

    lines = []

    async def collect():
        while True:
            lines.append(await read_line(dut))

    cocotb.start_soon(collect())
    while not lines:
        await ClockCycles(dut.clk, 1)
    hello = lines[0]
    assert hello.startswith("HELLO,nexys3"), hello
    first = cycles_of(hello)

    for byte in b"PING\n":
        await write_byte(dut, byte)
        await ClockCycles(dut.clk, CLKS)

    for _ in range(30):
        for line in lines:
            if line.startswith("PONG,"):
                assert cycles_of(line) >= first
                return
        await ClockCycles(dut.clk, 100)
    raise AssertionError(f"no PONG after HELLO, lines {lines!r}")
