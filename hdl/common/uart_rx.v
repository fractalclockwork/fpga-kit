// UART receiver, 8 data bits, no parity, one stop bit.
// valid is high for one clock when data holds a received byte.
module uart_rx #(
    parameter integer CLKS_PER_BIT = 434
) (
    input  wire       clk,
    input  wire       rst,
    input  wire       rx,
    output reg  [7:0] data,
    output reg        valid
);
    localparam [1:0] IDLE  = 2'd0;
    localparam [1:0] START = 2'd1;
    localparam [1:0] DATA  = 2'd2;
    localparam [1:0] STOP  = 2'd3;

    reg [1:0]  state;
    reg [15:0] clk_cnt;
    reg [2:0]  bit_idx;
    reg [7:0]  shift;
    reg        rx_q;

    always @(posedge clk) begin
        if (rst) begin
            state   <= IDLE;
            clk_cnt <= 16'd0;
            bit_idx <= 3'd0;
            shift   <= 8'd0;
            data    <= 8'd0;
            valid   <= 1'b0;
            rx_q    <= 1'b1;
        end else begin
            rx_q  <= rx;
            valid <= 1'b0;
            case (state)
                IDLE: begin
                    if (rx_q == 1'b0) begin
                        clk_cnt <= 16'd0;
                        state   <= START;
                    end
                end
                START: begin
                    // (CLKS_PER_BIT-1)/2 lands on the middle of the start bit
                    // after the one-clock synchronizer, including when
                    // CLKS_PER_BIT is only a few clocks in simulation.
                    if (clk_cnt == (CLKS_PER_BIT - 1) / 2) begin
                        if (rx_q == 1'b0) begin
                            clk_cnt <= 16'd0;
                            bit_idx <= 3'd0;
                            state   <= DATA;
                        end else begin
                            state <= IDLE;
                        end
                    end else begin
                        clk_cnt <= clk_cnt + 16'd1;
                    end
                end
                DATA: begin
                    if (clk_cnt == CLKS_PER_BIT - 1) begin
                        clk_cnt <= 16'd0;
                        shift   <= {rx_q, shift[7:1]};
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
                    if (clk_cnt == CLKS_PER_BIT - 1) begin
                        data  <= shift;
                        valid <= 1'b1;
                        state <= IDLE;
                    end else begin
                        clk_cnt <= clk_cnt + 16'd1;
                    end
                end
                default: state <= IDLE;
            endcase
        end
    end
endmodule
