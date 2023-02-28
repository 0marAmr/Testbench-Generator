module Mohamed_Khalid(A, B, C_in, Sum, C_out);
    // comment
    input A, B, C_in;
    output Sum, C_out;
    assign {C_out, Sum} = A + B + C_in;

endmodule