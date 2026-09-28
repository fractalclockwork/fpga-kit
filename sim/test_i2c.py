import cocotb
from cocotb.clock import Clock
from cocotb.triggers import FallingEdge, RisingEdge, ClockCycles

CLKS = 4


async def pull_ack(dut):
    previous = 1
    rises = 0
    dut.sda_in.value = 1
    while True:
        await RisingEdge(dut.clk)
        scl = 0 if int(dut.scl_low.value) else 1
        if previous == 0 and scl == 1:
            rises += 1
        dut.sda_in.value = 0 if rises == 9 and scl == 1 else 1
        previous = scl


async def read_byte(dut):
    await FallingEdge(dut.uart_tx)
    await ClockCycles(dut.clk, 6)
    value = 0
    for index in range(8):
        value |= int(dut.uart_tx.value) << index
        await ClockCycles(dut.clk, CLKS)
    return value


@cocotb.test()
async def decoder_acks(dut):
    clock = Clock(dut.clk, 10, units="ns")
    cocotb.start_soon(clock.start())
    dut.rst.value = 1
    dut.sda_in.value = 1
    await ClockCycles(dut.clk, 4)
    dut.rst.value = 0
    cocotb.start_soon(pull_ack(dut))
    chars = bytearray()
    while True:
        byte = await read_byte(dut)
        if byte == 0x0A:
            break
        chars.append(byte)
        if len(chars) > 40:
            break
    line = chars.decode("ascii")
    assert line.startswith("VDEC1,ACK"), line
