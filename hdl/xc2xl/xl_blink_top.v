// XC9572XL blink on LD3. Clock is XLCLK (JP8) at 1.8432 MHz.
// led = cnt[19] toggles about 3.5 times a second. Active low through 510 ohm.
module xl_blink_top (
    input  wire clk,
    output wire led
);
    reg [19:0] cnt = 20'd0;
    always @(posedge clk)
        cnt <= cnt + 20'd1;
    assign led = cnt[19];
endmodule
