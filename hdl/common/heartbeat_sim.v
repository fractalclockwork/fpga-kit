// Fast parameters so Cocotb can finish a HELLO and a PONG without a long route.
module heartbeat_sim (
    input  wire clk,
    input  wire rst,
    input  wire uart_rx,
    output wire uart_tx,
    output wire led
);
    heartbeat #(
        .CLKS_PER_BIT(4),
        .HELLO_EVERY(64),
        .BOARD("nexys3  ")
    ) dut (
        .clk(clk),
        .rst(rst),
        .uart_rx(uart_rx),
        .uart_tx(uart_tx),
        .led(led)
    );
endmodule
