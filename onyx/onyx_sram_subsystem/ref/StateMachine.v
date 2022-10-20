module coreir_shl #(
    parameter width = 1
) (
    input [width-1:0] in0/*verilator public*/,
    input [width-1:0] in1/*verilator public*/,
    output [width-1:0] out/*verilator public*/
);
  assign out = in0 << in1;
endmodule

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

module coreir_or #(
    parameter width = 1
) (
    input [width-1:0] in0/*verilator public*/,
    input [width-1:0] in1/*verilator public*/,
    output [width-1:0] out/*verilator public*/
);
  assign out = in0 | in1;
endmodule

module coreir_not #(
    parameter width = 1
) (
    input [width-1:0] in/*verilator public*/,
    output [width-1:0] out/*verilator public*/
);
  assign out = ~in;
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

module coreir_mem #(
    parameter has_init = 1'b0,
    parameter sync_read = 1'b0,
    parameter depth = 1,
    parameter width = 1,
    parameter [(width * depth) - 1:0] init = 0
) (
    input clk/*verilator public*/,
    input [width-1:0] wdata/*verilator public*/,
    input [$clog2(depth)-1:0] waddr/*verilator public*/,
    input wen/*verilator public*/,
    output [width-1:0] rdata/*verilator public*/,
    input [$clog2(depth)-1:0] raddr/*verilator public*/
);
  reg [width-1:0] data [depth-1:0]/*verilator public*/;
  generate if (has_init) begin
    genvar j;
    for (j = 0; j < depth; j = j + 1) begin
      initial begin
        data[j] = init[(j+1)*width-1:j*width];
      end
    end
  end
  endgenerate
  always @(posedge clk) begin
    if (wen) begin
      data[waddr] <= wdata;
    end
  end
  generate if (sync_read) begin
  reg [width-1:0] rdata_reg;
  always @(posedge clk) begin
    rdata_reg <= data[raddr];
  end
  assign rdata = rdata_reg;
  end else begin
  assign rdata = data[raddr];
  end
  endgenerate

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

module corebit_not (
    input in/*verilator public*/,
    output out/*verilator public*/
);
  assign out = ~in;
endmodule

module corebit_const #(
    parameter value = 1
) (
    output out/*verilator public*/
);
  assign out = value;
endmodule

module corebit_and (
    input in0/*verilator public*/,
    input in1/*verilator public*/,
    output out/*verilator public*/
);
  assign out = in0 & in1;
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

module commonlib_muxn__N2__width3 (
    input [2:0] in_data [1:0]/*verilator public*/,
    input [0:0] in_sel/*verilator public*/,
    output [2:0] out/*verilator public*/
);
wire [2:0] _join_out;
coreir_mux #(
    .width(3)
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

module commonlib_muxn__N2__width11 (
    input [10:0] in_data [1:0]/*verilator public*/,
    input [0:0] in_sel/*verilator public*/,
    output [10:0] out/*verilator public*/
);
wire [10:0] _join_out;
coreir_mux #(
    .width(11)
) _join (
    .in0(in_data[0]),
    .in1(in_data[1]),
    .sel(in_sel[0]),
    .out(_join_out)
);
assign out = _join_out;
endmodule

module commonlib_muxn__N2__width1 (
    input [0:0] in_data [1:0]/*verilator public*/,
    input [0:0] in_sel/*verilator public*/,
    output [0:0] out/*verilator public*/
);
wire [0:0] _join_out;
coreir_mux #(
    .width(1)
) _join (
    .in0(in_data[0]),
    .in1(in_data[1]),
    .sel(in_sel[0]),
    .out(_join_out)
);
assign out = _join_out;
endmodule

