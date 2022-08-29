module coreir_reg #(
    parameter width = 1,
    parameter clk_posedge = 1,
    parameter init = 1
) (
    input clk,
    input [width-1:0] in,
    output [width-1:0] out
);
  reg [width-1:0] outReg=init;
  wire real_clk;
  assign real_clk = clk_posedge ? clk : ~clk;
  always @(posedge real_clk) begin
    outReg <= in;
  end
  assign out = outReg;
endmodule

module coreir_mux #(
    parameter width = 1
) (
    input [width-1:0] in0,
    input [width-1:0] in1,
    input sel,
    output [width-1:0] out
);
  assign out = sel ? in1 : in0;
endmodule

module coreir_eq #(
    parameter width = 1
) (
    input [width-1:0] in0,
    input [width-1:0] in1,
    output out
);
  assign out = in0 == in1;
endmodule

module coreir_const #(
    parameter width = 1,
    parameter value = 1
) (
    output [width-1:0] out
);
  assign out = value;
endmodule

module corebit_or (
    input in0,
    input in1,
    output out
);
  assign out = in0 | in1;
endmodule

module corebit_and (
    input in0,
    input in1,
    output out
);
  assign out = in0 & in1;
endmodule

module commonlib_muxn__N2__width4 (
    input [3:0] in_data [1:0],
    input [0:0] in_sel,
    output [3:0] out
);
wire [3:0] _join_out;
coreir_mux #(
    .width(4)
) _join (
    .in0(in_data[0]),
    .in1(in_data[1]),
    .sel(in_sel[0]),
    .out(_join_out)
);
assign out = _join_out;
endmodule

module commonlib_muxn__N2__width2 (
    input [1:0] in_data [1:0],
    input [0:0] in_sel,
    output [1:0] out
);
wire [1:0] _join_out;
coreir_mux #(
    .width(2)
) _join (
    .in0(in_data[0]),
    .in1(in_data[1]),
    .sel(in_sel[0]),
    .out(_join_out)
);
assign out = _join_out;
endmodule

module commonlib_muxn__N2__width16 (
    input [15:0] in_data [1:0],
    input [0:0] in_sel,
    output [15:0] out
);
wire [15:0] _join_out;
coreir_mux #(
    .width(16)
) _join (
    .in0(in_data[0]),
    .in1(in_data[1]),
    .sel(in_sel[0]),
    .out(_join_out)
);
assign out = _join_out;
endmodule

