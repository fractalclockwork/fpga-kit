module i2c_probe_sim (
    input  wire clk,
    input  wire rst,
    input  wire sda_in,
    output wire sda_low,
    output wire scl_low,
    output wire uart_tx
);
    i2c_probe #(
        .CLKS_PER_BIT(4),
        .CLKS_PER_QUARTER(4)
    ) dut (
        .clk(clk),
        .rst(rst),
        .sda_in(sda_in),
        .sda_low(sda_low),
        .scl_low(scl_low),
        .uart_tx(uart_tx)
    );
endmodule
