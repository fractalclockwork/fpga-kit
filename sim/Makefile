SIM ?= icarus
TOPLEVEL_LANG = verilog
BOARD ?= nexys3

ifeq ($(BOARD),vdec1)
TOPLEVEL := i2c_probe_sim
MODULE := test_i2c
VERILOG_SOURCES := \
	$(abspath ../hdl/common/uart_tx.v) \
	$(abspath ../hdl/common/i2c_probe.v) \
	$(abspath ../hdl/common/i2c_probe_sim.v)
else
TOPLEVEL := heartbeat_sim
MODULE := test_heartbeat
VERILOG_SOURCES := \
	$(abspath ../hdl/common/uart_tx.v) \
	$(abspath ../hdl/common/uart_rx.v) \
	$(abspath ../hdl/common/heartbeat.v) \
	$(abspath ../hdl/common/heartbeat_sim.v)
endif

export COCOTB_REDUCED_LOG_FMT=1

COCOTB_MAKE := $(shell cocotb-config --makefiles 2>/dev/null)
ifeq ($(COCOTB_MAKE),)
$(error cocotb is not installed. pip install -r requirements.txt)
endif

include $(COCOTB_MAKE)/Makefile.sim
