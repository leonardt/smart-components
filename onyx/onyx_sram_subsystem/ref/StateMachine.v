module coreir_reg #(
    parameter width = 1,
    parameter clk_posedge = 1,
    parameter init = 1
) (
    input clk/*verilator public*/,
    input [width-1:0] in/*verilator public*/,
    output [width-1:0] out/*verilator public*/
);
  reg [width-1:0] outReg/*verilator public*/=init;
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
    input [width-1:0] in0/*verilator public*/,
    input [width-1:0] in1/*verilator public*/,
    input sel/*verilator public*/,
    output [width-1:0] out/*verilator public*/
);
  assign out = sel ? in1 : in0;
endmodule

module coreir_eq #(
    parameter width = 1
) (
    input [width-1:0] in0/*verilator public*/,
    input [width-1:0] in1/*verilator public*/,
    output out/*verilator public*/
);
  assign out = in0 == in1;
endmodule

module coreir_const #(
    parameter width = 1,
    parameter value = 1
) (
    output [width-1:0] out/*verilator public*/
);
  assign out = value;
endmodule

module corebit_or (
    input in0/*verilator public*/,
    input in1/*verilator public*/,
    output out/*verilator public*/
);
  assign out = in0 | in1;
endmodule

module commonlib_muxn__N2__width4 (
    input [3:0] in_data [1:0]/*verilator public*/,
    input [0:0] in_sel/*verilator public*/,
    output [3:0] out/*verilator public*/
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
    input [1:0] in_data [1:0]/*verilator public*/,
    input [0:0] in_sel/*verilator public*/,
    output [1:0] out/*verilator public*/
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
    input [15:0] in_data [1:0]/*verilator public*/,
    input [0:0] in_sel/*verilator public*/,
    output [15:0] out/*verilator public*/
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
    input [1:0] I/*verilator public*/,
    output [1:0] O/*verilator public*/,
    input CLK/*verilator public*/
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
    input [3:0] I0/*verilator public*/,
    input [3:0] I1/*verilator public*/,
    input S/*verilator public*/,
    output [3:0] O/*verilator public*/
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
    input [3:0] I/*verilator public*/,
    output [3:0] O/*verilator public*/,
    input CE/*verilator public*/,
    input CLK/*verilator public*/
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
    input [1:0] I0/*verilator public*/,
    input [1:0] I1/*verilator public*/,
    input S/*verilator public*/,
    output [1:0] O/*verilator public*/
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
    input [15:0] I0/*verilator public*/,
    input [15:0] I1/*verilator public*/,
    input S/*verilator public*/,
    output [15:0] O/*verilator public*/
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
    input [15:0] I/*verilator public*/,
    output [15:0] O/*verilator public*/,
    input CE/*verilator public*/,
    input CLK/*verilator public*/
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
    input [15:0] receive/*verilator public*/,
    input [3:0] offer/*verilator public*/,
    output [15:0] send/*verilator public*/,
    output [1:0] current_state/*verilator public*/,
    input CLK/*verilator public*/
);
wire [3:0] CommandFromClient_O;
wire [15:0] DataFromClient_O;
wire [15:0] DataToClient_O;
wire [15:0] Mux2xBits16_inst0_O;
wire [15:0] Mux2xBits16_inst1_O;
wire [15:0] Mux2xBits16_inst10_O;
wire [15:0] Mux2xBits16_inst11_O;
wire [15:0] Mux2xBits16_inst12_O;
wire [15:0] Mux2xBits16_inst2_O;
wire [15:0] Mux2xBits16_inst3_O;
wire [15:0] Mux2xBits16_inst4_O;
wire [15:0] Mux2xBits16_inst5_O;
wire [15:0] Mux2xBits16_inst6_O;
wire [15:0] Mux2xBits16_inst7_O;
wire [15:0] Mux2xBits16_inst8_O;
wire [15:0] Mux2xBits16_inst9_O;
wire [1:0] Mux2xBits2_inst0_O;
wire [1:0] Mux2xBits2_inst1_O;
wire [1:0] Mux2xBits2_inst2_O;
wire [1:0] Mux2xBits2_inst3_O;
wire [1:0] Mux2xBits2_inst4_O;
wire [1:0] Mux2xBits2_inst5_O;
wire [1:0] Mux2xBits2_inst6_O;
wire [3:0] Mux2xBits4_inst0_O;
wire [15:0] const_0_16_out;
wire [1:0] const_0_2_out;
wire [3:0] const_0_4_out;
wire [15:0] const_1_16_out;
wire [1:0] const_1_2_out;
wire [3:0] const_1_4_out;
wire [1:0] const_2_2_out;
wire [3:0] const_2_4_out;
wire [1:0] const_3_2_out;
wire [3:0] const_3_4_out;
wire magma_Bit_or_inst0_out;
wire magma_Bits_2_eq_inst0_out;
wire magma_Bits_2_eq_inst1_out;
wire magma_Bits_2_eq_inst2_out;
wire magma_Bits_2_eq_inst3_out;
wire magma_Bits_2_eq_inst4_out;
wire magma_Bits_2_eq_inst5_out;
wire magma_Bits_2_eq_inst6_out;
wire magma_Bits_2_eq_inst7_out;
wire magma_Bits_4_eq_inst0_out;
wire magma_Bits_4_eq_inst1_out;
wire magma_Bits_4_eq_inst2_out;
wire magma_Bits_4_eq_inst3_out;
wire [15:0] redundancy_reg_O;
wire [1:0] state_reg_O;
Register_unq2 CommandFromClient (
    .I(offer),
    .O(CommandFromClient_O),
    .CE(magma_Bit_or_inst0_out),
    .CLK(CLK)
);
Register_unq1 DataFromClient (
    .I(receive),
    .O(DataFromClient_O),
    .CE(magma_Bits_2_eq_inst1_out),
    .CLK(CLK)
);
Register_unq1 DataToClient (
    .I(Mux2xBits16_inst11_O),
    .O(DataToClient_O),
    .CE(magma_Bits_2_eq_inst2_out),
    .CLK(CLK)
);
Mux2xBits16 Mux2xBits16_inst0 (
    .I0(const_0_16_out),
    .I1(const_1_16_out),
    .S(magma_Bits_4_eq_inst0_out),
    .O(Mux2xBits16_inst0_O)
);
Mux2xBits16 Mux2xBits16_inst1 (
    .I0(const_0_16_out),
    .I1(DataFromClient_O),
    .S(magma_Bits_4_eq_inst3_out),
    .O(Mux2xBits16_inst1_O)
);
Mux2xBits16 Mux2xBits16_inst10 (
    .I0(Mux2xBits16_inst8_O),
    .I1(const_0_16_out),
    .S(magma_Bits_2_eq_inst5_out),
    .O(Mux2xBits16_inst10_O)
);
Mux2xBits16 Mux2xBits16_inst11 (
    .I0(Mux2xBits16_inst9_O),
    .I1(const_0_16_out),
    .S(magma_Bits_2_eq_inst5_out),
    .O(Mux2xBits16_inst11_O)
);
Mux2xBits16 Mux2xBits16_inst12 (
    .I0(const_0_16_out),
    .I1(DataFromClient_O),
    .S(magma_Bits_2_eq_inst5_out),
    .O(Mux2xBits16_inst12_O)
);
Mux2xBits16 Mux2xBits16_inst2 (
    .I0(Mux2xBits16_inst1_O),
    .I1(DataFromClient_O),
    .S(magma_Bits_4_eq_inst2_out),
    .O(Mux2xBits16_inst2_O)
);
Mux2xBits16 Mux2xBits16_inst3 (
    .I0(const_0_16_out),
    .I1(const_0_16_out),
    .S(magma_Bits_4_eq_inst2_out),
    .O(Mux2xBits16_inst3_O)
);
Mux2xBits16 Mux2xBits16_inst4 (
    .I0(Mux2xBits16_inst2_O),
    .I1(const_0_16_out),
    .S(magma_Bits_4_eq_inst1_out),
    .O(Mux2xBits16_inst4_O)
);
Mux2xBits16 Mux2xBits16_inst5 (
    .I0(Mux2xBits16_inst3_O),
    .I1(const_0_16_out),
    .S(magma_Bits_4_eq_inst1_out),
    .O(Mux2xBits16_inst5_O)
);
Mux2xBits16 Mux2xBits16_inst6 (
    .I0(const_0_16_out),
    .I1(Mux2xBits16_inst4_O),
    .S(magma_Bits_2_eq_inst7_out),
    .O(Mux2xBits16_inst6_O)
);
Mux2xBits16 Mux2xBits16_inst7 (
    .I0(const_0_16_out),
    .I1(Mux2xBits16_inst5_O),
    .S(magma_Bits_2_eq_inst7_out),
    .O(Mux2xBits16_inst7_O)
);
Mux2xBits16 Mux2xBits16_inst8 (
    .I0(Mux2xBits16_inst6_O),
    .I1(const_0_16_out),
    .S(magma_Bits_2_eq_inst6_out),
    .O(Mux2xBits16_inst8_O)
);
Mux2xBits16 Mux2xBits16_inst9 (
    .I0(Mux2xBits16_inst7_O),
    .I1(Mux2xBits16_inst0_O),
    .S(magma_Bits_2_eq_inst6_out),
    .O(Mux2xBits16_inst9_O)
);
Mux2xBits2 Mux2xBits2_inst0 (
    .I0(state_reg_O),
    .I1(const_3_2_out),
    .S(magma_Bits_4_eq_inst0_out),
    .O(Mux2xBits2_inst0_O)
);
Mux2xBits2 Mux2xBits2_inst1 (
    .I0(state_reg_O),
    .I1(const_3_2_out),
    .S(magma_Bits_4_eq_inst3_out),
    .O(Mux2xBits2_inst1_O)
);
Mux2xBits2 Mux2xBits2_inst2 (
    .I0(Mux2xBits2_inst1_O),
    .I1(const_3_2_out),
    .S(magma_Bits_4_eq_inst2_out),
    .O(Mux2xBits2_inst2_O)
);
Mux2xBits2 Mux2xBits2_inst3 (
    .I0(Mux2xBits2_inst2_O),
    .I1(const_1_2_out),
    .S(magma_Bits_4_eq_inst1_out),
    .O(Mux2xBits2_inst3_O)
);
Mux2xBits2 Mux2xBits2_inst4 (
    .I0(state_reg_O),
    .I1(Mux2xBits2_inst3_O),
    .S(magma_Bits_2_eq_inst7_out),
    .O(Mux2xBits2_inst4_O)
);
Mux2xBits2 Mux2xBits2_inst5 (
    .I0(Mux2xBits2_inst4_O),
    .I1(Mux2xBits2_inst0_O),
    .S(magma_Bits_2_eq_inst6_out),
    .O(Mux2xBits2_inst5_O)
);
Mux2xBits2 Mux2xBits2_inst6 (
    .I0(Mux2xBits2_inst5_O),
    .I1(const_1_2_out),
    .S(magma_Bits_2_eq_inst5_out),
    .O(Mux2xBits2_inst6_O)
);
Mux2xBits4 Mux2xBits4_inst0 (
    .I0(CommandFromClient_O),
    .I1(CommandFromClient_O),
    .S(magma_Bits_2_eq_inst6_out),
    .O(Mux2xBits4_inst0_O)
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
    .value(4'h2),
    .width(4)
) const_2_4 (
    .out(const_2_4_out)
);
coreir_const #(
    .value(2'h3),
    .width(2)
) const_3_2 (
    .out(const_3_2_out)
);
coreir_const #(
    .value(4'h3),
    .width(4)
) const_3_4 (
    .out(const_3_4_out)
);
corebit_or magma_Bit_or_inst0 (
    .in0(magma_Bits_2_eq_inst3_out),
    .in1(magma_Bits_2_eq_inst4_out),
    .out(magma_Bit_or_inst0_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst0 (
    .in0(state_reg_O),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst0_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst1 (
    .in0(state_reg_O),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst1_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst2 (
    .in0(state_reg_O),
    .in1(const_2_2_out),
    .out(magma_Bits_2_eq_inst2_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst3 (
    .in0(state_reg_O),
    .in1(const_1_2_out),
    .out(magma_Bits_2_eq_inst3_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst4 (
    .in0(state_reg_O),
    .in1(const_3_2_out),
    .out(magma_Bits_2_eq_inst4_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst5 (
    .in0(state_reg_O),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst5_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst6 (
    .in0(state_reg_O),
    .in1(const_1_2_out),
    .out(magma_Bits_2_eq_inst6_out)
);
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst7 (
    .in0(state_reg_O),
    .in1(const_3_2_out),
    .out(magma_Bits_2_eq_inst7_out)
);
coreir_eq #(
    .width(4)
) magma_Bits_4_eq_inst0 (
    .in0(CommandFromClient_O),
    .in1(const_1_4_out),
    .out(magma_Bits_4_eq_inst0_out)
);
coreir_eq #(
    .width(4)
) magma_Bits_4_eq_inst1 (
    .in0(CommandFromClient_O),
    .in1(const_0_4_out),
    .out(magma_Bits_4_eq_inst1_out)
);
coreir_eq #(
    .width(4)
) magma_Bits_4_eq_inst2 (
    .in0(CommandFromClient_O),
    .in1(const_2_4_out),
    .out(magma_Bits_4_eq_inst2_out)
);
coreir_eq #(
    .width(4)
) magma_Bits_4_eq_inst3 (
    .in0(CommandFromClient_O),
    .in1(const_3_4_out),
    .out(magma_Bits_4_eq_inst3_out)
);
Register_unq1 redundancy_reg (
    .I(Mux2xBits16_inst12_O),
    .O(redundancy_reg_O),
    .CE(magma_Bits_2_eq_inst0_out),
    .CLK(CLK)
);
Register state_reg (
    .I(Mux2xBits2_inst6_O),
    .O(state_reg_O),
    .CLK(CLK)
);
assign send = DataToClient_O;
assign current_state = state_reg_O;
endmodule
