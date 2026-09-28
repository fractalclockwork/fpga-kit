// UART transmitter, 8 data bits, no parity, one stop bit. The line idles high.
module uart_tx #(
    parameter integer CLKS_PER_BIT = 434
) (
    input  wire       clk,
    input  wire       rst,
    input  wire       start,
    input  wire [7:0] data,
    output reg        tx,
    output reg        busy
);
    localparam [1:0] IDLE  = 2'd0;
    localparam [1:0] START = 2'd1;
    localparam [1:0] DATA  = 2'd2;
    localparam [1:0] STOP  = 2'd3;

    reg [1:0]  state;
    reg [15:0] clk_cnt;
    reg [2:0]  bit_idx;
    reg [7:0]  shift;

    always @(posedge clk) begin
        if (rst) begin
            state   <= IDLE;
            tx      <= 1'b1;
            busy    <= 1'b0;
            clk_cnt <= 16'd0;
            bit_idx <= 3'd0;
            shift   <= 8'd0;
        end else begin
            case (state)
                IDLE: begin
                    tx   <= 1'b1;
                    busy <= 1'b0;
                    if (start) begin
                        busy    <= 1'b1;
                        shift   <= data;
                        clk_cnt <= 16'd0;
                        state   <= START;
                    end
                end
                START: begin
                    tx   <= 1'b0;
                    busy <= 1'b1;
                    if (clk_cnt == CLKS_PER_BIT - 1) begin
                        clk_cnt <= 16'd0;
                        bit_idx <= 3'd0;
                        state   <= DATA;
                    end else begin
                        clk_cnt <= clk_cnt + 16'd1;
                    end
                end
                DATA: begin
                    tx   <= shift[0];
                    busy <= 1'b1;
                    if (clk_cnt == CLKS_PER_BIT - 1) begin
                        clk_cnt <= 16'd0;
                        shift   <= {1'b0, shift[7:1]};
                        if (bit_idx == 3'd7) begin
                            state <= STOP;
                        end else begin
                            bit_idx <= bit_idx + 3'd1;
                        end
                    end else begin
                        clk_cnt <= clk_cnt + 16'd1;
                    end
                end
                STOP: begin
                    tx   <= 1'b1;
                    busy <= 1'b1;
                    if (clk_cnt == CLKS_PER_BIT - 1) begin
                        clk_cnt <= 16'd0;
                        busy    <= 1'b0;
                        state   <= IDLE;
                    end else begin
                        clk_cnt <= clk_cnt + 16'd1;
                    end
                end
                default: state <= IDLE;
            endcase
        end
    end
endmodule
