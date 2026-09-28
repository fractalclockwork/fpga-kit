module i2c_probe_top (
    input  wire clk,
    input  wire uart_rx,
    output wire uart_tx,
    inout  wire sda,
    inout  wire scl
);
    reg [3:0] por = 4'b0;
    wire sda_low;
    wire scl_low;
    wire sda_in = sda;
    always @(posedge clk)
        por <= {por[2:0], 1'b1};

    assign sda = sda_low ? 1'b0 : 1'bz;
    assign scl = scl_low ? 1'b0 : 1'bz;

    i2c_probe #(
        .CLKS_PER_BIT(434),
        .CLKS_PER_QUARTER(125)
    ) dut (
        .clk(clk),
        .rst(~por[3]),
        .sda_in(sda_in),
        .sda_low(sda_low),
        .scl_low(scl_low),
        .uart_tx(uart_tx)
    );
endmodule