module Register (
    input [1:0] I,
    output [1:0] O,
    input CLK
);
wire [1:0] reg_P2_inst0_out;
coreir_reg #(
    .clk_posedge(1'b1),
    .init(2'h0),
    .width(2)
) reg_P2_inst0 (
    .clk(CLK),
    .in(I),
    .out(reg_P2_inst0_out)
);
assign O = reg_P2_inst0_out;
endmodule

module Mux2xBits4 (
    input [3:0] I0,
    input [3:0] I1,
    input S,
    output [3:0] O
);
wire [3:0] coreir_commonlib_mux2x4_inst0_out;
wire [3:0] coreir_commonlib_mux2x4_inst0_in_data [1:0];
assign coreir_commonlib_mux2x4_inst0_in_data[1] = I1;
assign coreir_commonlib_mux2x4_inst0_in_data[0] = I0;
commonlib_muxn__N2__width4 coreir_commonlib_mux2x4_inst0 (
    .in_data(coreir_commonlib_mux2x4_inst0_in_data),
    .in_sel(S),
    .out(coreir_commonlib_mux2x4_inst0_out)
);
assign O = coreir_commonlib_mux2x4_inst0_out;
endmodule

module Register_unq2 (
    input [3:0] I,
    output [3:0] O,
    input CE,
    input CLK
);
wire [3:0] enable_mux_O;
wire [3:0] reg_P4_inst0_out;
Mux2xBits4 enable_mux (
    .I0(reg_P4_inst0_out),
    .I1(I),
    .S(CE),
    .O(enable_mux_O)
);
coreir_reg #(
    .clk_posedge(1'b1),
    .init(4'h0),
    .width(4)
) reg_P4_inst0 (
    .clk(CLK),
    .in(enable_mux_O),
    .out(reg_P4_inst0_out)
);
assign O = reg_P4_inst0_out;
endmodule

module Mux2xBits2 (
    input [1:0] I0,
    input [1:0] I1,
    input S,
    output [1:0] O
);
wire [1:0] coreir_commonlib_mux2x2_inst0_out;
wire [1:0] coreir_commonlib_mux2x2_inst0_in_data [1:0];
assign coreir_commonlib_mux2x2_inst0_in_data[1] = I1;
assign coreir_commonlib_mux2x2_inst0_in_data[0] = I0;
commonlib_muxn__N2__width2 coreir_commonlib_mux2x2_inst0 (
    .in_data(coreir_commonlib_mux2x2_inst0_in_data),
    .in_sel(S),
    .out(coreir_commonlib_mux2x2_inst0_out)
);
assign O = coreir_commonlib_mux2x2_inst0_out;
endmodule

module Mux2xBits16 (
    input [15:0] I0,
    input [15:0] I1,
    input S,
    output [15:0] O
);
wire [15:0] coreir_commonlib_mux2x16_inst0_out;
wire [15:0] coreir_commonlib_mux2x16_inst0_in_data [1:0];
assign coreir_commonlib_mux2x16_inst0_in_data[1] = I1;
assign coreir_commonlib_mux2x16_inst0_in_data[0] = I0;
commonlib_muxn__N2__width16 coreir_commonlib_mux2x16_inst0 (
    .in_data(coreir_commonlib_mux2x16_inst0_in_data),
    .in_sel(S),
    .out(coreir_commonlib_mux2x16_inst0_out)
);
assign O = coreir_commonlib_mux2x16_inst0_out;
endmodule

module Register_unq1 (
    input [15:0] I,
    output [15:0] O,
    input CE,
    input CLK
);
wire [15:0] enable_mux_O;
wire [15:0] reg_P16_inst0_out;
Mux2xBits16 enable_mux (
    .I0(reg_P16_inst0_out),
    .I1(I),
    .S(CE),
    .O(enable_mux_O)
);
coreir_reg #(
    .clk_posedge(1'b1),
    .init(16'h0000),
    .width(16)
) reg_P16_inst0 (
    .clk(CLK),
    .in(enable_mux_O),
    .out(reg_P16_inst0_out)
);
assign O = reg_P16_inst0_out;
endmodule

module StateMachine (
    input [15:0] receive,
    input [3:0] offer,
    output [15:0] send,
    output [1:0] current_state,
    input CLK
);
wire [15:0] Mux2xBits16_inst0_O;
wire [15:0] Mux2xBits16_inst1_O;
wire [15:0] Mux2xBits16_inst2_O;
wire [15:0] Mux2xBits16_inst3_O;
wire [15:0] Mux2xBits16_inst4_O;
wire [1:0] Mux2xBits2_inst0_O;
wire [1:0] Mux2xBits2_inst1_O;
wire [1:0] Mux2xBits2_inst2_O;
wire [1:0] Mux2xBits2_inst3_O;
wire [1:0] Mux2xBits2_inst4_O;
wire [1:0] Register_inst0_O;
wire [15:0] Register_inst1_O;
wire [15:0] Register_inst2_O;
wire [3:0] Register_inst3_O;
wire [15:0] Register_inst4_O;
wire [15:0] const_0_16_out;
wire [1:0] const_0_2_out;
wire [3:0] const_0_4_out;
wire [15:0] const_1_16_out;
wire [1:0] const_1_2_out;
wire [3:0] const_1_4_out;
wire [1:0] const_2_2_out;
wire [1:0] const_3_2_out;
wire magma_Bit_and_inst0_out;
wire magma_Bit_and_inst1_out;
wire magma_Bit_and_inst2_out;
wire magma_Bit_and_inst3_out;
wire magma_Bit_or_inst0_out;
wire magma_Bits_2_eq_inst0_out;
wire magma_Bits_2_eq_inst1_out;
wire magma_Bits_2_eq_inst10_out;
wire magma_Bits_2_eq_inst2_out;
wire magma_Bits_2_eq_inst3_out;
wire magma_Bits_2_eq_inst4_out;
wire magma_Bits_2_eq_inst5_out;
wire magma_Bits_2_eq_inst6_out;
wire magma_Bits_2_eq_inst7_out;
wire magma_Bits_2_eq_inst8_out;
wire magma_Bits_2_eq_inst9_out;
wire magma_Bits_4_eq_inst0_out;
wire magma_Bits_4_eq_inst1_out;
wire magma_Bits_4_eq_inst2_out;
wire magma_Bits_4_eq_inst3_out;
Mux2xBits16 Mux2xBits16_inst0 (
    .I0(const_0_16_out),
    .I1(const_1_16_out),
    .S(magma_Bits_2_eq_inst8_out),
    .O(Mux2xBits16_inst0_O)
);
Mux2xBits16 Mux2xBits16_inst1 (
    .I0(Mux2xBits16_inst0_O),
    .I1(const_0_16_out),
    .S(magma_Bit_and_inst1_out),
    .O(Mux2xBits16_inst1_O)
);
Mux2xBits16 Mux2xBits16_inst2 (
    .I0(Mux2xBits16_inst1_O),
    .I1(const_0_16_out),
    .S(magma_Bit_and_inst0_out),
    .O(Mux2xBits16_inst2_O)
);
Mux2xBits16 Mux2xBits16_inst3 (
    .I0(const_0_16_out),
    .I1(Register_inst2_O),
    .S(magma_Bits_2_eq_inst5_out),
    .O(Mux2xBits16_inst3_O)
);
Mux2xBits16 Mux2xBits16_inst4 (
    .I0(Mux2xBits16_inst2_O),
    .I1(const_0_16_out),
    .S(magma_Bits_2_eq_inst5_out),
    .O(Mux2xBits16_inst4_O)
);
Mux2xBits2 Mux2xBits2_inst0 (
    .I0(const_3_2_out),
    .I1(const_1_2_out),
    .S(magma_Bit_and_inst2_out),
    .O(Mux2xBits2_inst0_O)
);
Mux2xBits2 Mux2xBits2_inst1 (
    .I0(Mux2xBits2_inst0_O),
    .I1(const_3_2_out),
    .S(magma_Bits_2_eq_inst8_out),
    .O(Mux2xBits2_inst1_O)
);
Mux2xBits2 Mux2xBits2_inst2 (
    .I0(Mux2xBits2_inst1_O),
    .I1(const_2_2_out),
    .S(magma_Bit_and_inst1_out),
    .O(Mux2xBits2_inst2_O)
);
Mux2xBits2 Mux2xBits2_inst3 (
    .I0(Mux2xBits2_inst2_O),
    .I1(const_1_2_out),
    .S(magma_Bit_and_inst0_out),
    .O(Mux2xBits2_inst3_O)
);
Mux2xBits2 Mux2xBits2_inst4 (
    .I0(Mux2xBits2_inst3_O),
    .I1(const_1_2_out),
    .S(magma_Bits_2_eq_inst5_out),
    .O(Mux2xBits2_inst4_O)
);
Register Register_inst0 (
    .I(Mux2xBits2_inst4_O),
    .O(Register_inst0_O),
    .CLK(CLK)
);
Register_unq1 Register_inst1 (
    .I(Mux2xBits16_inst4_O),
    .O(Register_inst1_O),
    .CE(magma_Bits_2_eq_inst2_out),
    .CLK(CLK)
);
Register_unq1 Register_inst2 (
    .I(receive),
    .O(Register_inst2_O),
    .CE(magma_Bits_2_eq_inst0_out),
    .CLK(CLK)
);
Register_unq2 Register_inst3 (
    .I(offer),
    .O(Register_inst3_O),
    .CE(magma_Bit_or_inst0_out),
    .CLK(CLK)
);
Register_unq1 Register_inst4 (
    .I(Mux2xBits16_inst3_O),
    .O(Register_inst4_O),
    .CE(magma_Bits_2_eq_inst1_out),
    .CLK(CLK)
);
coreir_const #(
    .value(16'h0000),
    .width(16)
) const_0_16 (
    .out(const_0_16_out)
);
coreir_const #(
    .value(2'h0),
    .width(2)
) const_0_2 (
    .out(const_0_2_out)
);
coreir_const #(
    .value(4'h0),
    .width(4)
) const_0_4 (
    .out(const_0_4_out)
);
coreir_const #(
    .value(16'h0001),
    .width(16)
) const_1_16 (
    .out(const_1_16_out)
);
coreir_const #(
    .value(2'h1),
    .width(2)
) const_1_2 (
    .out(const_1_2_out)
);
coreir_const #(
    .value(4'h1),
    .width(4)
) const_1_4 (
    .out(const_1_4_out)
);
coreir_const #(
    .value(2'h2),
    .width(2)
) const_2_2 (
    .out(const_2_2_out)
);
coreir_const #(
    .value(2'h3),
    .width(2)
) const_3_2 (
    .out(const_3_2_out)
);
corebit_and magma_Bit_and_inst0 (
    .in0(magma_Bits_2_eq_inst6_out),
    .in1(magma_Bits_4_eq_inst0_out),
    .out(magma_Bit_and_inst0_out)
);
corebit_and magma_Bit_and_inst1 (
    .in0(magma_Bits_2_eq_inst7_out),
    .in1(magma_Bits_4_eq_inst1_out),
    .out(magma_Bit_and_inst1_out)
);
corebit_and magma_Bit_and_inst2 (
    .in0(magma_Bits_2_eq_inst9_out),
    .in1(magma_Bits_4_eq_inst2_out),
    .out(magma_Bit_and_inst2_out)
);
corebit_and magma_Bit_and_inst3 (
    .in0(magma_Bits_2_eq_inst10_out),
    .in1(magma_Bits_4_eq_inst3_out),
    .out(magma_Bit_and_inst3_out)
);
corebit_or magma_Bit_or_inst0 (
    .in0(magma_Bits_2_eq_inst3_out),
    .in1(magma_Bits_2_eq_inst4_out),
    .out(magma_Bit_or_inst0_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst0 (
    .in0(Register_inst0_O),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst0_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst1 (
    .in0(Register_inst0_O),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst1_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst10 (
    .in0(Register_inst0_O),
    .in1(const_3_2_out),
    .out(magma_Bits_2_eq_inst10_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst2 (
    .in0(Register_inst0_O),
    .in1(const_2_2_out),
    .out(magma_Bits_2_eq_inst2_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst3 (
    .in0(Register_inst0_O),
    .in1(const_1_2_out),
    .out(magma_Bits_2_eq_inst3_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst4 (
    .in0(Register_inst0_O),
    .in1(const_3_2_out),
    .out(magma_Bits_2_eq_inst4_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst5 (
    .in0(Register_inst0_O),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst5_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst6 (
    .in0(Register_inst0_O),
    .in1(const_1_2_out),
    .out(magma_Bits_2_eq_inst6_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst7 (
    .in0(Register_inst0_O),
    .in1(const_1_2_out),
    .out(magma_Bits_2_eq_inst7_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst8 (
    .in0(Register_inst0_O),
    .in1(const_2_2_out),
    .out(magma_Bits_2_eq_inst8_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst9 (
    .in0(Register_inst0_O),
    .in1(const_3_2_out),
    .out(magma_Bits_2_eq_inst9_out)
);
coreir_eq #(
    .width(4)
) magma_Bits_4_eq_inst0 (
    .in0(Register_inst3_O),
    .in1(const_0_4_out),
    .out(magma_Bits_4_eq_inst0_out)
);
coreir_eq #(
    .width(4)
) magma_Bits_4_eq_inst1 (
    .in0(Register_inst3_O),
    .in1(const_1_4_out),
    .out(magma_Bits_4_eq_inst1_out)
);
coreir_eq #(
    .width(4)
) magma_Bits_4_eq_inst2 (
    .in0(Register_inst3_O),
    .in1(const_0_4_out),
    .out(magma_Bits_4_eq_inst2_out)
);
coreir_eq #(
    .width(4)
) magma_Bits_4_eq_inst3 (
    .in0(Register_inst3_O),
    .in1(const_1_4_out),
    .out(magma_Bits_4_eq_inst3_out)
);
assign send = Register_inst1_O;
assign current_state = Register_inst0_O;
endmodule

