// One-shot I2C probe of ADV7183B write address 0x40.
// sda_low and scl_low are open-drain drives. The FPGA top turns them into inout wires.
// The UART line is VDEC1,ACK ,<8 hex cycles> or VDEC1,NACK,<8 hex cycles>.
module i2c_probe #(
    parameter integer CLKS_PER_BIT     = 434,
    parameter integer CLKS_PER_QUARTER = 125
) (
    input  wire clk,
    input  wire rst,
    input  wire sda_in,
    output reg  sda_low,
    output reg  scl_low,
    output wire uart_tx
);
    localparam [2:0] ST_IDLE  = 3'd0;
    localparam [2:0] ST_START = 3'd1;
    localparam [2:0] ST_BITS  = 3'd2;
    localparam [2:0] ST_STOP  = 3'd3;
    localparam [2:0] ST_UART  = 3'd4;
    localparam [2:0] ST_DONE  = 3'd5;
    localparam [7:0] ADDR     = 8'h40;

    reg [2:0]  state;
    reg [1:0]  phase;
    reg [15:0] quarter;
    reg [3:0]  bit_i;
    reg        ack;
    reg        sampled;
    reg [31:0] cycle;
    reg [4:0]  uidx;
    reg        tx_start;
    reg [7:0]  tx_data;
    wire       tx_busy;

    uart_tx #(.CLKS_PER_BIT(CLKS_PER_BIT)) utx (
        .clk(clk),
        .rst(rst),
        .start(tx_start),
        .data(tx_data),
        .tx(uart_tx),
        .busy(tx_busy)
    );

    function [7:0] hexdig;
        input [3:0] n;
        begin
            if (n < 4'd10)
                hexdig = 8'h30 + {4'd0, n};
            else
                hexdig = 8'h41 + {4'd0, n} - 8'd10;
        end
    endfunction

    function [7:0] line_byte;
        input        got_ack;
        input [31:0] cyc;
        input [4:0]  i;
        reg [31:0] status;
        reg [1:0] status_i;
        begin
            status = got_ack ? "ACK " : "NACK";
            // Indexes stay inside the vectors for every value of i. XST does
            // not limit a part select to the branch that uses it.
            status_i = (5'd9 - i);
            if (i == 5'd0) line_byte = "V";
            else if (i == 5'd1) line_byte = "D";
            else if (i == 5'd2) line_byte = "E";
            else if (i == 5'd3) line_byte = "C";
            else if (i == 5'd4) line_byte = "1";
            else if (i == 5'd5) line_byte = ",";
            else if (i < 5'd10) line_byte = status[{status_i, 3'b000} +: 8];
            else if (i == 5'd10) line_byte = ",";
            else if (i == 5'd11) line_byte = hexdig(cyc[31:28]);
            else if (i == 5'd12) line_byte = hexdig(cyc[27:24]);
            else if (i == 5'd13) line_byte = hexdig(cyc[23:20]);
            else if (i == 5'd14) line_byte = hexdig(cyc[19:16]);
            else if (i == 5'd15) line_byte = hexdig(cyc[15:12]);
            else if (i == 5'd16) line_byte = hexdig(cyc[11:8]);
            else if (i == 5'd17) line_byte = hexdig(cyc[7:4]);
            else if (i == 5'd18) line_byte = hexdig(cyc[3:0]);
            else line_byte = 8'h0A;
        end
    endfunction

    always @(posedge clk) begin
        if (rst) begin
            state    <= ST_IDLE;
            phase    <= 2'd0;
            quarter  <= 16'd0;
            bit_i    <= 4'd0;
            ack      <= 1'b0;
            sampled  <= 1'b0;
            cycle    <= 32'd0;
            sda_low  <= 1'b0;
            scl_low  <= 1'b0;
            uidx     <= 5'd0;
            tx_start <= 1'b0;
            tx_data  <= 8'd0;
        end else begin
            cycle    <= cycle + 32'd1;
            tx_start <= 1'b0;
            case (state)
                ST_IDLE: begin
                    sda_low <= 1'b0;
                    scl_low <= 1'b0;
                    state   <= ST_START;
                    phase   <= 2'd0;
                    quarter <= 16'd0;
                end
                ST_START: begin
                    scl_low <= 1'b0;
                    sda_low <= (phase != 2'd0);
                    if (quarter == CLKS_PER_QUARTER - 1) begin
                        quarter <= 16'd0;
                        if (phase == 2'd1) begin
                            state <= ST_BITS;
                            phase <= 2'd0;
                            bit_i <= 4'd0;
                        end else begin
                            phase <= phase + 2'd1;
                        end
                    end else begin
                        quarter <= quarter + 16'd1;
                    end
                end
                ST_BITS: begin
                    scl_low <= (phase == 2'd0) || (phase == 2'd3);
                    if (bit_i < 4'd8)
                        sda_low <= ~ADDR[7 - bit_i];
                    else
                        sda_low <= 1'b0;
                    if (phase == 2'd2 && bit_i == 4'd8 && !sampled) begin
                        ack     <= (sda_in == 1'b0);
                        sampled <= 1'b1;
                    end
                    if (quarter == CLKS_PER_QUARTER - 1) begin
                        quarter <= 16'd0;
                        if (phase == 2'd3) begin
                            phase <= 2'd0;
                            if (bit_i == 4'd8)
                                state <= ST_STOP;
                            else
                                bit_i <= bit_i + 4'd1;
                        end else begin
                            phase <= phase + 2'd1;
                        end
                    end else begin
                        quarter <= quarter + 16'd1;
                    end
                end
                ST_STOP: begin
                    scl_low <= (phase == 2'd0);
                    sda_low <= (phase != 2'd2);
                    if (quarter == CLKS_PER_QUARTER - 1) begin
                        quarter <= 16'd0;
                        if (phase == 2'd2) begin
                            state <= ST_UART;
                            uidx  <= 5'd0;
                        end else begin
                            phase <= phase + 2'd1;
                        end
                    end else begin
                        quarter <= quarter + 16'd1;
                    end
                end
                ST_UART: begin
                    sda_low <= 1'b0;
                    scl_low <= 1'b0;
                    if (!tx_busy && !tx_start) begin
                        tx_data  <= line_byte(ack, cycle, uidx);
                        tx_start <= 1'b1;
                        if (uidx == 5'd19)
                            state <= ST_DONE;
                        else
                            uidx <= uidx + 5'd1;
                    end
                end
                default: begin
                    sda_low <= 1'b0;
                    scl_low <= 1'b0;
                end
            endcase
        end
    end
endmodule
