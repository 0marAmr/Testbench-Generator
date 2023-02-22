#To do list: 
#   clock generator block

HDL_file_name = 'FA' # str(input("Enter verilog file name: "))
file = open(HDL_file_name+'.v', 'r')
rtl_code = file.read()
test_bench=open(HDL_file_name+'_tb.v', 'w')

# remove comments from rtl_code
while("//" in rtl_code):
    rtl_code = rtl_code[:rtl_code.find("//")] + rtl_code[rtl_code.find("\n",rtl_code.find("//")) :]

rtl_code = " ".join(rtl_code.split()) #remove all white spaces


# get module name
module_name_start_index = rtl_code.find("module") + 6
module_name_stop_index = rtl_code.find("(")
module_name = rtl_code[module_name_start_index:module_name_stop_index]

# check if there is a clock signal 
clk_signal = 1 if "clk" in rtl_code else 0
clk_period_value = 20

instance_name = 'uut' 


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
print(rtl_code)

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
            input_vector.append(signal)
        elif "output" in temp:
            output_vector.append(signal)
        break
    
    if "input" in temp :
        if ']' in temp:
            size = temp[temp.find('['): temp.find(']')+1]
            signal = ''
            temp = "input"
        elif char == "," or char ==';':
            input_vector.append(size + " " + signal)
            signal = ''
        elif "output" in temp:
            temp = "output"
            signal = ''
            size = ''
            discard_char = 1
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
            output_vector.append(signal)
            signal = ''
        elif "input" in temp:
            temp = "input"
            signal = ''
            discard_char = 1
        elif discard_char:
            discard_char  = 0
            continue
        else :
            signal += char

# remove wire, reg from signals names
for i,signal in enumerate(input_vector):
    if "wire" in signal:
        input_vector[i] = signal[signal.find("wire")+4:].strip()
    elif "reg" in signal:
        input_vector[i] = signal[signal.find("reg")+3:].strip()

for i,signal in enumerate(output_vector):
    if "wire" in signal:
        output_vector[i] = signal[signal.find("wire")+4:].strip()
    elif "reg" in signal:
        output_vector[i] = signal[signal.find("reg")+4:].strip()

test_bench.write("/*test bench is automatically generated*/\n\n")
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

for input in input_vector:
    if ']' in input:
        input = input[input.find(']')+1:]
    test_bench.write("\t."+input+f'({input})\n')

for output in output_vector:
    if ']' in output:
        output = output[output.find(']')+1:]
    test_bench.write("\t."+output+f'({output})\n')

print(input_vector)
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
        break
        
############ initial block ############
test_bench.write("\n\n// test vector generator\n")
test_bench.write("initial "+ "begin\n\n")
test_bench.write(f"@(negedge {signal}); // wait for the device to reset\n\n")

test_bench.write("$finish; \nend" +'\n')

test_bench.write("\nendmodule")
