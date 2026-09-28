module heartbeat_top (
    input  wire clk,
    input  wire uart_rx,
    output wire uart_tx,
    output wire led
);
    reg [3:0] por = 4'b0;
    always @(posedge clk)
        por <= {por[2:0], 1'b1};

    heartbeat #(
        .CLKS_PER_BIT(434),
        .HELLO_EVERY(50000000),
        .BOARD("spartan3")
    ) dut (
        .clk(clk),
        .rst(~por[3]),
        .uart_rx(uart_rx),
        .uart_tx(uart_tx),
        .led(led)
    );
endmodule
