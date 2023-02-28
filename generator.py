HDL_file_name = str(input("Enter verilog file name: "))
file = open(HDL_file_name+'.v', 'r')
timeunit = '1ns'
timeprecision = '1ps'
delay=10
rtl_code = file.read()
test_bench=open(HDL_file_name+'_tb.v', 'w')

# remove comments from rtl_code
while("//" in rtl_code):
    rtl_code = rtl_code[:rtl_code.find("//")] + rtl_code[rtl_code.find("\n",rtl_code.find("//")) :]
while("/*" in rtl_code):
    rtl_code = rtl_code[:rtl_code.find("/*")] + rtl_code[rtl_code.find("*/")+2:]

rtl_code = " ".join(rtl_code.split()) #remove all white spaces

# get module name
module_name_start_index = rtl_code.find("module") + 6
module_name_stop_index = rtl_code.find("(") if rtl_code.find("#") == -1  else rtl_code.find("#")
module_name = rtl_code[module_name_start_index:module_name_stop_index].strip()

# check if there is a clock signal 
clk_signal = 1 if "clk" in rtl_code else 0
clk_period_value = 20

# check for reset signal
reset_signal = 0

instance_name = 'UUT' # default instance name


## trim the rtl code to get the inputs and outputs
# first index
if rtl_code.find("input") < rtl_code.find("output"):
    first_index = rtl_code.find("input")
else:
    first_index = rtl_code.find("output")
# last index
if rtl_code.rfind("output") > rtl_code.rfind("input"):
    last_index = rtl_code.find(';',rtl_code.rfind("output"))+1 # 1 is added to include the semi-colon @ the end
else:
    last_index = rtl_code.find(';',rtl_code.rfind("input"))+1
    
rtl_code = rtl_code[first_index:last_index]

rtl_code = [char for char in rtl_code if char != ' ' ] # convert the code to a list of characters

input_vector=[]
output_vector=[]

temp = ''
signal = ''
size = ''
discard_char = 1 # discard the first captured character


for i, char in enumerate(rtl_code):
    temp = temp + char
   
    if "input" in temp and "output" in temp:
        temp = "input" if (temp.find("input") >  temp.find("output")) else "output"
        signal = ''
        size = ''
        discard_char = 1
         
    if temp.count("input") > 1 : 
        temp = "input"
        signal = ''
        size = ''
        continue
    elif temp.count("output") > 1 : 
        temp = "output"
        signal = ''
        size = ''
        continue
        
    if char == ')' :
        if "input" in temp :
            input_vector.append(size + " " + signal)
        elif "output" in temp:
            output_vector.append(size + " " + signal)
        break
    
    if "input" in temp :
        if ']' in temp:
            size = temp[temp.find('['): temp.find(']')+1]
            signal = ''
            temp = "input"
        elif char == "," or char ==';':
            input_vector.append(size + " " + signal)
            signal = ''
        elif discard_char:
            discard_char  = 0
            continue
        else: 
            signal += char
    
    if "output" in temp :
        if ']' in temp:
            size = temp[temp.find('['): temp.find(']')+1]
            signal = ''
            temp = "output"
        elif char == ',' or char ==';':
            output_vector.append(size + " " + signal)
            signal = ''
        elif discard_char:
            discard_char  = 0
            continue
        else :
            signal += char

# remove wire, reg from signals names
for i,signal in enumerate(input_vector):
    if "wire" in signal:
        input_vector[i] = signal[signal.find("wire")+4:]
    elif "reg" in signal:
        input_vector[i] = signal[signal.find("reg")+3:]

for i,signal in enumerate(output_vector):
    if "wire" in signal:
        output_vector[i] = signal[signal.find("wire")+4:]
    elif "reg" in signal:
        output_vector[i] = signal[signal.find("reg")+4:]

test_bench.write("/*test bench is automatically generated*/\n\n")
test_bench.write("`include \"" +  HDL_file_name + '.v\"' +  '\n')
test_bench.write("`timescale " + timeunit + '/' + timeprecision + '\n')
test_bench.write("module ")
test_bench.write(module_name+'_tb' + ';\n\n')

############ signals declaration ############
test_bench.write("// input signals\n")
for input in input_vector:
    test_bench.write("reg "+input+';\n')

test_bench.write("\n// output signals\n")
for output in output_vector:
    test_bench.write("wire "+ output+';\n')

############ instantiation ############
test_bench.write("\n// instantiation\n")
test_bench.write(module_name + ' ' + instance_name + "(\n")

print(input_vector)
print(output_vector)

for input in input_vector:
    if ']' in input:
        input = input[input.find(']')+1:]
    test_bench.write("\t."+input+f'({input}),\n')

for index, output in enumerate(output_vector):
    print(f"{index}: {output}")
    if ']' in output:
        output = output[output.find(']')+1:]
    if index != len(output_vector)-1:
        test_bench.write("\t."+output+f'({output}),\n')
    else:
        test_bench.write("\t."+output+f'({output})\n')

test_bench.write("\t);")

############ clock generator block ############
if clk_signal:
    test_bench.write("\n\n// clock signal\n")
    test_bench.write(f"parameter PERIOD  = {clk_period_value};\n\n")
    test_bench.write("initial "+ "begin\n")
    test_bench.write("clk = 0;\n")
    test_bench.write("forever #(PERIOD/2)  clk=~clk; \nend" +'\n')
    
############ active low reset block ############
for signal in input_vector:
    if "reset" in signal:
        test_bench.write("\n\n// reset pulse\n")
        test_bench.write("initial "+ "begin\n")
        test_bench.write(f"{signal} = 1'b0;\n")
        test_bench.write("#(PERIOD/2);\n")
        test_bench.write(f"{signal} = 1'b1;\n")
        test_bench.write(" end" +'\n')
        reset_signal = 1
        break
        
############ initial block ############
test_bench.write("\n\n// test vector generator\n")
test_bench.write("initial "+ "begin\n")
if reset_signal:
    test_bench.write(f"@(negedge {signal}); // wait for the device to reset\n\n")

test_bench.write("\t/* Dumping Files */\n")
test_bench.write(f"\t$dumpfile(\"{module_name} _tb.vcd\");\n");
test_bench.write(f"\t$dumpvars(1,{module_name}_tb);\n");

test_bench.write("\t/* Generate Test Cases */\n")
# if comb circuit 
i=0
while i < 2**len(input_vector):
    test_bench.write(f"\t#{delay}")
    for j, value in enumerate(input_vector): 
        test_bench.write(f"{value}={(i & (1<<len(input_vector)- j-1)) >> len(input_vector)- j-1};")
    test_bench.write("\n")
    i=i+1

test_bench.write(f"\t#{delay} $finish;\n\tend\n")
test_bench.write("\nendmodule")