module Register_unq6 (
    input [0:0] I/*verilator public*/,
    output [0:0] O/*verilator public*/,
    input CLK/*verilator public*/
);
wire [0:0] reg_P1_inst0_out;
coreir_reg #(
    .clk_posedge(1'b1),
    .init(1'h0),
    .width(1)
) reg_P1_inst0 (
    .clk(CLK),
    .in(I),
    .out(reg_P1_inst0_out)
);
assign O = reg_P1_inst0_out;
endmodule

module Register_unq4 (
    input I/*verilator public*/,
    output O/*verilator public*/,
    input CLK/*verilator public*/
);
wire [0:0] reg_P1_inst0_out;
coreir_reg #(
    .clk_posedge(1'b1),
    .init(1'h0),
    .width(1)
) reg_P1_inst0 (
    .clk(CLK),
    .in(I),
    .out(reg_P1_inst0_out)
);
assign O = reg_P1_inst0_out[0];
endmodule

module Register_unq1 (
    input [0:0] I/*verilator public*/,
    output [0:0] O/*verilator public*/,
    input CLK/*verilator public*/
);
wire [0:0] reg_P1_inst0_out;
coreir_reg #(
    .clk_posedge(1'b1),
    .init(1'h1),
    .width(1)
) reg_P1_inst0 (
    .clk(CLK),
    .in(I),
    .out(reg_P1_inst0_out)
);
assign O = reg_P1_inst0_out;
endmodule

module Register (
    input [2:0] I/*verilator public*/,
    output [2:0] O/*verilator public*/,
    input CLK/*verilator public*/
);
wire [2:0] reg_P3_inst0_out;
coreir_reg #(
    .clk_posedge(1'b1),
    .init(3'h0),
    .width(3)
) reg_P3_inst0 (
    .clk(CLK),
    .in(I),
    .out(reg_P3_inst0_out)
);
assign O = reg_P3_inst0_out;
endmodule

module Mux2xEnable (
    input I0/*verilator public*/,
    input I1/*verilator public*/,
    input S/*verilator public*/,
    output O/*verilator public*/
);
wire [0:0] coreir_commonlib_mux2x1_inst0_out;
wire [0:0] coreir_commonlib_mux2x1_inst0_in_data [1:0];
assign coreir_commonlib_mux2x1_inst0_in_data[1] = I1;
assign coreir_commonlib_mux2x1_inst0_in_data[0] = I0;
commonlib_muxn__N2__width1 coreir_commonlib_mux2x1_inst0 (
    .in_data(coreir_commonlib_mux2x1_inst0_in_data),
    .in_sel(S),
    .out(coreir_commonlib_mux2x1_inst0_out)
);
assign O = coreir_commonlib_mux2x1_inst0_out[0];
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

module Mux2xBits3 (
    input [2:0] I0/*verilator public*/,
    input [2:0] I1/*verilator public*/,
    input S/*verilator public*/,
    output [2:0] O/*verilator public*/
);
wire [2:0] coreir_commonlib_mux2x3_inst0_out;
wire [2:0] coreir_commonlib_mux2x3_inst0_in_data [1:0];
assign coreir_commonlib_mux2x3_inst0_in_data[1] = I1;
assign coreir_commonlib_mux2x3_inst0_in_data[0] = I0;
commonlib_muxn__N2__width3 coreir_commonlib_mux2x3_inst0 (
    .in_data(coreir_commonlib_mux2x3_inst0_in_data),
    .in_sel(S),
    .out(coreir_commonlib_mux2x3_inst0_out)
);
assign O = coreir_commonlib_mux2x3_inst0_out;
endmodule

module Register_unq5 (
    input [2:0] I/*verilator public*/,
    output [2:0] O/*verilator public*/,
    input CE/*verilator public*/,
    input CLK/*verilator public*/
);
wire [2:0] enable_mux_O;
wire [2:0] reg_P3_inst0_out;
Mux2xBits3 enable_mux (
    .I0(reg_P3_inst0_out),
    .I1(I),
    .S(CE),
    .O(enable_mux_O)
);
coreir_reg #(
    .clk_posedge(1'b1),
    .init(3'h0),
    .width(3)
) reg_P3_inst0 (
    .clk(CLK),
    .in(enable_mux_O),
    .out(reg_P3_inst0_out)
);
assign O = reg_P3_inst0_out;
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

module Register_unq2 (
    input [1:0] I/*verilator public*/,
    output [1:0] O/*verilator public*/,
    input CE/*verilator public*/,
    input CLK/*verilator public*/
);
wire [1:0] enable_mux_O;
wire [1:0] reg_P2_inst0_out;
Mux2xBits2 enable_mux (
    .I0(reg_P2_inst0_out),
    .I1(I),
    .S(CE),
    .O(enable_mux_O)
);
coreir_reg #(
    .clk_posedge(1'b1),
    .init(2'h0),
    .width(2)
) reg_P2_inst0 (
    .clk(CLK),
    .in(enable_mux_O),
    .out(reg_P2_inst0_out)
);
assign O = reg_P2_inst0_out;
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

module Register_unq3 (
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

module Mux2xBits11 (
    input [10:0] I0/*verilator public*/,
    input [10:0] I1/*verilator public*/,
    input S/*verilator public*/,
    output [10:0] O/*verilator public*/
);
wire [10:0] coreir_commonlib_mux2x11_inst0_out;
wire [10:0] coreir_commonlib_mux2x11_inst0_in_data [1:0];
assign coreir_commonlib_mux2x11_inst0_in_data[1] = I1;
assign coreir_commonlib_mux2x11_inst0_in_data[0] = I0;
commonlib_muxn__N2__width11 coreir_commonlib_mux2x11_inst0 (
    .in_data(coreir_commonlib_mux2x11_inst0_in_data),
    .in_sel(S),
    .out(coreir_commonlib_mux2x11_inst0_out)
);
assign O = coreir_commonlib_mux2x11_inst0_out;
endmodule

module Mux2xBits1 (
    input [0:0] I0/*verilator public*/,
    input [0:0] I1/*verilator public*/,
    input S/*verilator public*/,
    output [0:0] O/*verilator public*/
);
wire [0:0] coreir_commonlib_mux2x1_inst0_out;
wire [0:0] coreir_commonlib_mux2x1_inst0_in_data [1:0];
assign coreir_commonlib_mux2x1_inst0_in_data[1] = I1;
assign coreir_commonlib_mux2x1_inst0_in_data[0] = I0;
commonlib_muxn__N2__width1 coreir_commonlib_mux2x1_inst0 (
    .in_data(coreir_commonlib_mux2x1_inst0_in_data),
    .in_sel(S),
    .out(coreir_commonlib_mux2x1_inst0_out)
);
assign O = coreir_commonlib_mux2x1_inst0_out;
endmodule

module Mux2xBit (
    input I0/*verilator public*/,
    input I1/*verilator public*/,
    input S/*verilator public*/,
    output O/*verilator public*/
);
wire [0:0] coreir_commonlib_mux2x1_inst0_out;
wire [0:0] coreir_commonlib_mux2x1_inst0_in_data [1:0];
assign coreir_commonlib_mux2x1_inst0_in_data[1] = I1;
assign coreir_commonlib_mux2x1_inst0_in_data[0] = I0;
commonlib_muxn__N2__width1 coreir_commonlib_mux2x1_inst0 (
    .in_data(coreir_commonlib_mux2x1_inst0_in_data),
    .in_sel(S),
    .out(coreir_commonlib_mux2x1_inst0_out)
);
assign O = coreir_commonlib_mux2x1_inst0_out[0];
endmodule

module Memory (
    input [10:0] RADDR/*verilator public*/,
    output [3:0] RDATA/*verilator public*/,
    input CLK/*verilator public*/,
    input [10:0] WADDR/*verilator public*/,
    input [3:0] WDATA/*verilator public*/,
    input WE/*verilator public*/
);
wire [3:0] coreir_mem2048x4_inst0_rdata;
coreir_mem #(
    .depth(2048),
    .has_init(1'b0),
    .sync_read(1'b0),
    .width(4)
) coreir_mem2048x4_inst0 (
    .clk(CLK),
    .wdata(WDATA),
    .waddr(WADDR),
    .wen(WE),
    .rdata(coreir_mem2048x4_inst0_rdata),
    .raddr(RADDR)
);
assign RDATA = coreir_mem2048x4_inst0_rdata;
endmodule

module SRAMSMR (
    input CEn/*verilator public*/,
    input [15:0] WDATA/*verilator public*/,
    input WEn/*verilator public*/,
    output [15:0] RDATA/*verilator public*/,
    input REn/*verilator public*/,
    input CLK/*verilator public*/,
    input [10:0] ADDR/*verilator public*/,
    input [1:0] RCE/*verilator public*/,
    input [1:0] RCF0A/*verilator public*/,
    input [1:0] RCF1A/*verilator public*/,
    input deep_sleep/*verilator public*/,
    input power_gate/*verilator public*/,
    output wake_ack/*verilator public*/,
    output [1:0] current_state/*verilator public*/
);
wire [3:0] Memory_inst0_RDATA;
wire [3:0] Memory_inst1_RDATA;
wire [3:0] Memory_inst2_RDATA;
wire [3:0] Memory_inst3_RDATA;
wire [3:0] Memory_inst4_RDATA;
wire [3:0] Memory_inst5_RDATA;
wire [3:0] Mux2xBits4_inst0_O;
wire [3:0] Mux2xBits4_inst1_O;
wire [3:0] Mux2xBits4_inst10_O;
wire [3:0] Mux2xBits4_inst11_O;
wire [3:0] Mux2xBits4_inst12_O;
wire [3:0] Mux2xBits4_inst13_O;
wire [3:0] Mux2xBits4_inst14_O;
wire [3:0] Mux2xBits4_inst15_O;
wire [3:0] Mux2xBits4_inst2_O;
wire [3:0] Mux2xBits4_inst3_O;
wire [3:0] Mux2xBits4_inst4_O;
wire [3:0] Mux2xBits4_inst5_O;
wire [3:0] Mux2xBits4_inst6_O;
wire [3:0] Mux2xBits4_inst7_O;
wire [3:0] Mux2xBits4_inst8_O;
wire [3:0] Mux2xBits4_inst9_O;
wire [15:0] Register_inst0_O;
wire Register_inst1_O;
wire bit_const_0_None_out;
wire bit_const_1_None_out;
wire [1:0] const_0_2_out;
wire [3:0] const_0_4_out;
wire [3:0] const_1_4_out;
wire magma_Bit_and_inst0_out;
wire magma_Bit_and_inst1_out;
wire magma_Bit_and_inst10_out;
wire magma_Bit_and_inst11_out;
wire magma_Bit_and_inst12_out;
wire magma_Bit_and_inst13_out;
wire magma_Bit_and_inst14_out;
wire magma_Bit_and_inst15_out;
wire magma_Bit_and_inst16_out;
wire magma_Bit_and_inst17_out;
wire magma_Bit_and_inst18_out;
wire magma_Bit_and_inst19_out;
wire magma_Bit_and_inst2_out;
wire magma_Bit_and_inst20_out;
wire magma_Bit_and_inst21_out;
wire magma_Bit_and_inst22_out;
wire magma_Bit_and_inst23_out;
wire magma_Bit_and_inst24_out;
wire magma_Bit_and_inst25_out;
wire magma_Bit_and_inst26_out;
wire magma_Bit_and_inst27_out;
wire magma_Bit_and_inst28_out;
wire magma_Bit_and_inst29_out;
wire magma_Bit_and_inst3_out;
wire magma_Bit_and_inst30_out;
wire magma_Bit_and_inst31_out;
wire magma_Bit_and_inst32_out;
wire magma_Bit_and_inst33_out;
wire magma_Bit_and_inst34_out;
wire magma_Bit_and_inst35_out;
wire magma_Bit_and_inst36_out;
wire magma_Bit_and_inst37_out;
wire magma_Bit_and_inst38_out;
wire magma_Bit_and_inst39_out;
wire magma_Bit_and_inst4_out;
wire magma_Bit_and_inst40_out;
wire magma_Bit_and_inst41_out;
wire magma_Bit_and_inst42_out;
wire magma_Bit_and_inst5_out;
wire magma_Bit_and_inst6_out;
wire magma_Bit_and_inst7_out;
wire magma_Bit_and_inst8_out;
wire magma_Bit_and_inst9_out;
wire magma_Bit_not_inst0_out;
wire magma_Bit_not_inst1_out;
wire magma_Bit_not_inst10_out;
wire magma_Bit_not_inst2_out;
wire magma_Bit_not_inst3_out;
wire magma_Bit_not_inst4_out;
wire magma_Bit_not_inst5_out;
wire magma_Bit_not_inst6_out;
wire magma_Bit_not_inst7_out;
wire magma_Bit_not_inst8_out;
wire magma_Bit_not_inst9_out;
wire magma_Bit_or_inst0_out;
wire magma_Bit_or_inst1_out;
wire magma_Bit_or_inst10_out;
wire magma_Bit_or_inst11_out;
wire magma_Bit_or_inst12_out;
wire magma_Bit_or_inst13_out;
wire magma_Bit_or_inst14_out;
wire magma_Bit_or_inst15_out;
wire magma_Bit_or_inst2_out;
wire magma_Bit_or_inst3_out;
wire magma_Bit_or_inst4_out;
wire magma_Bit_or_inst5_out;
wire magma_Bit_or_inst6_out;
wire magma_Bit_or_inst7_out;
wire magma_Bit_or_inst8_out;
wire magma_Bit_or_inst9_out;
wire magma_Bits_2_eq_inst0_out;
wire magma_Bits_2_eq_inst1_out;
wire magma_Bits_2_eq_inst2_out;
wire magma_Bits_2_eq_inst3_out;
wire magma_Bits_2_eq_inst4_out;
wire magma_Bits_2_eq_inst5_out;
wire magma_Bits_2_eq_inst6_out;
wire magma_Bits_2_eq_inst7_out;
wire magma_Bits_2_eq_inst8_out;
wire [3:0] magma_Bits_4_or_inst0_out;
wire [3:0] magma_Bits_4_shl_inst0_out;
wire [3:0] magma_Bits_4_shl_inst1_out;
Memory Memory_inst0 (
    .RADDR(ADDR),
    .RDATA(Memory_inst0_RDATA),
    .CLK(CLK),
    .WADDR(ADDR),
    .WDATA(WDATA[3:0]),
    .WE(magma_Bit_and_inst16_out)
);
Memory Memory_inst1 (
    .RADDR(ADDR),
    .RDATA(Memory_inst1_RDATA),
    .CLK(CLK),
    .WADDR(ADDR),
    .WDATA(Mux2xBits4_inst10_O),
    .WE(magma_Bit_and_inst22_out)
);
Memory Memory_inst2 (
    .RADDR(ADDR),
    .RDATA(Memory_inst2_RDATA),
    .CLK(CLK),
    .WADDR(ADDR),
    .WDATA(Mux2xBits4_inst12_O),
    .WE(magma_Bit_and_inst28_out)
);
Memory Memory_inst3 (
    .RADDR(ADDR),
    .RDATA(Memory_inst3_RDATA),
    .CLK(CLK),
    .WADDR(ADDR),
    .WDATA(Mux2xBits4_inst14_O),
    .WE(magma_Bit_and_inst34_out)
);
Memory Memory_inst4 (
    .RADDR(ADDR),
    .RDATA(Memory_inst4_RDATA),
    .CLK(CLK),
    .WADDR(ADDR),
    .WDATA(Mux2xBits4_inst15_O),
    .WE(magma_Bit_and_inst38_out)
);
Memory Memory_inst5 (
    .RADDR(ADDR),
    .RDATA(Memory_inst5_RDATA),
    .CLK(CLK),
    .WADDR(ADDR),
    .WDATA(WDATA[15:12]),
    .WE(magma_Bit_and_inst42_out)
);
Mux2xBits4 Mux2xBits4_inst0 (
    .I0(const_0_4_out),
    .I1(magma_Bits_4_shl_inst0_out),
    .S(RCE[0]),
    .O(Mux2xBits4_inst0_O)
);
Mux2xBits4 Mux2xBits4_inst1 (
    .I0(const_0_4_out),
    .I1(magma_Bits_4_shl_inst1_out),
    .S(RCE[1]),
    .O(Mux2xBits4_inst1_O)
);
Mux2xBits4 Mux2xBits4_inst10 (
    .I0(WDATA[7:4]),
    .I1(WDATA[3:0]),
    .S(magma_Bit_or_inst10_out),
    .O(Mux2xBits4_inst10_O)
);
Mux2xBits4 Mux2xBits4_inst11 (
    .I0(WDATA[11:8]),
    .I1(WDATA[7:4]),
    .S(magma_Bit_or_inst12_out),
    .O(Mux2xBits4_inst11_O)
);
Mux2xBits4 Mux2xBits4_inst12 (
    .I0(Mux2xBits4_inst11_O),
    .I1(WDATA[3:0]),
    .S(magma_Bit_or_inst13_out),
    .O(Mux2xBits4_inst12_O)
);
Mux2xBits4 Mux2xBits4_inst13 (
    .I0(WDATA[15:12]),
    .I1(WDATA[11:8]),
    .S(magma_Bit_or_inst14_out),
    .O(Mux2xBits4_inst13_O)
);
Mux2xBits4 Mux2xBits4_inst14 (
    .I0(Mux2xBits4_inst13_O),
    .I1(WDATA[7:4]),
    .S(magma_Bit_or_inst15_out),
    .O(Mux2xBits4_inst14_O)
);
Mux2xBits4 Mux2xBits4_inst15 (
    .I0(WDATA[15:12]),
    .I1(WDATA[11:8]),
    .S(magma_Bit_or_inst15_out),
    .O(Mux2xBits4_inst15_O)
);
Mux2xBits4 Mux2xBits4_inst2 (
    .I0(Memory_inst0_RDATA),
    .I1(Memory_inst1_RDATA),
    .S(magma_Bit_or_inst0_out),
    .O(Mux2xBits4_inst2_O)
);
Mux2xBits4 Mux2xBits4_inst3 (
    .I0(Mux2xBits4_inst2_O),
    .I1(Memory_inst2_RDATA),
    .S(magma_Bit_or_inst1_out),
    .O(Mux2xBits4_inst3_O)
);
Mux2xBits4 Mux2xBits4_inst4 (
    .I0(Memory_inst1_RDATA),
    .I1(Memory_inst2_RDATA),
    .S(magma_Bit_or_inst2_out),
    .O(Mux2xBits4_inst4_O)
);
Mux2xBits4 Mux2xBits4_inst5 (
    .I0(Mux2xBits4_inst4_O),
    .I1(Memory_inst3_RDATA),
    .S(magma_Bit_or_inst3_out),
    .O(Mux2xBits4_inst5_O)
);
Mux2xBits4 Mux2xBits4_inst6 (
    .I0(Memory_inst2_RDATA),
    .I1(Memory_inst3_RDATA),
    .S(magma_Bit_or_inst4_out),
    .O(Mux2xBits4_inst6_O)
);
Mux2xBits4 Mux2xBits4_inst7 (
    .I0(Mux2xBits4_inst6_O),
    .I1(Memory_inst4_RDATA),
    .S(magma_Bit_or_inst5_out),
    .O(Mux2xBits4_inst7_O)
);
Mux2xBits4 Mux2xBits4_inst8 (
    .I0(Memory_inst3_RDATA),
    .I1(Memory_inst4_RDATA),
    .S(magma_Bit_or_inst6_out),
    .O(Mux2xBits4_inst8_O)
);
Mux2xBits4 Mux2xBits4_inst9 (
    .I0(Mux2xBits4_inst8_O),
    .I1(Memory_inst5_RDATA),
    .S(magma_Bit_or_inst7_out),
    .O(Mux2xBits4_inst9_O)
);
wire [15:0] Register_inst0_I;
assign Register_inst0_I = {Mux2xBits4_inst9_O,Mux2xBits4_inst7_O,Mux2xBits4_inst5_O,Mux2xBits4_inst3_O};
Register_unq3 Register_inst0 (
    .I(Register_inst0_I),
    .O(Register_inst0_O),
    .CE(magma_Bit_and_inst10_out),
    .CLK(CLK)
);
Register_unq4 Register_inst1 (
    .I(magma_Bits_2_eq_inst8_out),
    .O(Register_inst1_O),
    .CLK(CLK)
);
corebit_const #(
    .value(1'b0)
) bit_const_0_None (
    .out(bit_const_0_None_out)
);
corebit_const #(
    .value(1'b1)
) bit_const_1_None (
    .out(bit_const_1_None_out)
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
    .value(4'h1),
    .width(4)
) const_1_4 (
    .out(const_1_4_out)
);
corebit_and magma_Bit_and_inst0 (
    .in0(bit_const_1_None_out),
    .in1(magma_Bits_4_or_inst0_out[0]),
    .out(magma_Bit_and_inst0_out)
);
corebit_and magma_Bit_and_inst1 (
    .in0(magma_Bit_or_inst0_out),
    .in1(magma_Bits_4_or_inst0_out[0]),
    .out(magma_Bit_and_inst1_out)
);
corebit_and magma_Bit_and_inst10 (
    .in0(magma_Bit_and_inst9_out),
    .in1(REn),
    .out(magma_Bit_and_inst10_out)
);
corebit_and magma_Bit_and_inst11 (
    .in0(bit_const_1_None_out),
    .in1(magma_Bits_4_or_inst0_out[0]),
    .out(magma_Bit_and_inst11_out)
);
corebit_and magma_Bit_and_inst12 (
    .in0(magma_Bit_or_inst8_out),
    .in1(magma_Bits_4_or_inst0_out[0]),
    .out(magma_Bit_and_inst12_out)
);
corebit_and magma_Bit_and_inst13 (
    .in0(magma_Bit_not_inst1_out),
    .in1(magma_Bits_2_eq_inst1_out),
    .out(magma_Bit_and_inst13_out)
);
corebit_and magma_Bit_and_inst14 (
    .in0(magma_Bit_and_inst13_out),
    .in1(Register_inst1_O),
    .out(magma_Bit_and_inst14_out)
);
corebit_and magma_Bit_and_inst15 (
    .in0(magma_Bit_and_inst14_out),
    .in1(WEn),
    .out(magma_Bit_and_inst15_out)
);
corebit_and magma_Bit_and_inst16 (
    .in0(magma_Bit_and_inst15_out),
    .in1(magma_Bit_not_inst2_out),
    .out(magma_Bit_and_inst16_out)
);
corebit_and magma_Bit_and_inst17 (
    .in0(bit_const_1_None_out),
    .in1(magma_Bits_4_or_inst0_out[1]),
    .out(magma_Bit_and_inst17_out)
);
corebit_and magma_Bit_and_inst18 (
    .in0(magma_Bit_or_inst10_out),
    .in1(magma_Bits_4_or_inst0_out[1]),
    .out(magma_Bit_and_inst18_out)
);
corebit_and magma_Bit_and_inst19 (
    .in0(magma_Bit_not_inst3_out),
    .in1(magma_Bits_2_eq_inst2_out),
    .out(magma_Bit_and_inst19_out)
);
corebit_and magma_Bit_and_inst2 (
    .in0(bit_const_1_None_out),
    .in1(magma_Bits_4_or_inst0_out[1]),
    .out(magma_Bit_and_inst2_out)
);
corebit_and magma_Bit_and_inst20 (
    .in0(magma_Bit_and_inst19_out),
    .in1(Register_inst1_O),
    .out(magma_Bit_and_inst20_out)
);
corebit_and magma_Bit_and_inst21 (
    .in0(magma_Bit_and_inst20_out),
    .in1(WEn),
    .out(magma_Bit_and_inst21_out)
);
corebit_and magma_Bit_and_inst22 (
    .in0(magma_Bit_and_inst21_out),
    .in1(magma_Bit_not_inst4_out),
    .out(magma_Bit_and_inst22_out)
);
corebit_and magma_Bit_and_inst23 (
    .in0(bit_const_1_None_out),
    .in1(magma_Bits_4_or_inst0_out[2]),
    .out(magma_Bit_and_inst23_out)
);
corebit_and magma_Bit_and_inst24 (
    .in0(magma_Bit_or_inst12_out),
    .in1(magma_Bits_4_or_inst0_out[2]),
    .out(magma_Bit_and_inst24_out)
);
corebit_and magma_Bit_and_inst25 (
    .in0(magma_Bit_not_inst5_out),
    .in1(magma_Bits_2_eq_inst3_out),
    .out(magma_Bit_and_inst25_out)
);
corebit_and magma_Bit_and_inst26 (
    .in0(magma_Bit_and_inst25_out),
    .in1(Register_inst1_O),
    .out(magma_Bit_and_inst26_out)
);
corebit_and magma_Bit_and_inst27 (
    .in0(magma_Bit_and_inst26_out),
    .in1(WEn),
    .out(magma_Bit_and_inst27_out)
);
corebit_and magma_Bit_and_inst28 (
    .in0(magma_Bit_and_inst27_out),
    .in1(magma_Bit_not_inst6_out),
    .out(magma_Bit_and_inst28_out)
);
corebit_and magma_Bit_and_inst29 (
    .in0(bit_const_1_None_out),
    .in1(magma_Bits_4_or_inst0_out[3]),
    .out(magma_Bit_and_inst29_out)
);
corebit_and magma_Bit_and_inst3 (
    .in0(magma_Bit_or_inst2_out),
    .in1(magma_Bits_4_or_inst0_out[1]),
    .out(magma_Bit_and_inst3_out)
);
corebit_and magma_Bit_and_inst30 (
    .in0(magma_Bit_or_inst14_out),
    .in1(magma_Bits_4_or_inst0_out[3]),
    .out(magma_Bit_and_inst30_out)
);
corebit_and magma_Bit_and_inst31 (
    .in0(magma_Bit_not_inst7_out),
    .in1(magma_Bits_2_eq_inst4_out),
    .out(magma_Bit_and_inst31_out)
);
corebit_and magma_Bit_and_inst32 (
    .in0(magma_Bit_and_inst31_out),
    .in1(Register_inst1_O),
    .out(magma_Bit_and_inst32_out)
);
corebit_and magma_Bit_and_inst33 (
    .in0(magma_Bit_and_inst32_out),
    .in1(WEn),
    .out(magma_Bit_and_inst33_out)
);
corebit_and magma_Bit_and_inst34 (
    .in0(magma_Bit_and_inst33_out),
    .in1(magma_Bit_not_inst8_out),
    .out(magma_Bit_and_inst34_out)
);
corebit_and magma_Bit_and_inst35 (
    .in0(magma_Bit_not_inst9_out),
    .in1(magma_Bits_2_eq_inst5_out),
    .out(magma_Bit_and_inst35_out)
);
corebit_and magma_Bit_and_inst36 (
    .in0(magma_Bit_and_inst35_out),
    .in1(Register_inst1_O),
    .out(magma_Bit_and_inst36_out)
);
corebit_and magma_Bit_and_inst37 (
    .in0(magma_Bit_and_inst36_out),
    .in1(WEn),
    .out(magma_Bit_and_inst37_out)
);
corebit_and magma_Bit_and_inst38 (
    .in0(magma_Bit_and_inst37_out),
    .in1(magma_Bit_or_inst14_out),
    .out(magma_Bit_and_inst38_out)
);
corebit_and magma_Bit_and_inst39 (
    .in0(magma_Bit_not_inst10_out),
    .in1(magma_Bits_2_eq_inst6_out),
    .out(magma_Bit_and_inst39_out)
);
corebit_and magma_Bit_and_inst4 (
    .in0(bit_const_1_None_out),
    .in1(magma_Bits_4_or_inst0_out[2]),
    .out(magma_Bit_and_inst4_out)
);
corebit_and magma_Bit_and_inst40 (
    .in0(magma_Bit_and_inst39_out),
    .in1(Register_inst1_O),
    .out(magma_Bit_and_inst40_out)
);
corebit_and magma_Bit_and_inst41 (
    .in0(magma_Bit_and_inst40_out),
    .in1(WEn),
    .out(magma_Bit_and_inst41_out)
);
corebit_and magma_Bit_and_inst42 (
    .in0(magma_Bit_and_inst41_out),
    .in1(magma_Bit_or_inst15_out),
    .out(magma_Bit_and_inst42_out)
);
corebit_and magma_Bit_and_inst5 (
    .in0(magma_Bit_or_inst4_out),
    .in1(magma_Bits_4_or_inst0_out[2]),
    .out(magma_Bit_and_inst5_out)
);
corebit_and magma_Bit_and_inst6 (
    .in0(bit_const_1_None_out),
    .in1(magma_Bits_4_or_inst0_out[3]),
    .out(magma_Bit_and_inst6_out)
);
corebit_and magma_Bit_and_inst7 (
    .in0(magma_Bit_or_inst6_out),
    .in1(magma_Bits_4_or_inst0_out[3]),
    .out(magma_Bit_and_inst7_out)
);
corebit_and magma_Bit_and_inst8 (
    .in0(magma_Bit_not_inst0_out),
    .in1(magma_Bits_2_eq_inst0_out),
    .out(magma_Bit_and_inst8_out)
);
corebit_and magma_Bit_and_inst9 (
    .in0(magma_Bit_and_inst8_out),
    .in1(Register_inst1_O),
    .out(magma_Bit_and_inst9_out)
);
corebit_not magma_Bit_not_inst0 (
    .in(CEn),
    .out(magma_Bit_not_inst0_out)
);
corebit_not magma_Bit_not_inst1 (
    .in(CEn),
    .out(magma_Bit_not_inst1_out)
);
corebit_not magma_Bit_not_inst10 (
    .in(CEn),
    .out(magma_Bit_not_inst10_out)
);
corebit_not magma_Bit_not_inst2 (
    .in(magma_Bits_4_or_inst0_out[0]),
    .out(magma_Bit_not_inst2_out)
);
corebit_not magma_Bit_not_inst3 (
    .in(CEn),
    .out(magma_Bit_not_inst3_out)
);
corebit_not magma_Bit_not_inst4 (
    .in(magma_Bits_4_or_inst0_out[1]),
    .out(magma_Bit_not_inst4_out)
);
corebit_not magma_Bit_not_inst5 (
    .in(CEn),
    .out(magma_Bit_not_inst5_out)
);
corebit_not magma_Bit_not_inst6 (
    .in(magma_Bits_4_or_inst0_out[2]),
    .out(magma_Bit_not_inst6_out)
);
corebit_not magma_Bit_not_inst7 (
    .in(CEn),
    .out(magma_Bit_not_inst7_out)
);
corebit_not magma_Bit_not_inst8 (
    .in(magma_Bits_4_or_inst0_out[3]),
    .out(magma_Bit_not_inst8_out)
);
corebit_not magma_Bit_not_inst9 (
    .in(CEn),
    .out(magma_Bit_not_inst9_out)
);
corebit_or magma_Bit_or_inst0 (
    .in0(bit_const_0_None_out),
    .in1(magma_Bit_and_inst0_out),
    .out(magma_Bit_or_inst0_out)
);
corebit_or magma_Bit_or_inst1 (
    .in0(bit_const_0_None_out),
    .in1(magma_Bit_and_inst1_out),
    .out(magma_Bit_or_inst1_out)
);
corebit_or magma_Bit_or_inst10 (
    .in0(magma_Bit_or_inst8_out),
    .in1(magma_Bit_and_inst17_out),
    .out(magma_Bit_or_inst10_out)
);
corebit_or magma_Bit_or_inst11 (
    .in0(magma_Bit_or_inst9_out),
    .in1(magma_Bit_and_inst18_out),
    .out(magma_Bit_or_inst11_out)
);
corebit_or magma_Bit_or_inst12 (
    .in0(magma_Bit_or_inst10_out),
    .in1(magma_Bit_and_inst23_out),
    .out(magma_Bit_or_inst12_out)
);
corebit_or magma_Bit_or_inst13 (
    .in0(magma_Bit_or_inst11_out),
    .in1(magma_Bit_and_inst24_out),
    .out(magma_Bit_or_inst13_out)
);
corebit_or magma_Bit_or_inst14 (
    .in0(magma_Bit_or_inst12_out),
    .in1(magma_Bit_and_inst29_out),
    .out(magma_Bit_or_inst14_out)
);
corebit_or magma_Bit_or_inst15 (
    .in0(magma_Bit_or_inst13_out),
    .in1(magma_Bit_and_inst30_out),
    .out(magma_Bit_or_inst15_out)
);
corebit_or magma_Bit_or_inst2 (
    .in0(magma_Bit_or_inst0_out),
    .in1(magma_Bit_and_inst2_out),
    .out(magma_Bit_or_inst2_out)
);
corebit_or magma_Bit_or_inst3 (
    .in0(magma_Bit_or_inst1_out),
    .in1(magma_Bit_and_inst3_out),
    .out(magma_Bit_or_inst3_out)
);
corebit_or magma_Bit_or_inst4 (
    .in0(magma_Bit_or_inst2_out),
    .in1(magma_Bit_and_inst4_out),
    .out(magma_Bit_or_inst4_out)
);
corebit_or magma_Bit_or_inst5 (
    .in0(magma_Bit_or_inst3_out),
    .in1(magma_Bit_and_inst5_out),
    .out(magma_Bit_or_inst5_out)
);
corebit_or magma_Bit_or_inst6 (
    .in0(magma_Bit_or_inst4_out),
    .in1(magma_Bit_and_inst6_out),
    .out(magma_Bit_or_inst6_out)
);
corebit_or magma_Bit_or_inst7 (
    .in0(magma_Bit_or_inst5_out),
    .in1(magma_Bit_and_inst7_out),
    .out(magma_Bit_or_inst7_out)
);
corebit_or magma_Bit_or_inst8 (
    .in0(bit_const_0_None_out),
    .in1(magma_Bit_and_inst11_out),
    .out(magma_Bit_or_inst8_out)
);
corebit_or magma_Bit_or_inst9 (
    .in0(bit_const_0_None_out),
    .in1(magma_Bit_and_inst12_out),
    .out(magma_Bit_or_inst9_out)
);
wire [1:0] magma_Bits_2_eq_inst0_in0;
assign magma_Bits_2_eq_inst0_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst0 (
    .in0(magma_Bits_2_eq_inst0_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst0_out)
);
wire [1:0] magma_Bits_2_eq_inst1_in0;
assign magma_Bits_2_eq_inst1_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst1 (
    .in0(magma_Bits_2_eq_inst1_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst1_out)
);
wire [1:0] magma_Bits_2_eq_inst2_in0;
assign magma_Bits_2_eq_inst2_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst2 (
    .in0(magma_Bits_2_eq_inst2_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst2_out)
);
wire [1:0] magma_Bits_2_eq_inst3_in0;
assign magma_Bits_2_eq_inst3_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst3 (
    .in0(magma_Bits_2_eq_inst3_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst3_out)
);
wire [1:0] magma_Bits_2_eq_inst4_in0;
assign magma_Bits_2_eq_inst4_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst4 (
    .in0(magma_Bits_2_eq_inst4_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst4_out)
);
wire [1:0] magma_Bits_2_eq_inst5_in0;
assign magma_Bits_2_eq_inst5_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst5 (
    .in0(magma_Bits_2_eq_inst5_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst5_out)
);
wire [1:0] magma_Bits_2_eq_inst6_in0;
assign magma_Bits_2_eq_inst6_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst6 (
    .in0(magma_Bits_2_eq_inst6_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst6_out)
);
wire [1:0] magma_Bits_2_eq_inst7_in0;
assign magma_Bits_2_eq_inst7_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst7 (
    .in0(magma_Bits_2_eq_inst7_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst7_out)
);
wire [1:0] magma_Bits_2_eq_inst8_in0;
assign magma_Bits_2_eq_inst8_in0 = {power_gate,deep_sleep};
coreir_eq #(
    .width(2)
) magma_Bits_2_eq_inst8 (
    .in0(magma_Bits_2_eq_inst8_in0),
    .in1(const_0_2_out),
    .out(magma_Bits_2_eq_inst8_out)
);
coreir_or #(
    .width(4)
) magma_Bits_4_or_inst0 (
    .in0(Mux2xBits4_inst0_O),
    .in1(Mux2xBits4_inst1_O),
    .out(magma_Bits_4_or_inst0_out)
);
wire [3:0] magma_Bits_4_shl_inst0_in1;
assign magma_Bits_4_shl_inst0_in1 = {bit_const_0_None_out,bit_const_0_None_out,RCF0A};
coreir_shl #(
    .width(4)
) magma_Bits_4_shl_inst0 (
    .in0(const_1_4_out),
    .in1(magma_Bits_4_shl_inst0_in1),
    .out(magma_Bits_4_shl_inst0_out)
);
wire [3:0] magma_Bits_4_shl_inst1_in1;
assign magma_Bits_4_shl_inst1_in1 = {bit_const_0_None_out,bit_const_0_None_out,RCF1A};
coreir_shl #(
    .width(4)
) magma_Bits_4_shl_inst1 (
    .in0(const_1_4_out),
    .in1(magma_Bits_4_shl_inst1_in1),
    .out(magma_Bits_4_shl_inst1_out)
);
assign RDATA = Register_inst0_O;
assign wake_ack = magma_Bits_2_eq_inst7_out;
assign current_state = {power_gate,deep_sleep};
endmodule

module StateMachine (
    input [15:0] receive/*verilator public*/,
    input [0:0] receive_valid/*verilator public*/,
    output [0:0] receive_ready/*verilator public*/,
    input [2:0] offer/*verilator public*/,
    input [0:0] offer_valid/*verilator public*/,
    output [0:0] offer_ready/*verilator public*/,
    output [15:0] send/*verilator public*/,
    input [0:0] send_ready/*verilator public*/,
    output [0:0] send_valid/*verilator public*/,
    output [2:0] current_state/*verilator public*/,
    input CLK/*verilator public*/
);
wire [2:0] CommandFromClient_O;
wire [0:0] CommandFromClient_ready_O;
wire [0:0] CommandFromClient_valid_O;
wire [15:0] DataFromClient_O;
wire [0:0] DataFromClient_ready_O;
wire [0:0] DataFromClient_valid_O;
wire [15:0] DataToClient_O;
wire [0:0] DataToClient_ready_O;
wire [0:0] DataToClient_valid_O;
wire Mux2xBit_inst0_O;
wire Mux2xBit_inst1_O;
wire Mux2xBit_inst10_O;
wire Mux2xBit_inst11_O;
wire Mux2xBit_inst12_O;
wire Mux2xBit_inst13_O;
wire Mux2xBit_inst14_O;
wire Mux2xBit_inst15_O;
wire Mux2xBit_inst16_O;
wire Mux2xBit_inst17_O;
wire Mux2xBit_inst18_O;
wire Mux2xBit_inst19_O;
wire Mux2xBit_inst2_O;
wire Mux2xBit_inst3_O;
wire Mux2xBit_inst4_O;
wire Mux2xBit_inst5_O;
wire Mux2xBit_inst6_O;
wire Mux2xBit_inst7_O;
wire Mux2xBit_inst8_O;
wire Mux2xBit_inst9_O;
wire [10:0] Mux2xBits11_inst0_O;
wire [10:0] Mux2xBits11_inst1_O;
wire [10:0] Mux2xBits11_inst2_O;
wire [10:0] Mux2xBits11_inst3_O;
wire [10:0] Mux2xBits11_inst4_O;
wire [10:0] Mux2xBits11_inst5_O;
wire [10:0] Mux2xBits11_inst6_O;
wire [10:0] Mux2xBits11_inst7_O;
wire [15:0] Mux2xBits16_inst0_O;
wire [15:0] Mux2xBits16_inst1_O;
wire [15:0] Mux2xBits16_inst10_O;
wire [15:0] Mux2xBits16_inst11_O;
wire [15:0] Mux2xBits16_inst12_O;
wire [15:0] Mux2xBits16_inst13_O;
wire [15:0] Mux2xBits16_inst2_O;
wire [15:0] Mux2xBits16_inst3_O;
wire [15:0] Mux2xBits16_inst4_O;
wire [15:0] Mux2xBits16_inst5_O;
wire [15:0] Mux2xBits16_inst6_O;
wire [15:0] Mux2xBits16_inst7_O;
wire [15:0] Mux2xBits16_inst8_O;
wire [15:0] Mux2xBits16_inst9_O;
wire [0:0] Mux2xBits1_inst0_O;
wire [0:0] Mux2xBits1_inst1_O;
wire [0:0] Mux2xBits1_inst10_O;
wire [0:0] Mux2xBits1_inst11_O;
wire [0:0] Mux2xBits1_inst12_O;
wire [0:0] Mux2xBits1_inst13_O;
wire [0:0] Mux2xBits1_inst14_O;
wire [0:0] Mux2xBits1_inst15_O;
wire [0:0] Mux2xBits1_inst16_O;
wire [0:0] Mux2xBits1_inst17_O;
wire [0:0] Mux2xBits1_inst18_O;
wire [0:0] Mux2xBits1_inst19_O;
wire [0:0] Mux2xBits1_inst2_O;
wire [0:0] Mux2xBits1_inst20_O;
wire [0:0] Mux2xBits1_inst3_O;
wire [0:0] Mux2xBits1_inst4_O;
wire [0:0] Mux2xBits1_inst5_O;
wire [0:0] Mux2xBits1_inst6_O;
wire [0:0] Mux2xBits1_inst7_O;
wire [0:0] Mux2xBits1_inst8_O;
wire [0:0] Mux2xBits1_inst9_O;
wire [2:0] Mux2xBits3_inst0_O;
wire [2:0] Mux2xBits3_inst1_O;
wire [2:0] Mux2xBits3_inst10_O;
wire [2:0] Mux2xBits3_inst11_O;
wire [2:0] Mux2xBits3_inst12_O;
wire [2:0] Mux2xBits3_inst13_O;
wire [2:0] Mux2xBits3_inst14_O;
wire [2:0] Mux2xBits3_inst15_O;
wire [2:0] Mux2xBits3_inst16_O;
wire [2:0] Mux2xBits3_inst17_O;
wire [2:0] Mux2xBits3_inst18_O;
wire [2:0] Mux2xBits3_inst19_O;
wire [2:0] Mux2xBits3_inst2_O;
wire [2:0] Mux2xBits3_inst20_O;
wire [2:0] Mux2xBits3_inst21_O;
wire [2:0] Mux2xBits3_inst22_O;
wire [2:0] Mux2xBits3_inst23_O;
wire [2:0] Mux2xBits3_inst24_O;
wire [2:0] Mux2xBits3_inst25_O;
wire [2:0] Mux2xBits3_inst26_O;
wire [2:0] Mux2xBits3_inst27_O;
wire [2:0] Mux2xBits3_inst28_O;
wire [2:0] Mux2xBits3_inst29_O;
wire [2:0] Mux2xBits3_inst3_O;
wire [2:0] Mux2xBits3_inst30_O;
wire [2:0] Mux2xBits3_inst31_O;
wire [2:0] Mux2xBits3_inst32_O;
wire [2:0] Mux2xBits3_inst33_O;
wire [2:0] Mux2xBits3_inst34_O;
wire [2:0] Mux2xBits3_inst35_O;
wire [2:0] Mux2xBits3_inst36_O;
wire [2:0] Mux2xBits3_inst37_O;
wire [2:0] Mux2xBits3_inst38_O;
wire [2:0] Mux2xBits3_inst39_O;
wire [2:0] Mux2xBits3_inst4_O;
wire [2:0] Mux2xBits3_inst40_O;
wire [2:0] Mux2xBits3_inst41_O;
wire [2:0] Mux2xBits3_inst42_O;
wire [2:0] Mux2xBits3_inst43_O;
wire [2:0] Mux2xBits3_inst44_O;
wire [2:0] Mux2xBits3_inst45_O;
wire [2:0] Mux2xBits3_inst46_O;
wire [2:0] Mux2xBits3_inst47_O;
wire [2:0] Mux2xBits3_inst48_O;
wire [2:0] Mux2xBits3_inst49_O;
wire [2:0] Mux2xBits3_inst5_O;
wire [2:0] Mux2xBits3_inst50_O;
wire [2:0] Mux2xBits3_inst51_O;
wire [2:0] Mux2xBits3_inst52_O;
wire [2:0] Mux2xBits3_inst53_O;
wire [2:0] Mux2xBits3_inst54_O;
wire [2:0] Mux2xBits3_inst55_O;
wire [2:0] Mux2xBits3_inst56_O;
wire [2:0] Mux2xBits3_inst57_O;
wire [2:0] Mux2xBits3_inst58_O;
wire [2:0] Mux2xBits3_inst59_O;
wire [2:0] Mux2xBits3_inst6_O;
wire [2:0] Mux2xBits3_inst60_O;
wire [2:0] Mux2xBits3_inst61_O;
wire [2:0] Mux2xBits3_inst62_O;
wire [2:0] Mux2xBits3_inst63_O;
wire [2:0] Mux2xBits3_inst64_O;
wire [2:0] Mux2xBits3_inst65_O;
wire [2:0] Mux2xBits3_inst66_O;
wire [2:0] Mux2xBits3_inst67_O;
wire [2:0] Mux2xBits3_inst68_O;
wire [2:0] Mux2xBits3_inst69_O;
wire [2:0] Mux2xBits3_inst7_O;
wire [2:0] Mux2xBits3_inst70_O;
wire [2:0] Mux2xBits3_inst71_O;
wire [2:0] Mux2xBits3_inst72_O;
wire [2:0] Mux2xBits3_inst73_O;
wire [2:0] Mux2xBits3_inst74_O;
wire [2:0] Mux2xBits3_inst75_O;
wire [2:0] Mux2xBits3_inst76_O;
wire [2:0] Mux2xBits3_inst77_O;
wire [2:0] Mux2xBits3_inst78_O;
wire [2:0] Mux2xBits3_inst79_O;
wire [2:0] Mux2xBits3_inst8_O;
wire [2:0] Mux2xBits3_inst80_O;
wire [2:0] Mux2xBits3_inst81_O;
wire [2:0] Mux2xBits3_inst82_O;
wire [2:0] Mux2xBits3_inst83_O;
wire [2:0] Mux2xBits3_inst84_O;
wire [2:0] Mux2xBits3_inst85_O;
wire [2:0] Mux2xBits3_inst86_O;
wire [2:0] Mux2xBits3_inst87_O;
wire [2:0] Mux2xBits3_inst88_O;
wire [2:0] Mux2xBits3_inst89_O;
wire [2:0] Mux2xBits3_inst9_O;
wire [2:0] Mux2xBits3_inst90_O;
wire [2:0] Mux2xBits3_inst91_O;
wire [2:0] Mux2xBits3_inst92_O;
wire [2:0] Mux2xBits3_inst93_O;
wire Mux2xEnable_inst0_O;
wire Mux2xEnable_inst1_O;
wire Mux2xEnable_inst2_O;
wire Mux2xEnable_inst3_O;
wire [15:0] SRAMSMR_inst0_RDATA;
wire SRAMSMR_inst0_wake_ack;
wire [1:0] SRAMSMR_inst0_current_state;
wire bit_const_0_None_out;
wire bit_const_1_None_out;
wire [0:0] const_0_1_out;
wire [1:0] const_0_2_out;
wire [2:0] const_0_3_out;
wire [15:0] const_13_16_out;
wire [15:0] const_15_16_out;
wire [0:0] const_1_1_out;
wire [1:0] const_1_2_out;
wire [2:0] const_1_3_out;
wire [2:0] const_2_3_out;
wire [2:0] const_3_3_out;
wire [2:0] const_4_3_out;
wire [2:0] const_5_3_out;
wire [10:0] const_6_11_out;
wire [2:0] const_6_3_out;
wire [2:0] const_7_3_out;
wire [0:0] initreg_O;
wire magma_Bit_and_inst0_out;
wire magma_Bit_not_inst0_out;
wire magma_Bits_1_eq_inst0_out;
wire magma_Bits_1_eq_inst1_out;
wire magma_Bits_1_eq_inst2_out;
wire magma_Bits_1_eq_inst3_out;
wire magma_Bits_1_eq_inst4_out;
wire magma_Bits_1_eq_inst5_out;
wire magma_Bits_1_eq_inst6_out;
wire [0:0] magma_Bits_1_not_inst0_out;
wire [0:0] magma_Bits_1_not_inst1_out;
wire [0:0] magma_Bits_1_not_inst2_out;
wire [0:0] magma_Bits_1_not_inst3_out;
wire [0:0] magma_Bits_1_not_inst4_out;
wire [0:0] magma_Bits_1_not_inst5_out;
wire [0:0] magma_Bits_1_not_inst6_out;
wire [0:0] magma_Bits_1_not_inst7_out;
wire [0:0] magma_Bits_1_not_inst8_out;
wire magma_Bits_3_eq_inst0_out;
wire magma_Bits_3_eq_inst1_out;
wire magma_Bits_3_eq_inst10_out;
wire magma_Bits_3_eq_inst11_out;
wire magma_Bits_3_eq_inst12_out;
wire magma_Bits_3_eq_inst13_out;
wire magma_Bits_3_eq_inst14_out;
wire magma_Bits_3_eq_inst15_out;
wire magma_Bits_3_eq_inst16_out;
wire magma_Bits_3_eq_inst17_out;
wire magma_Bits_3_eq_inst18_out;
wire magma_Bits_3_eq_inst19_out;
wire magma_Bits_3_eq_inst2_out;
wire magma_Bits_3_eq_inst20_out;
wire magma_Bits_3_eq_inst21_out;
wire magma_Bits_3_eq_inst22_out;
wire magma_Bits_3_eq_inst23_out;
wire magma_Bits_3_eq_inst24_out;
wire magma_Bits_3_eq_inst25_out;
wire magma_Bits_3_eq_inst26_out;
wire magma_Bits_3_eq_inst27_out;
wire magma_Bits_3_eq_inst28_out;
wire magma_Bits_3_eq_inst29_out;
wire magma_Bits_3_eq_inst3_out;
wire magma_Bits_3_eq_inst30_out;
wire magma_Bits_3_eq_inst31_out;
wire magma_Bits_3_eq_inst32_out;
wire magma_Bits_3_eq_inst33_out;
wire magma_Bits_3_eq_inst34_out;
wire magma_Bits_3_eq_inst35_out;
wire magma_Bits_3_eq_inst36_out;
wire magma_Bits_3_eq_inst37_out;
wire magma_Bits_3_eq_inst38_out;
wire magma_Bits_3_eq_inst39_out;
wire magma_Bits_3_eq_inst4_out;
wire magma_Bits_3_eq_inst40_out;
wire magma_Bits_3_eq_inst41_out;
wire magma_Bits_3_eq_inst42_out;
wire magma_Bits_3_eq_inst43_out;
wire magma_Bits_3_eq_inst44_out;
wire magma_Bits_3_eq_inst45_out;
wire magma_Bits_3_eq_inst46_out;
wire magma_Bits_3_eq_inst47_out;
wire magma_Bits_3_eq_inst48_out;
wire magma_Bits_3_eq_inst49_out;
wire magma_Bits_3_eq_inst5_out;
wire magma_Bits_3_eq_inst50_out;
wire magma_Bits_3_eq_inst51_out;
wire magma_Bits_3_eq_inst52_out;
wire magma_Bits_3_eq_inst53_out;
wire magma_Bits_3_eq_inst54_out;
wire magma_Bits_3_eq_inst55_out;
wire magma_Bits_3_eq_inst56_out;
wire magma_Bits_3_eq_inst57_out;
wire magma_Bits_3_eq_inst58_out;
wire magma_Bits_3_eq_inst59_out;
wire magma_Bits_3_eq_inst6_out;
wire magma_Bits_3_eq_inst60_out;
wire magma_Bits_3_eq_inst61_out;
wire magma_Bits_3_eq_inst62_out;
wire magma_Bits_3_eq_inst63_out;
wire magma_Bits_3_eq_inst64_out;
wire magma_Bits_3_eq_inst65_out;
wire magma_Bits_3_eq_inst66_out;
wire magma_Bits_3_eq_inst67_out;
wire magma_Bits_3_eq_inst68_out;
wire magma_Bits_3_eq_inst69_out;
wire magma_Bits_3_eq_inst7_out;
wire magma_Bits_3_eq_inst70_out;
wire magma_Bits_3_eq_inst71_out;
wire magma_Bits_3_eq_inst72_out;
wire magma_Bits_3_eq_inst73_out;
wire magma_Bits_3_eq_inst74_out;
wire magma_Bits_3_eq_inst75_out;
wire magma_Bits_3_eq_inst76_out;
wire magma_Bits_3_eq_inst77_out;
wire magma_Bits_3_eq_inst78_out;
wire magma_Bits_3_eq_inst79_out;
wire magma_Bits_3_eq_inst8_out;
wire magma_Bits_3_eq_inst80_out;
wire magma_Bits_3_eq_inst81_out;
wire magma_Bits_3_eq_inst82_out;
wire magma_Bits_3_eq_inst83_out;
wire magma_Bits_3_eq_inst84_out;
wire magma_Bits_3_eq_inst85_out;
wire magma_Bits_3_eq_inst86_out;
wire magma_Bits_3_eq_inst87_out;
wire magma_Bits_3_eq_inst9_out;
wire [15:0] mem_addr_reg_O;
wire [15:0] mem_data_reg_O;
wire [1:0] redundancy_reg_O;
wire [2:0] state_reg_O;
Register_unq5 CommandFromClient (
    .I(offer),
    .O(CommandFromClient_O),
    .CE(Mux2xBit_inst17_O),
    .CLK(CLK)
);
Register_unq6 CommandFromClient_ready (
    .I(Mux2xBits1_inst19_O),
    .O(CommandFromClient_ready_O),
    .CLK(CLK)
);
Register_unq6 CommandFromClient_valid (
    .I(offer_valid),
    .O(CommandFromClient_valid_O),
    .CLK(CLK)
);
Register_unq3 DataFromClient (
    .I(receive),
    .O(DataFromClient_O),
    .CE(Mux2xBit_inst10_O),
    .CLK(CLK)
);
Register_unq6 DataFromClient_ready (
    .I(Mux2xBits1_inst20_O),
    .O(DataFromClient_ready_O),
    .CLK(CLK)
);
Register_unq6 DataFromClient_valid (
    .I(receive_valid),
    .O(DataFromClient_valid_O),
    .CLK(CLK)
);
Register_unq3 DataToClient (
    .I(Mux2xBits16_inst13_O),
    .O(DataToClient_O),
    .CE(Mux2xBit_inst18_O),
    .CLK(CLK)
);
Register_unq6 DataToClient_ready (
    .I(send_ready),
    .O(DataToClient_ready_O),
    .CLK(CLK)
);
Register_unq6 DataToClient_valid (
    .I(Mux2xBits1_inst18_O),
    .O(DataToClient_valid_O),
    .CLK(CLK)
);
Mux2xBit Mux2xBit_inst0 (
    .I0(bit_const_1_None_out),
    .I1(bit_const_1_None_out),
    .S(magma_Bit_and_inst0_out),
    .O(Mux2xBit_inst0_O)
);
Mux2xBit Mux2xBit_inst1 (
    .I0(bit_const_1_None_out),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_1_eq_inst6_out),
    .O(Mux2xBit_inst1_O)
);
Mux2xBit Mux2xBit_inst10 (
    .I0(Mux2xBit_inst5_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBit_inst10_O)
);
Mux2xBit Mux2xBit_inst11 (
    .I0(Mux2xBit_inst8_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBit_inst11_O)
);
Mux2xBit Mux2xBit_inst12 (
    .I0(bit_const_1_None_out),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBit_inst12_O)
);
Mux2xBit Mux2xBit_inst13 (
    .I0(Mux2xBit_inst9_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBit_inst13_O)
);
Mux2xBit Mux2xBit_inst14 (
    .I0(Mux2xBit_inst11_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBit_inst14_O)
);
Mux2xBit Mux2xBit_inst15 (
    .I0(Mux2xBit_inst12_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBit_inst15_O)
);
Mux2xBit Mux2xBit_inst16 (
    .I0(Mux2xBit_inst13_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBit_inst16_O)
);
Mux2xBit Mux2xBit_inst17 (
    .I0(bit_const_1_None_out),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBit_inst17_O)
);
Mux2xBit Mux2xBit_inst18 (
    .I0(Mux2xBit_inst14_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBit_inst18_O)
);
Mux2xBit Mux2xBit_inst19 (
    .I0(Mux2xBit_inst15_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBit_inst19_O)
);
Mux2xBit Mux2xBit_inst2 (
    .I0(bit_const_1_None_out),
    .I1(Mux2xBit_inst1_O),
    .S(magma_Bits_3_eq_inst77_out),
    .O(Mux2xBit_inst2_O)
);
Mux2xBit Mux2xBit_inst3 (
    .I0(Mux2xBit_inst2_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst66_out),
    .O(Mux2xBit_inst3_O)
);
Mux2xBit Mux2xBit_inst4 (
    .I0(bit_const_1_None_out),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBit_inst4_O)
);
Mux2xBit Mux2xBit_inst5 (
    .I0(bit_const_1_None_out),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBit_inst5_O)
);
Mux2xBit Mux2xBit_inst6 (
    .I0(Mux2xBit_inst3_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBit_inst6_O)
);
Mux2xBit Mux2xBit_inst7 (
    .I0(Mux2xBit_inst4_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst44_out),
    .O(Mux2xBit_inst7_O)
);
Mux2xBit Mux2xBit_inst8 (
    .I0(Mux2xBit_inst6_O),
    .I1(Mux2xBit_inst0_O),
    .S(magma_Bits_3_eq_inst44_out),
    .O(Mux2xBit_inst8_O)
);
Mux2xBit Mux2xBit_inst9 (
    .I0(Mux2xBit_inst7_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBit_inst9_O)
);
Mux2xBits11 Mux2xBits11_inst0 (
    .I0(const_6_11_out),
    .I1(Mux2xBits16_inst0_O[10:0]),
    .S(magma_Bits_1_eq_inst5_out),
    .O(Mux2xBits11_inst0_O)
);
Mux2xBits11 Mux2xBits11_inst1 (
    .I0(const_6_11_out),
    .I1(Mux2xBits16_inst0_O[10:0]),
    .S(magma_Bits_3_eq_inst77_out),
    .O(Mux2xBits11_inst1_O)
);
Mux2xBits11 Mux2xBits11_inst2 (
    .I0(Mux2xBits11_inst1_O),
    .I1(Mux2xBits11_inst0_O),
    .S(magma_Bits_3_eq_inst66_out),
    .O(Mux2xBits11_inst2_O)
);
Mux2xBits11 Mux2xBits11_inst3 (
    .I0(Mux2xBits11_inst2_O),
    .I1(const_6_11_out),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBits11_inst3_O)
);
Mux2xBits11 Mux2xBits11_inst4 (
    .I0(Mux2xBits11_inst3_O),
    .I1(const_6_11_out),
    .S(magma_Bits_3_eq_inst44_out),
    .O(Mux2xBits11_inst4_O)
);
Mux2xBits11 Mux2xBits11_inst5 (
    .I0(Mux2xBits11_inst4_O),
    .I1(const_6_11_out),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBits11_inst5_O)
);
Mux2xBits11 Mux2xBits11_inst6 (
    .I0(Mux2xBits11_inst5_O),
    .I1(const_6_11_out),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBits11_inst6_O)
);
Mux2xBits11 Mux2xBits11_inst7 (
    .I0(Mux2xBits11_inst6_O),
    .I1(const_6_11_out),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBits11_inst7_O)
);
Mux2xBits16 Mux2xBits16_inst0 (
    .I0(mem_addr_reg_O),
    .I1(const_13_16_out),
    .S(magma_Bits_1_eq_inst0_out),
    .O(Mux2xBits16_inst0_O)
);
wire [15:0] Mux2xBits16_inst1_I0;
assign Mux2xBits16_inst1_I0 = {Mux2xBits16_inst0_O[15],Mux2xBits16_inst0_O[14],Mux2xBits16_inst0_O[13],Mux2xBits16_inst0_O[12],Mux2xBits16_inst0_O[11],Mux2xBits16_inst0_O[10:0]};
Mux2xBits16 Mux2xBits16_inst1 (
    .I0(Mux2xBits16_inst1_I0),
    .I1(DataFromClient_O),
    .S(magma_Bits_1_eq_inst4_out),
    .O(Mux2xBits16_inst1_O)
);
Mux2xBits16 Mux2xBits16_inst10 (
    .I0(Mux2xBits16_inst8_O),
    .I1(Mux2xBits16_inst0_O),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBits16_inst10_O)
);
Mux2xBits16 Mux2xBits16_inst11 (
    .I0(Mux2xBits16_inst9_O),
    .I1(const_15_16_out),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBits16_inst11_O)
);
Mux2xBits16 Mux2xBits16_inst12 (
    .I0(Mux2xBits16_inst10_O),
    .I1(Mux2xBits16_inst0_O),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBits16_inst12_O)
);
Mux2xBits16 Mux2xBits16_inst13 (
    .I0(Mux2xBits16_inst11_O),
    .I1(const_15_16_out),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBits16_inst13_O)
);
Mux2xBits16 Mux2xBits16_inst2 (
    .I0(const_15_16_out),
    .I1(SRAMSMR_inst0_RDATA),
    .S(magma_Bits_3_eq_inst77_out),
    .O(Mux2xBits16_inst2_O)
);
Mux2xBits16 Mux2xBits16_inst3 (
    .I0(Mux2xBits16_inst2_O),
    .I1(const_15_16_out),
    .S(magma_Bits_3_eq_inst66_out),
    .O(Mux2xBits16_inst3_O)
);
Mux2xBits16 Mux2xBits16_inst4 (
    .I0(Mux2xBits16_inst0_O),
    .I1(Mux2xBits16_inst1_O),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBits16_inst4_O)
);
Mux2xBits16 Mux2xBits16_inst5 (
    .I0(Mux2xBits16_inst3_O),
    .I1(const_15_16_out),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBits16_inst5_O)
);
Mux2xBits16 Mux2xBits16_inst6 (
    .I0(Mux2xBits16_inst4_O),
    .I1(Mux2xBits16_inst0_O),
    .S(magma_Bits_3_eq_inst44_out),
    .O(Mux2xBits16_inst6_O)
);
wire [15:0] Mux2xBits16_inst7_I1;
assign Mux2xBits16_inst7_I1 = {bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,bit_const_0_None_out,SRAMSMR_inst0_wake_ack};
Mux2xBits16 Mux2xBits16_inst7 (
    .I0(Mux2xBits16_inst5_O),
    .I1(Mux2xBits16_inst7_I1),
    .S(magma_Bits_3_eq_inst44_out),
    .O(Mux2xBits16_inst7_O)
);
Mux2xBits16 Mux2xBits16_inst8 (
    .I0(Mux2xBits16_inst6_O),
    .I1(Mux2xBits16_inst0_O),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBits16_inst8_O)
);
Mux2xBits16 Mux2xBits16_inst9 (
    .I0(Mux2xBits16_inst7_O),
    .I1(const_15_16_out),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBits16_inst9_O)
);
Mux2xBits1 Mux2xBits1_inst0 (
    .I0(const_1_1_out),
    .I1(magma_Bits_1_not_inst3_out),
    .S(magma_Bit_not_inst0_out),
    .O(Mux2xBits1_inst0_O)
);
Mux2xBits1 Mux2xBits1_inst1 (
    .I0(const_1_1_out),
    .I1(Mux2xBits1_inst0_O),
    .S(magma_Bits_1_eq_inst1_out),
    .O(Mux2xBits1_inst1_O)
);
Mux2xBits1 Mux2xBits1_inst10 (
    .I0(Mux2xBits1_inst8_O),
    .I1(magma_Bits_1_not_inst2_out),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBits1_inst10_O)
);
Mux2xBits1 Mux2xBits1_inst11 (
    .I0(Mux2xBits1_inst9_O),
    .I1(Mux2xBits1_inst4_O),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBits1_inst11_O)
);
Mux2xBits1 Mux2xBits1_inst12 (
    .I0(Mux2xBits1_inst10_O),
    .I1(Mux2xBits1_inst3_O),
    .S(magma_Bits_3_eq_inst44_out),
    .O(Mux2xBits1_inst12_O)
);
Mux2xBits1 Mux2xBits1_inst13 (
    .I0(Mux2xBits1_inst11_O),
    .I1(magma_Bits_1_not_inst0_out),
    .S(magma_Bits_3_eq_inst44_out),
    .O(Mux2xBits1_inst13_O)
);
Mux2xBits1 Mux2xBits1_inst14 (
    .I0(Mux2xBits1_inst12_O),
    .I1(magma_Bits_1_not_inst2_out),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBits1_inst14_O)
);
Mux2xBits1 Mux2xBits1_inst15 (
    .I0(Mux2xBits1_inst13_O),
    .I1(Mux2xBits1_inst2_O),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBits1_inst15_O)
);
Mux2xBits1 Mux2xBits1_inst16 (
    .I0(Mux2xBits1_inst14_O),
    .I1(magma_Bits_1_not_inst2_out),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBits1_inst16_O)
);
Mux2xBits1 Mux2xBits1_inst17 (
    .I0(Mux2xBits1_inst15_O),
    .I1(magma_Bits_1_not_inst0_out),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBits1_inst17_O)
);
Mux2xBits1 Mux2xBits1_inst18 (
    .I0(Mux2xBits1_inst16_O),
    .I1(magma_Bits_1_not_inst2_out),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBits1_inst18_O)
);
Mux2xBits1 Mux2xBits1_inst19 (
    .I0(magma_Bits_1_not_inst1_out),
    .I1(Mux2xBits1_inst1_O),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBits1_inst19_O)
);
Mux2xBits1 Mux2xBits1_inst2 (
    .I0(const_1_1_out),
    .I1(magma_Bits_1_not_inst4_out),
    .S(magma_Bits_1_eq_inst2_out),
    .O(Mux2xBits1_inst2_O)
);
Mux2xBits1 Mux2xBits1_inst20 (
    .I0(Mux2xBits1_inst17_O),
    .I1(magma_Bits_1_not_inst0_out),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBits1_inst20_O)
);
Mux2xBits1 Mux2xBits1_inst3 (
    .I0(const_1_1_out),
    .I1(magma_Bits_1_not_inst5_out),
    .S(magma_Bit_and_inst0_out),
    .O(Mux2xBits1_inst3_O)
);
Mux2xBits1 Mux2xBits1_inst4 (
    .I0(const_1_1_out),
    .I1(magma_Bits_1_not_inst6_out),
    .S(magma_Bits_1_eq_inst4_out),
    .O(Mux2xBits1_inst4_O)
);
Mux2xBits1 Mux2xBits1_inst5 (
    .I0(const_1_1_out),
    .I1(magma_Bits_1_not_inst7_out),
    .S(magma_Bits_1_eq_inst5_out),
    .O(Mux2xBits1_inst5_O)
);
Mux2xBits1 Mux2xBits1_inst6 (
    .I0(const_1_1_out),
    .I1(magma_Bits_1_not_inst8_out),
    .S(magma_Bits_1_eq_inst6_out),
    .O(Mux2xBits1_inst6_O)
);
Mux2xBits1 Mux2xBits1_inst7 (
    .I0(magma_Bits_1_not_inst2_out),
    .I1(Mux2xBits1_inst6_O),
    .S(magma_Bits_3_eq_inst77_out),
    .O(Mux2xBits1_inst7_O)
);
Mux2xBits1 Mux2xBits1_inst8 (
    .I0(Mux2xBits1_inst7_O),
    .I1(magma_Bits_1_not_inst2_out),
    .S(magma_Bits_3_eq_inst66_out),
    .O(Mux2xBits1_inst8_O)
);
Mux2xBits1 Mux2xBits1_inst9 (
    .I0(magma_Bits_1_not_inst0_out),
    .I1(Mux2xBits1_inst5_O),
    .S(magma_Bits_3_eq_inst66_out),
    .O(Mux2xBits1_inst9_O)
);
Mux2xBits3 Mux2xBits3_inst0 (
    .I0(const_0_3_out),
    .I1(const_2_3_out),
    .S(magma_Bits_3_eq_inst0_out),
    .O(Mux2xBits3_inst0_O)
);
Mux2xBits3 Mux2xBits3_inst1 (
    .I0(Mux2xBits3_inst0_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst1_out),
    .O(Mux2xBits3_inst1_O)
);
Mux2xBits3 Mux2xBits3_inst10 (
    .I0(state_reg_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst12_out),
    .O(Mux2xBits3_inst10_O)
);
Mux2xBits3 Mux2xBits3_inst11 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst10_O),
    .S(magma_Bits_3_eq_inst11_out),
    .O(Mux2xBits3_inst11_O)
);
Mux2xBits3 Mux2xBits3_inst12 (
    .I0(Mux2xBits3_inst11_O),
    .I1(const_2_3_out),
    .S(magma_Bits_3_eq_inst14_out),
    .O(Mux2xBits3_inst12_O)
);
Mux2xBits3 Mux2xBits3_inst13 (
    .I0(Mux2xBits3_inst11_O),
    .I1(Mux2xBits3_inst12_O),
    .S(magma_Bits_3_eq_inst13_out),
    .O(Mux2xBits3_inst13_O)
);
Mux2xBits3 Mux2xBits3_inst14 (
    .I0(Mux2xBits3_inst13_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst16_out),
    .O(Mux2xBits3_inst14_O)
);
Mux2xBits3 Mux2xBits3_inst15 (
    .I0(Mux2xBits3_inst13_O),
    .I1(Mux2xBits3_inst14_O),
    .S(magma_Bits_3_eq_inst15_out),
    .O(Mux2xBits3_inst15_O)
);
Mux2xBits3 Mux2xBits3_inst16 (
    .I0(Mux2xBits3_inst15_O),
    .I1(const_4_3_out),
    .S(magma_Bits_3_eq_inst18_out),
    .O(Mux2xBits3_inst16_O)
);
Mux2xBits3 Mux2xBits3_inst17 (
    .I0(Mux2xBits3_inst15_O),
    .I1(Mux2xBits3_inst16_O),
    .S(magma_Bits_3_eq_inst17_out),
    .O(Mux2xBits3_inst17_O)
);
Mux2xBits3 Mux2xBits3_inst18 (
    .I0(Mux2xBits3_inst17_O),
    .I1(const_6_3_out),
    .S(magma_Bits_3_eq_inst20_out),
    .O(Mux2xBits3_inst18_O)
);
Mux2xBits3 Mux2xBits3_inst19 (
    .I0(Mux2xBits3_inst17_O),
    .I1(Mux2xBits3_inst18_O),
    .S(magma_Bits_3_eq_inst19_out),
    .O(Mux2xBits3_inst19_O)
);
Mux2xBits3 Mux2xBits3_inst2 (
    .I0(Mux2xBits3_inst1_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst2_out),
    .O(Mux2xBits3_inst2_O)
);
Mux2xBits3 Mux2xBits3_inst20 (
    .I0(Mux2xBits3_inst19_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst22_out),
    .O(Mux2xBits3_inst20_O)
);
Mux2xBits3 Mux2xBits3_inst21 (
    .I0(Mux2xBits3_inst19_O),
    .I1(Mux2xBits3_inst20_O),
    .S(magma_Bits_3_eq_inst21_out),
    .O(Mux2xBits3_inst21_O)
);
Mux2xBits3 Mux2xBits3_inst22 (
    .I0(Mux2xBits3_inst21_O),
    .I1(const_5_3_out),
    .S(magma_Bits_3_eq_inst24_out),
    .O(Mux2xBits3_inst22_O)
);
Mux2xBits3 Mux2xBits3_inst23 (
    .I0(Mux2xBits3_inst21_O),
    .I1(Mux2xBits3_inst22_O),
    .S(magma_Bits_3_eq_inst23_out),
    .O(Mux2xBits3_inst23_O)
);
Mux2xBits3 Mux2xBits3_inst24 (
    .I0(Mux2xBits3_inst23_O),
    .I1(const_7_3_out),
    .S(magma_Bits_3_eq_inst26_out),
    .O(Mux2xBits3_inst24_O)
);
Mux2xBits3 Mux2xBits3_inst25 (
    .I0(Mux2xBits3_inst23_O),
    .I1(Mux2xBits3_inst24_O),
    .S(magma_Bits_3_eq_inst25_out),
    .O(Mux2xBits3_inst25_O)
);
Mux2xBits3 Mux2xBits3_inst26 (
    .I0(Mux2xBits3_inst25_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst28_out),
    .O(Mux2xBits3_inst26_O)
);
Mux2xBits3 Mux2xBits3_inst27 (
    .I0(Mux2xBits3_inst25_O),
    .I1(Mux2xBits3_inst26_O),
    .S(magma_Bits_3_eq_inst27_out),
    .O(Mux2xBits3_inst27_O)
);
Mux2xBits3 Mux2xBits3_inst28 (
    .I0(Mux2xBits3_inst27_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst30_out),
    .O(Mux2xBits3_inst28_O)
);
Mux2xBits3 Mux2xBits3_inst29 (
    .I0(Mux2xBits3_inst27_O),
    .I1(Mux2xBits3_inst28_O),
    .S(magma_Bits_3_eq_inst29_out),
    .O(Mux2xBits3_inst29_O)
);
Mux2xBits3 Mux2xBits3_inst3 (
    .I0(Mux2xBits3_inst2_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst3_out),
    .O(Mux2xBits3_inst3_O)
);
Mux2xBits3 Mux2xBits3_inst30 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst29_O),
    .S(magma_Bit_not_inst0_out),
    .O(Mux2xBits3_inst30_O)
);
Mux2xBits3 Mux2xBits3_inst31 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst30_O),
    .S(magma_Bits_1_eq_inst1_out),
    .O(Mux2xBits3_inst31_O)
);
Mux2xBits3 Mux2xBits3_inst32 (
    .I0(state_reg_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst34_out),
    .O(Mux2xBits3_inst32_O)
);
Mux2xBits3 Mux2xBits3_inst33 (
    .I0(Mux2xBits3_inst32_O),
    .I1(Mux2xBits3_inst32_O),
    .S(magma_Bits_3_eq_inst35_out),
    .O(Mux2xBits3_inst33_O)
);
Mux2xBits3 Mux2xBits3_inst34 (
    .I0(Mux2xBits3_inst33_O),
    .I1(Mux2xBits3_inst33_O),
    .S(magma_Bits_3_eq_inst36_out),
    .O(Mux2xBits3_inst34_O)
);
Mux2xBits3 Mux2xBits3_inst35 (
    .I0(Mux2xBits3_inst34_O),
    .I1(Mux2xBits3_inst34_O),
    .S(magma_Bits_3_eq_inst37_out),
    .O(Mux2xBits3_inst35_O)
);
Mux2xBits3 Mux2xBits3_inst36 (
    .I0(Mux2xBits3_inst35_O),
    .I1(Mux2xBits3_inst35_O),
    .S(magma_Bits_3_eq_inst38_out),
    .O(Mux2xBits3_inst36_O)
);
Mux2xBits3 Mux2xBits3_inst37 (
    .I0(Mux2xBits3_inst36_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst39_out),
    .O(Mux2xBits3_inst37_O)
);
Mux2xBits3 Mux2xBits3_inst38 (
    .I0(Mux2xBits3_inst37_O),
    .I1(const_5_3_out),
    .S(magma_Bits_3_eq_inst40_out),
    .O(Mux2xBits3_inst38_O)
);
Mux2xBits3 Mux2xBits3_inst39 (
    .I0(Mux2xBits3_inst38_O),
    .I1(const_7_3_out),
    .S(magma_Bits_3_eq_inst41_out),
    .O(Mux2xBits3_inst39_O)
);
Mux2xBits3 Mux2xBits3_inst4 (
    .I0(Mux2xBits3_inst3_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst4_out),
    .O(Mux2xBits3_inst4_O)
);
Mux2xBits3 Mux2xBits3_inst40 (
    .I0(Mux2xBits3_inst39_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst42_out),
    .O(Mux2xBits3_inst40_O)
);
Mux2xBits3 Mux2xBits3_inst41 (
    .I0(Mux2xBits3_inst40_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst43_out),
    .O(Mux2xBits3_inst41_O)
);
Mux2xBits3 Mux2xBits3_inst42 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst41_O),
    .S(magma_Bits_1_eq_inst2_out),
    .O(Mux2xBits3_inst42_O)
);
Mux2xBits3 Mux2xBits3_inst43 (
    .I0(state_reg_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst45_out),
    .O(Mux2xBits3_inst43_O)
);
Mux2xBits3 Mux2xBits3_inst44 (
    .I0(Mux2xBits3_inst43_O),
    .I1(Mux2xBits3_inst43_O),
    .S(magma_Bits_3_eq_inst46_out),
    .O(Mux2xBits3_inst44_O)
);
Mux2xBits3 Mux2xBits3_inst45 (
    .I0(Mux2xBits3_inst44_O),
    .I1(Mux2xBits3_inst44_O),
    .S(magma_Bits_3_eq_inst47_out),
    .O(Mux2xBits3_inst45_O)
);
Mux2xBits3 Mux2xBits3_inst46 (
    .I0(Mux2xBits3_inst45_O),
    .I1(Mux2xBits3_inst45_O),
    .S(magma_Bits_3_eq_inst48_out),
    .O(Mux2xBits3_inst46_O)
);
Mux2xBits3 Mux2xBits3_inst47 (
    .I0(Mux2xBits3_inst46_O),
    .I1(Mux2xBits3_inst46_O),
    .S(magma_Bits_3_eq_inst49_out),
    .O(Mux2xBits3_inst47_O)
);
Mux2xBits3 Mux2xBits3_inst48 (
    .I0(Mux2xBits3_inst47_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst50_out),
    .O(Mux2xBits3_inst48_O)
);
Mux2xBits3 Mux2xBits3_inst49 (
    .I0(Mux2xBits3_inst48_O),
    .I1(const_5_3_out),
    .S(magma_Bits_3_eq_inst51_out),
    .O(Mux2xBits3_inst49_O)
);
Mux2xBits3 Mux2xBits3_inst5 (
    .I0(Mux2xBits3_inst4_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst5_out),
    .O(Mux2xBits3_inst5_O)
);
Mux2xBits3 Mux2xBits3_inst50 (
    .I0(Mux2xBits3_inst49_O),
    .I1(const_7_3_out),
    .S(magma_Bits_3_eq_inst52_out),
    .O(Mux2xBits3_inst50_O)
);
Mux2xBits3 Mux2xBits3_inst51 (
    .I0(Mux2xBits3_inst50_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst53_out),
    .O(Mux2xBits3_inst51_O)
);
Mux2xBits3 Mux2xBits3_inst52 (
    .I0(Mux2xBits3_inst51_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst54_out),
    .O(Mux2xBits3_inst52_O)
);
Mux2xBits3 Mux2xBits3_inst53 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst52_O),
    .S(magma_Bit_and_inst0_out),
    .O(Mux2xBits3_inst53_O)
);
Mux2xBits3 Mux2xBits3_inst54 (
    .I0(state_reg_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst56_out),
    .O(Mux2xBits3_inst54_O)
);
Mux2xBits3 Mux2xBits3_inst55 (
    .I0(Mux2xBits3_inst54_O),
    .I1(Mux2xBits3_inst54_O),
    .S(magma_Bits_3_eq_inst57_out),
    .O(Mux2xBits3_inst55_O)
);
Mux2xBits3 Mux2xBits3_inst56 (
    .I0(Mux2xBits3_inst55_O),
    .I1(Mux2xBits3_inst55_O),
    .S(magma_Bits_3_eq_inst58_out),
    .O(Mux2xBits3_inst56_O)
);
Mux2xBits3 Mux2xBits3_inst57 (
    .I0(Mux2xBits3_inst56_O),
    .I1(Mux2xBits3_inst56_O),
    .S(magma_Bits_3_eq_inst59_out),
    .O(Mux2xBits3_inst57_O)
);
Mux2xBits3 Mux2xBits3_inst58 (
    .I0(Mux2xBits3_inst57_O),
    .I1(Mux2xBits3_inst57_O),
    .S(magma_Bits_3_eq_inst60_out),
    .O(Mux2xBits3_inst58_O)
);
Mux2xBits3 Mux2xBits3_inst59 (
    .I0(Mux2xBits3_inst58_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst61_out),
    .O(Mux2xBits3_inst59_O)
);
Mux2xBits3 Mux2xBits3_inst6 (
    .I0(Mux2xBits3_inst5_O),
    .I1(const_4_3_out),
    .S(magma_Bits_3_eq_inst6_out),
    .O(Mux2xBits3_inst6_O)
);
Mux2xBits3 Mux2xBits3_inst60 (
    .I0(Mux2xBits3_inst59_O),
    .I1(const_5_3_out),
    .S(magma_Bits_3_eq_inst62_out),
    .O(Mux2xBits3_inst60_O)
);
Mux2xBits3 Mux2xBits3_inst61 (
    .I0(Mux2xBits3_inst60_O),
    .I1(const_7_3_out),
    .S(magma_Bits_3_eq_inst63_out),
    .O(Mux2xBits3_inst61_O)
);
Mux2xBits3 Mux2xBits3_inst62 (
    .I0(Mux2xBits3_inst61_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst64_out),
    .O(Mux2xBits3_inst62_O)
);
Mux2xBits3 Mux2xBits3_inst63 (
    .I0(Mux2xBits3_inst62_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst65_out),
    .O(Mux2xBits3_inst63_O)
);
Mux2xBits3 Mux2xBits3_inst64 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst63_O),
    .S(magma_Bits_1_eq_inst4_out),
    .O(Mux2xBits3_inst64_O)
);
Mux2xBits3 Mux2xBits3_inst65 (
    .I0(state_reg_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst67_out),
    .O(Mux2xBits3_inst65_O)
);
Mux2xBits3 Mux2xBits3_inst66 (
    .I0(Mux2xBits3_inst65_O),
    .I1(Mux2xBits3_inst65_O),
    .S(magma_Bits_3_eq_inst68_out),
    .O(Mux2xBits3_inst66_O)
);
Mux2xBits3 Mux2xBits3_inst67 (
    .I0(Mux2xBits3_inst66_O),
    .I1(Mux2xBits3_inst66_O),
    .S(magma_Bits_3_eq_inst69_out),
    .O(Mux2xBits3_inst67_O)
);
Mux2xBits3 Mux2xBits3_inst68 (
    .I0(Mux2xBits3_inst67_O),
    .I1(Mux2xBits3_inst67_O),
    .S(magma_Bits_3_eq_inst70_out),
    .O(Mux2xBits3_inst68_O)
);
Mux2xBits3 Mux2xBits3_inst69 (
    .I0(Mux2xBits3_inst68_O),
    .I1(Mux2xBits3_inst68_O),
    .S(magma_Bits_3_eq_inst71_out),
    .O(Mux2xBits3_inst69_O)
);
Mux2xBits3 Mux2xBits3_inst7 (
    .I0(Mux2xBits3_inst6_O),
    .I1(const_4_3_out),
    .S(magma_Bits_3_eq_inst7_out),
    .O(Mux2xBits3_inst7_O)
);
Mux2xBits3 Mux2xBits3_inst70 (
    .I0(Mux2xBits3_inst69_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst72_out),
    .O(Mux2xBits3_inst70_O)
);
Mux2xBits3 Mux2xBits3_inst71 (
    .I0(Mux2xBits3_inst70_O),
    .I1(const_5_3_out),
    .S(magma_Bits_3_eq_inst73_out),
    .O(Mux2xBits3_inst71_O)
);
Mux2xBits3 Mux2xBits3_inst72 (
    .I0(Mux2xBits3_inst71_O),
    .I1(const_7_3_out),
    .S(magma_Bits_3_eq_inst74_out),
    .O(Mux2xBits3_inst72_O)
);
Mux2xBits3 Mux2xBits3_inst73 (
    .I0(Mux2xBits3_inst72_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst75_out),
    .O(Mux2xBits3_inst73_O)
);
Mux2xBits3 Mux2xBits3_inst74 (
    .I0(Mux2xBits3_inst73_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst76_out),
    .O(Mux2xBits3_inst74_O)
);
Mux2xBits3 Mux2xBits3_inst75 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst74_O),
    .S(magma_Bits_1_eq_inst5_out),
    .O(Mux2xBits3_inst75_O)
);
Mux2xBits3 Mux2xBits3_inst76 (
    .I0(state_reg_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst78_out),
    .O(Mux2xBits3_inst76_O)
);
Mux2xBits3 Mux2xBits3_inst77 (
    .I0(Mux2xBits3_inst76_O),
    .I1(Mux2xBits3_inst76_O),
    .S(magma_Bits_3_eq_inst79_out),
    .O(Mux2xBits3_inst77_O)
);
Mux2xBits3 Mux2xBits3_inst78 (
    .I0(Mux2xBits3_inst77_O),
    .I1(Mux2xBits3_inst77_O),
    .S(magma_Bits_3_eq_inst80_out),
    .O(Mux2xBits3_inst78_O)
);
Mux2xBits3 Mux2xBits3_inst79 (
    .I0(Mux2xBits3_inst78_O),
    .I1(Mux2xBits3_inst78_O),
    .S(magma_Bits_3_eq_inst81_out),
    .O(Mux2xBits3_inst79_O)
);
Mux2xBits3 Mux2xBits3_inst8 (
    .I0(Mux2xBits3_inst7_O),
    .I1(const_6_3_out),
    .S(magma_Bits_3_eq_inst8_out),
    .O(Mux2xBits3_inst8_O)
);
Mux2xBits3 Mux2xBits3_inst80 (
    .I0(Mux2xBits3_inst79_O),
    .I1(Mux2xBits3_inst79_O),
    .S(magma_Bits_3_eq_inst82_out),
    .O(Mux2xBits3_inst80_O)
);
Mux2xBits3 Mux2xBits3_inst81 (
    .I0(Mux2xBits3_inst80_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst83_out),
    .O(Mux2xBits3_inst81_O)
);
Mux2xBits3 Mux2xBits3_inst82 (
    .I0(Mux2xBits3_inst81_O),
    .I1(const_5_3_out),
    .S(magma_Bits_3_eq_inst84_out),
    .O(Mux2xBits3_inst82_O)
);
Mux2xBits3 Mux2xBits3_inst83 (
    .I0(Mux2xBits3_inst82_O),
    .I1(const_7_3_out),
    .S(magma_Bits_3_eq_inst85_out),
    .O(Mux2xBits3_inst83_O)
);
Mux2xBits3 Mux2xBits3_inst84 (
    .I0(Mux2xBits3_inst83_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst86_out),
    .O(Mux2xBits3_inst84_O)
);
Mux2xBits3 Mux2xBits3_inst85 (
    .I0(Mux2xBits3_inst84_O),
    .I1(const_3_3_out),
    .S(magma_Bits_3_eq_inst87_out),
    .O(Mux2xBits3_inst85_O)
);
Mux2xBits3 Mux2xBits3_inst86 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst85_O),
    .S(magma_Bits_1_eq_inst6_out),
    .O(Mux2xBits3_inst86_O)
);
Mux2xBits3 Mux2xBits3_inst87 (
    .I0(state_reg_O),
    .I1(Mux2xBits3_inst86_O),
    .S(magma_Bits_3_eq_inst77_out),
    .O(Mux2xBits3_inst87_O)
);
Mux2xBits3 Mux2xBits3_inst88 (
    .I0(Mux2xBits3_inst87_O),
    .I1(Mux2xBits3_inst75_O),
    .S(magma_Bits_3_eq_inst66_out),
    .O(Mux2xBits3_inst88_O)
);
Mux2xBits3 Mux2xBits3_inst89 (
    .I0(Mux2xBits3_inst88_O),
    .I1(Mux2xBits3_inst64_O),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xBits3_inst89_O)
);
Mux2xBits3 Mux2xBits3_inst9 (
    .I0(Mux2xBits3_inst8_O),
    .I1(const_5_3_out),
    .S(magma_Bits_3_eq_inst9_out),
    .O(Mux2xBits3_inst9_O)
);
Mux2xBits3 Mux2xBits3_inst90 (
    .I0(Mux2xBits3_inst89_O),
    .I1(Mux2xBits3_inst53_O),
    .S(magma_Bits_3_eq_inst44_out),
    .O(Mux2xBits3_inst90_O)
);
Mux2xBits3 Mux2xBits3_inst91 (
    .I0(Mux2xBits3_inst90_O),
    .I1(Mux2xBits3_inst42_O),
    .S(magma_Bits_3_eq_inst33_out),
    .O(Mux2xBits3_inst91_O)
);
Mux2xBits3 Mux2xBits3_inst92 (
    .I0(Mux2xBits3_inst91_O),
    .I1(const_1_3_out),
    .S(magma_Bits_3_eq_inst32_out),
    .O(Mux2xBits3_inst92_O)
);
Mux2xBits3 Mux2xBits3_inst93 (
    .I0(Mux2xBits3_inst92_O),
    .I1(Mux2xBits3_inst31_O),
    .S(magma_Bits_3_eq_inst10_out),
    .O(Mux2xBits3_inst93_O)
);
Mux2xEnable Mux2xEnable_inst0 (
    .I0(bit_const_1_None_out),
    .I1(bit_const_0_None_out),
    .S(magma_Bits_3_eq_inst66_out),
    .O(Mux2xEnable_inst0_O)
);
Mux2xEnable Mux2xEnable_inst1 (
    .I0(bit_const_0_None_out),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst66_out),
    .O(Mux2xEnable_inst1_O)
);
Mux2xEnable Mux2xEnable_inst2 (
    .I0(Mux2xEnable_inst0_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xEnable_inst2_O)
);
Mux2xEnable Mux2xEnable_inst3 (
    .I0(Mux2xEnable_inst1_O),
    .I1(bit_const_1_None_out),
    .S(magma_Bits_3_eq_inst55_out),
    .O(Mux2xEnable_inst3_O)
);
wire [1:0] SRAMSMR_inst0_RCE;
assign SRAMSMR_inst0_RCE = {DataFromClient_O[1],DataFromClient_O[0]};
SRAMSMR SRAMSMR_inst0 (
    .CEn(bit_const_0_None_out),
    .WDATA(DataFromClient_O),
    .WEn(Mux2xEnable_inst3_O),
    .RDATA(SRAMSMR_inst0_RDATA),
    .REn(Mux2xEnable_inst2_O),
    .CLK(CLK),
    .ADDR(Mux2xBits11_inst7_O),
    .RCE(SRAMSMR_inst0_RCE),
    .RCF0A(const_0_2_out),
    .RCF1A(const_1_2_out),
    .deep_sleep(bit_const_0_None_out),
    .power_gate(bit_const_0_None_out),
    .wake_ack(SRAMSMR_inst0_wake_ack),
    .current_state(SRAMSMR_inst0_current_state)
);
corebit_const #(
    .value(1'b0)
) bit_const_0_None (
    .out(bit_const_0_None_out)
);
corebit_const #(
    .value(1'b1)
) bit_const_1_None (
    .out(bit_const_1_None_out)
);
coreir_const #(
    .value(1'h0),
    .width(1)
) const_0_1 (
    .out(const_0_1_out)
);
coreir_const #(
    .value(2'h0),
    .width(2)
) const_0_2 (
    .out(const_0_2_out)
);
coreir_const #(
    .value(3'h0),
    .width(3)
) const_0_3 (
    .out(const_0_3_out)
);
coreir_const #(
    .value(16'h000d),
    .width(16)
) const_13_16 (
    .out(const_13_16_out)
);
coreir_const #(
    .value(16'h000f),
    .width(16)
) const_15_16 (
    .out(const_15_16_out)
);
coreir_const #(
    .value(1'h1),
    .width(1)
) const_1_1 (
    .out(const_1_1_out)
);
coreir_const #(
    .value(2'h1),
    .width(2)
) const_1_2 (
    .out(const_1_2_out)
);
coreir_const #(
    .value(3'h1),
    .width(3)
) const_1_3 (
    .out(const_1_3_out)
);
coreir_const #(
    .value(3'h2),
    .width(3)
) const_2_3 (
    .out(const_2_3_out)
);
coreir_const #(
    .value(3'h3),
    .width(3)
) const_3_3 (
    .out(const_3_3_out)
);
coreir_const #(
    .value(3'h4),
    .width(3)
) const_4_3 (
    .out(const_4_3_out)
);
coreir_const #(
    .value(3'h5),
    .width(3)
) const_5_3 (
    .out(const_5_3_out)
);
coreir_const #(
    .value(11'h006),
    .width(11)
) const_6_11 (
    .out(const_6_11_out)
);
coreir_const #(
    .value(3'h6),
    .width(3)
) const_6_3 (
    .out(const_6_3_out)
);
coreir_const #(
    .value(3'h7),
    .width(3)
) const_7_3 (
    .out(const_7_3_out)
);
Register_unq1 initreg (
    .I(const_0_1_out),
    .O(initreg_O),
    .CLK(CLK)
);
corebit_and magma_Bit_and_inst0 (
    .in0(magma_Bits_1_eq_inst3_out),
    .in1(SRAMSMR_inst0_wake_ack),
    .out(magma_Bit_and_inst0_out)
);
corebit_not magma_Bit_not_inst0 (
    .in(magma_Bits_3_eq_inst31_out),
    .out(magma_Bit_not_inst0_out)
);
coreir_eq #(
    .width(1)
) magma_Bits_1_eq_inst0 (
    .in0(initreg_O),
    .in1(const_1_1_out),
    .out(magma_Bits_1_eq_inst0_out)
);
coreir_eq #(
    .width(1)
) magma_Bits_1_eq_inst1 (
    .in0(CommandFromClient_valid_O),
    .in1(const_1_1_out),
    .out(magma_Bits_1_eq_inst1_out)
);
coreir_eq #(
    .width(1)
) magma_Bits_1_eq_inst2 (
    .in0(DataFromClient_valid_O),
    .in1(const_1_1_out),
    .out(magma_Bits_1_eq_inst2_out)
);
coreir_eq #(
    .width(1)
) magma_Bits_1_eq_inst3 (
    .in0(DataToClient_ready_O),
    .in1(const_1_1_out),
    .out(magma_Bits_1_eq_inst3_out)
);
coreir_eq #(
    .width(1)
) magma_Bits_1_eq_inst4 (
    .in0(DataFromClient_valid_O),
    .in1(const_1_1_out),
    .out(magma_Bits_1_eq_inst4_out)
);
coreir_eq #(
    .width(1)
) magma_Bits_1_eq_inst5 (
    .in0(DataFromClient_valid_O),
    .in1(const_1_1_out),
    .out(magma_Bits_1_eq_inst5_out)
);
coreir_eq #(
    .width(1)
) magma_Bits_1_eq_inst6 (
    .in0(DataToClient_ready_O),
    .in1(const_1_1_out),
    .out(magma_Bits_1_eq_inst6_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst0 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst0_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst1 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst1_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst2 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst2_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst3 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst3_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst4 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst4_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst5 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst5_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst6 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst6_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst7 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst7_out)
);
coreir_not #(
    .width(1)
) magma_Bits_1_not_inst8 (
    .in(const_1_1_out),
    .out(magma_Bits_1_not_inst8_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst0 (
    .in0(state_reg_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst0_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst1 (
    .in0(state_reg_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst1_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst10 (
    .in0(Mux2xBits3_inst9_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst10_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst11 (
    .in0(state_reg_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst11_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst12 (
    .in0(CommandFromClient_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst12_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst13 (
    .in0(state_reg_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst13_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst14 (
    .in0(CommandFromClient_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst14_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst15 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst15_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst16 (
    .in0(CommandFromClient_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst16_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst17 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst17_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst18 (
    .in0(CommandFromClient_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst18_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst19 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst19_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst2 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst2_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst20 (
    .in0(CommandFromClient_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst20_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst21 (
    .in0(state_reg_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst21_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst22 (
    .in0(CommandFromClient_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst22_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst23 (
    .in0(state_reg_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst23_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst24 (
    .in0(CommandFromClient_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst24_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst25 (
    .in0(state_reg_O),
    .in1(const_6_3_out),
    .out(magma_Bits_3_eq_inst25_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst26 (
    .in0(CommandFromClient_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst26_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst27 (
    .in0(state_reg_O),
    .in1(const_7_3_out),
    .out(magma_Bits_3_eq_inst27_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst28 (
    .in0(CommandFromClient_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst28_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst29 (
    .in0(state_reg_O),
    .in1(const_5_3_out),
    .out(magma_Bits_3_eq_inst29_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst3 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst3_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst30 (
    .in0(CommandFromClient_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst30_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst31 (
    .in0(Mux2xBits3_inst29_O),
    .in1(state_reg_O),
    .out(magma_Bits_3_eq_inst31_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst32 (
    .in0(Mux2xBits3_inst9_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst32_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst33 (
    .in0(Mux2xBits3_inst9_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst33_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst34 (
    .in0(state_reg_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst34_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst35 (
    .in0(state_reg_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst35_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst36 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst36_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst37 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst37_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst38 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst38_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst39 (
    .in0(state_reg_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst39_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst4 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst4_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst40 (
    .in0(state_reg_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst40_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst41 (
    .in0(state_reg_O),
    .in1(const_6_3_out),
    .out(magma_Bits_3_eq_inst41_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst42 (
    .in0(state_reg_O),
    .in1(const_7_3_out),
    .out(magma_Bits_3_eq_inst42_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst43 (
    .in0(state_reg_O),
    .in1(const_5_3_out),
    .out(magma_Bits_3_eq_inst43_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst44 (
    .in0(Mux2xBits3_inst9_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst44_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst45 (
    .in0(state_reg_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst45_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst46 (
    .in0(state_reg_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst46_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst47 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst47_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst48 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst48_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst49 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst49_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst5 (
    .in0(state_reg_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst5_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst50 (
    .in0(state_reg_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst50_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst51 (
    .in0(state_reg_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst51_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst52 (
    .in0(state_reg_O),
    .in1(const_6_3_out),
    .out(magma_Bits_3_eq_inst52_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst53 (
    .in0(state_reg_O),
    .in1(const_7_3_out),
    .out(magma_Bits_3_eq_inst53_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst54 (
    .in0(state_reg_O),
    .in1(const_5_3_out),
    .out(magma_Bits_3_eq_inst54_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst55 (
    .in0(Mux2xBits3_inst9_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst55_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst56 (
    .in0(state_reg_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst56_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst57 (
    .in0(state_reg_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst57_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst58 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst58_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst59 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst59_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst6 (
    .in0(state_reg_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst6_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst60 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst60_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst61 (
    .in0(state_reg_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst61_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst62 (
    .in0(state_reg_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst62_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst63 (
    .in0(state_reg_O),
    .in1(const_6_3_out),
    .out(magma_Bits_3_eq_inst63_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst64 (
    .in0(state_reg_O),
    .in1(const_7_3_out),
    .out(magma_Bits_3_eq_inst64_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst65 (
    .in0(state_reg_O),
    .in1(const_5_3_out),
    .out(magma_Bits_3_eq_inst65_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst66 (
    .in0(Mux2xBits3_inst9_O),
    .in1(const_6_3_out),
    .out(magma_Bits_3_eq_inst66_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst67 (
    .in0(state_reg_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst67_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst68 (
    .in0(state_reg_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst68_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst69 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst69_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst7 (
    .in0(state_reg_O),
    .in1(const_6_3_out),
    .out(magma_Bits_3_eq_inst7_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst70 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst70_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst71 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst71_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst72 (
    .in0(state_reg_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst72_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst73 (
    .in0(state_reg_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst73_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst74 (
    .in0(state_reg_O),
    .in1(const_6_3_out),
    .out(magma_Bits_3_eq_inst74_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst75 (
    .in0(state_reg_O),
    .in1(const_7_3_out),
    .out(magma_Bits_3_eq_inst75_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst76 (
    .in0(state_reg_O),
    .in1(const_5_3_out),
    .out(magma_Bits_3_eq_inst76_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst77 (
    .in0(Mux2xBits3_inst9_O),
    .in1(const_5_3_out),
    .out(magma_Bits_3_eq_inst77_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst78 (
    .in0(state_reg_O),
    .in1(const_0_3_out),
    .out(magma_Bits_3_eq_inst78_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst79 (
    .in0(state_reg_O),
    .in1(const_1_3_out),
    .out(magma_Bits_3_eq_inst79_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst8 (
    .in0(state_reg_O),
    .in1(const_7_3_out),
    .out(magma_Bits_3_eq_inst8_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst80 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst80_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst81 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst81_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst82 (
    .in0(state_reg_O),
    .in1(const_3_3_out),
    .out(magma_Bits_3_eq_inst82_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst83 (
    .in0(state_reg_O),
    .in1(const_2_3_out),
    .out(magma_Bits_3_eq_inst83_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst84 (
    .in0(state_reg_O),
    .in1(const_4_3_out),
    .out(magma_Bits_3_eq_inst84_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst85 (
    .in0(state_reg_O),
    .in1(const_6_3_out),
    .out(magma_Bits_3_eq_inst85_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst86 (
    .in0(state_reg_O),
    .in1(const_7_3_out),
    .out(magma_Bits_3_eq_inst86_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst87 (
    .in0(state_reg_O),
    .in1(const_5_3_out),
    .out(magma_Bits_3_eq_inst87_out)
);
coreir_eq #(
    .width(3)
) magma_Bits_3_eq_inst9 (
    .in0(state_reg_O),
    .in1(const_5_3_out),
    .out(magma_Bits_3_eq_inst9_out)
);
Register_unq3 mem_addr_reg (
    .I(Mux2xBits16_inst12_O),
    .O(mem_addr_reg_O),
    .CE(Mux2xBit_inst16_O),
    .CLK(CLK)
);
Register_unq3 mem_data_reg (
    .I(DataFromClient_O),
    .O(mem_data_reg_O),
    .CE(bit_const_1_None_out),
    .CLK(CLK)
);
wire [1:0] redundancy_reg_I;
assign redundancy_reg_I = {DataFromClient_O[1],DataFromClient_O[0]};
Register_unq2 redundancy_reg (
    .I(redundancy_reg_I),
    .O(redundancy_reg_O),
    .CE(Mux2xBit_inst19_O),
    .CLK(CLK)
);
Register state_reg (
    .I(Mux2xBits3_inst93_O),
    .O(state_reg_O),
    .CLK(CLK)
);
assign receive_ready = DataFromClient_ready_O;
assign offer_ready = CommandFromClient_ready_O;
assign send = DataToClient_O;
assign send_valid = DataToClient_valid_O;
assign current_state = state_reg_O;
endmodule

