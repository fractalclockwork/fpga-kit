// XC2C256 UART on the 1.8432 MHz oscillator: 115200 baud is 16 clocks per bit.
// Lines are "HELLO,xc2xl" and "PONG,xc2xl". Digilent J4-5/6 = PA35/PA36.
// The full FPGA heartbeat does not fit in 256 macrocells.
module heartbeat_top (
    input  wire clk,
    input  wire uart_rx,
    output reg  uart_tx,
    output wire led
);
    reg [20:0] tmr = 21'd0;
    assign led = tmr[20];

    reg        rx_meta = 1'b1;
    reg        rx_q = 1'b1;
    reg [1:0]  rx_state = 2'd0;
    reg [3:0]  rx_div = 4'd0;
    reg [2:0]  rx_bit = 3'd0;
    reg [7:0]  rx_shift = 8'd0;
    reg [2:0]  ping = 3'd0;
    reg        pong_arm = 1'b0;
    reg        hello_arm = 1'b0;

    reg        tx_busy = 1'b0;
    reg        tx_is_pong = 1'b0;
    reg [3:0]  tx_div = 4'd0;
    reg [3:0]  tx_bit = 4'd0;
    reg [3:0]  tx_idx = 4'd0;
    reg [7:0]  tx_shift = 8'd0;

    function [7:0] msg_byte;
        input       pong;
        input [3:0] i;
        begin
            case (i)
                4'd0: msg_byte = pong ? "P" : "H";
                4'd1: msg_byte = pong ? "O" : "E";
                4'd2: msg_byte = pong ? "N" : "L";
                4'd3: msg_byte = pong ? "G" : "L";
                4'd4: msg_byte = pong ? "," : "O";
                4'd5: msg_byte = pong ? "x" : ",";
                4'd6: msg_byte = pong ? "c" : "x";
                4'd7: msg_byte = pong ? "2" : "c";
                4'd8: msg_byte = pong ? "x" : "2";
                4'd9: msg_byte = pong ? "l" : "x";
                4'd10: msg_byte = pong ? 8'h0A : "l";
                default: msg_byte = 8'h0A;
            endcase
        end
    endfunction

    initial uart_tx = 1'b1;

    always @(posedge clk) begin
        tmr <= tmr + 21'd1;
        rx_meta <= uart_rx;
        rx_q <= rx_meta;
        if (tmr == 21'h1FFFFF)
            hello_arm <= 1'b1;

        case (rx_state)
            2'd0: begin
                if (!rx_q) begin
                    rx_state <= 2'd1;
                    rx_div <= 4'd0;
                end
            end
            2'd1: begin
                rx_div <= rx_div + 4'd1;
                if (rx_div == 4'd7) begin
                    rx_div <= 4'd0;
                    if (!rx_q) begin
                        rx_state <= 2'd2;
                        rx_bit <= 3'd0;
                    end else
                        rx_state <= 2'd0;
                end
            end
            2'd2: begin
                rx_div <= rx_div + 4'd1;
                if (rx_div == 4'd15) begin
                    rx_shift <= {rx_q, rx_shift[7:1]};
                    rx_bit <= rx_bit + 3'd1;
                    if (rx_bit == 3'd7)
                        rx_state <= 2'd3;
                end
            end
            default: begin
                rx_div <= rx_div + 4'd1;
                if (rx_div == 4'd15) begin
                    rx_state <= 2'd0;
                    if (rx_q) begin
                        if (rx_shift == 8'h0A || rx_shift == 8'h0D) begin
                            if (ping == 3'd4)
                                pong_arm <= 1'b1;
                            ping <= 3'd0;
                        end else begin
                            case (ping)
                                3'd0: ping <= (rx_shift == "P") ? 3'd1 : 3'd0;
                                3'd1: ping <= (rx_shift == "I") ? 3'd2 : ((rx_shift == "P") ? 3'd1 : 3'd0);
                                3'd2: ping <= (rx_shift == "N") ? 3'd3 : ((rx_shift == "P") ? 3'd1 : 3'd0);
                                3'd3: ping <= (rx_shift == "G") ? 3'd4 : ((rx_shift == "P") ? 3'd1 : 3'd0);
                                default: ping <= (rx_shift == "P") ? 3'd1 : 3'd0;
                            endcase
                        end
                    end
                end
            end
        endcase

        if (!tx_busy) begin
            uart_tx <= 1'b1;
            if (pong_arm || hello_arm) begin
                tx_busy <= 1'b1;
                tx_is_pong <= pong_arm;
                tx_idx <= 4'd0;
                tx_bit <= 4'd0;
                tx_div <= 4'd0;
                tx_shift <= msg_byte(pong_arm, 4'd0);
                if (pong_arm)
                    pong_arm <= 1'b0;
                else
                    hello_arm <= 1'b0;
            end
        end else begin
            tx_div <= tx_div + 4'd1;
            if (tx_div == 4'd15) begin
                if (tx_bit == 4'd0) begin
                    uart_tx <= 1'b0;
                    tx_bit <= 4'd1;
                end else if (tx_bit <= 4'd8) begin
                    uart_tx <= tx_shift[0];
                    tx_shift <= {1'b0, tx_shift[7:1]};
                    tx_bit <= tx_bit + 4'd1;
                end else if (tx_bit == 4'd9) begin
                    uart_tx <= 1'b1;
                    tx_bit <= 4'd10;
                end else if (tx_idx == (tx_is_pong ? 4'd10 : 4'd11)) begin
                    tx_busy <= 1'b0;
                    uart_tx <= 1'b1;
                end else begin
                    tx_idx <= tx_idx + 4'd1;
                    tx_bit <= 4'd0;
                    tx_shift <= msg_byte(tx_is_pong, tx_idx + 4'd1);
                end
            end
        end
    end
endmodule
