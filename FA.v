module FA(A, B, C_in, S, C_out);
 input A, B, C_in;
 output S, C_out;
assign {C_out, S} = A + B + C_in;
endmodule
