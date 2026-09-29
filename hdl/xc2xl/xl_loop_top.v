// J5 pin loopback on the XC9572XL. Short Digilent J5-5 to J5-6
// (CPLD pins 43 and 42). Pin 6 toggles; pin 5 must follow both levels.
// LD3 flashes ~3.5 Hz when both levels have matched; stays dark when open.
// Brief edge skew must not clear a good match (bad-counter sticky match).
module xl_loop_top (
    input  wire clk,
    input  wire loop_rx,
    output wire loop_tx,
    output wire led
);
    reg [19:0] div = 20'd0;
    reg        tx = 1'b0;
    reg [1:0]  rx_sync = 2'b11;
    reg [1:0]  matched = 2'b00;
    reg [7:0]  bad = 8'd0;

    always @(posedge clk) begin
        div <= div + 20'd1;
        if (div[15:0] == 16'd0)
            tx <= ~tx;
        rx_sync <= {rx_sync[0], loop_rx};

        if (rx_sync[1] != tx) begin
            if (bad == 8'hff)
                matched <= 2'b00;
            else
                bad <= bad + 8'd1;
        end else begin
            bad <= 8'd0;
            if (!tx)
                matched[0] <= 1'b1;
            else
                matched[1] <= 1'b1;
        end
    end

    assign loop_tx = tx;
    assign led = (matched == 2'b11) ? div[18] : 1'b1;
endmodule
