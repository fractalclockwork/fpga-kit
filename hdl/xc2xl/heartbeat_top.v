// Probe pattern for J4. Pins 1-3 are power. Pin 4 is the button (GSR).
// A single high walks J4 pins 5 through 40, about 0.6 s on each pin
// at 1.8432 MHz. With no clock, pin 5 stays high and the rest stay low.
// LD2 flashes on its own, about 3.5 times a second, and stays on with no clock.
module heartbeat_top (
    input  wire        clk,
    output wire        led,
    output wire [35:0] io
);
    reg [35:0] walk = 36'b1;
    reg [19:0] div = 20'd0;

    always @(posedge clk) begin
        div <= div + 20'd1;
        if (div == 20'hfffff)
            walk <= {walk[34:0], walk[35]};
    end

    assign io = walk;
    assign led = div[18];
endmodule
