// Periodic HELLO line, plus a PONG reply to the command PING.
// Wire format:
//   HELLO,<8-char board>,<8 hex cycles>
//   PONG,<8-char board>,<8 hex cycles>
// The cycle field is the free-running clock counter when the line is sent.
module heartbeat #(
    parameter integer CLKS_PER_BIT = 434,
    parameter integer HELLO_EVERY  = 50000000,
    parameter [63:0]  BOARD        = "board   "
) (
    input  wire clk,
    input  wire rst,
    input  wire uart_rx,
    output wire uart_tx,
    output wire led
);
    reg [31:0] cycle;
    reg [31:0] hello_cnt;
    reg        hello_due;
    reg        pong_due;
    reg [4:0]  idx;
    reg        sending;
    reg        is_pong;
    reg [31:0] snap;
    reg [7:0]  tx_data;
    reg        tx_start;
    wire       tx_busy;
    wire [7:0] rx_data;
    wire       rx_valid;
    reg [31:0] rx_word;

    uart_tx #(.CLKS_PER_BIT(CLKS_PER_BIT)) utx (
        .clk(clk),
        .rst(rst),
        .start(tx_start),
        .data(tx_data),
        .tx(uart_tx),
        .busy(tx_busy)
    );

    uart_rx #(.CLKS_PER_BIT(CLKS_PER_BIT)) urx (
        .clk(clk),
        .rst(rst),
        .rx(uart_rx),
        .data(rx_data),
        .valid(rx_valid)
    );

    assign led = cycle[26];

    function [7:0] hexdig;
        input [3:0] n;
        begin
            if (n < 4'd10)
                hexdig = 8'h30 + {4'd0, n};
            else
                hexdig = 8'h41 + {4'd0, n} - 8'd10;
        end
    endfunction

    // Byte i of "HELLO,<board>,<hex>\n" or "PONG,<board>,<hex>\n".
    // HELLO is one character longer, so the board field starts one index later.
    function [7:0] msg_byte;
        input        pong;
        input [31:0] cyc;
        input [4:0]  i;
        reg [4:0] tag_len;
        reg [4:0] at;
        begin
            tag_len = pong ? 5'd4 : 5'd5;
            if (i < tag_len) begin
                if (pong) begin
                    case (i)
                        5'd0: msg_byte = "P";
                        5'd1: msg_byte = "O";
                        5'd2: msg_byte = "N";
                        default: msg_byte = "G";
                    endcase
                end else begin
                    case (i)
                        5'd0: msg_byte = "H";
                        5'd1: msg_byte = "E";
                        5'd2: msg_byte = "L";
                        5'd3: msg_byte = "L";
                        default: msg_byte = "O";
                    endcase
                end
            end else if (i == tag_len) begin
                msg_byte = ",";
            end else begin
                at = i - tag_len - 5'd1;
                // Constant slices. Spartan-3 XST rejects a variable part select
                // even inside the branch that keeps the index in range.
                if (at < 5'd8) begin
                    case (at[2:0])
                        3'd0: msg_byte = BOARD[63:56];
                        3'd1: msg_byte = BOARD[55:48];
                        3'd2: msg_byte = BOARD[47:40];
                        3'd3: msg_byte = BOARD[39:32];
                        3'd4: msg_byte = BOARD[31:24];
                        3'd5: msg_byte = BOARD[23:16];
                        3'd6: msg_byte = BOARD[15:8];
                        default: msg_byte = BOARD[7:0];
                    endcase
                end else if (at == 5'd8)
                    msg_byte = ",";
                else if (at < 5'd17) begin
                    case (at - 5'd9)
                        5'd0: msg_byte = hexdig(cyc[31:28]);
                        5'd1: msg_byte = hexdig(cyc[27:24]);
                        5'd2: msg_byte = hexdig(cyc[23:20]);
                        5'd3: msg_byte = hexdig(cyc[19:16]);
                        5'd4: msg_byte = hexdig(cyc[15:12]);
                        5'd5: msg_byte = hexdig(cyc[11:8]);
                        5'd6: msg_byte = hexdig(cyc[7:4]);
                        default: msg_byte = hexdig(cyc[3:0]);
                    endcase
                end else
                    msg_byte = 8'h0A;
            end
        end
    endfunction

    always @(posedge clk) begin
        if (rst) begin
            cycle     <= 32'd0;
            hello_cnt <= 32'd0;
            hello_due <= 1'b0;
            pong_due  <= 1'b0;
            idx       <= 5'd0;
            sending   <= 1'b0;
            is_pong   <= 1'b0;
            snap      <= 32'd0;
            tx_data   <= 8'd0;
            tx_start  <= 1'b0;
            rx_word   <= 32'd0;
        end else begin
            cycle    <= cycle + 32'd1;
            tx_start <= 1'b0;

            if (rx_valid) begin
                if (rx_data == 8'h0A || rx_data == 8'h0D) begin
                    if (rx_word == "PING")
                        pong_due <= 1'b1;
                    rx_word <= 32'd0;
                end else begin
                    rx_word <= {rx_word[23:0], rx_data};
                end
            end

            if (!hello_due && !sending) begin
                if (hello_cnt == HELLO_EVERY - 1) begin
                    hello_cnt <= 32'd0;
                    hello_due <= 1'b1;
                end else begin
                    hello_cnt <= hello_cnt + 32'd1;
                end
            end

            if (!sending && (pong_due || hello_due)) begin
                is_pong <= pong_due;
                snap    <= cycle;
                sending <= 1'b1;
                idx     <= 5'd0;
                if (pong_due)
                    pong_due <= 1'b0;
                else
                    hello_due <= 1'b0;
            end else if (sending && !tx_busy && !tx_start) begin
                tx_data  <= msg_byte(is_pong, snap, idx);
                tx_start <= 1'b1;
                // HELLO line is 24 bytes. PONG is 23 because its tag is shorter.
                if (idx == (is_pong ? 5'd22 : 5'd23))
                    sending <= 1'b0;
                else
                    idx <= idx + 5'd1;
            end
        end
    end
endmodule
