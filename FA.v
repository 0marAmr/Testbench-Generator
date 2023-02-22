module FA(A, B, C_in, S, C_out);
 input [3:0] A, B, C_in;
 output S, C_out;
assign {C_out, S} = A + B + C_in;
endmodule