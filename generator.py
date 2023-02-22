#To do list: 
#   deal with comments in code
#   clock generator block

HDL_name = 'FA' # str(input("Enter verilog file name: "))
file = open(HDL_name+'.v', 'r')
test_bench=open(HDL_name+'_tb.v', 'w')

# before removing spaces we'll make use of \n to eliminate comments :)

rtl_code = " ".join(file.read().split()) #remove all white spaces

# get module name
module_name_start_index = rtl_code.find("module") + 6
module_name_stop_index = rtl_code.find("(")
module_name = rtl_code[module_name_start_index:module_name_stop_index]

instance_name = 'uut'

## trim the rtl code to get the inputs and outputs

if rtl_code.find("input") < rtl_code.find("output"):
    first_index = rtl_code.find("input")
else:
    first_index = rtl_code.find("output")

if rtl_code.rfind("output") > rtl_code.rfind("input"):
    last_index = rtl_code[rtl_code.rfind("output"):].find(';')+rtl_code.rfind("output")+1
else:
    last_index = rtl_code[rtl_code.rfind("input"):].find(';')+rtl_code.rfind("input") +1

rtl_code = rtl_code[first_index:last_index]

rtl_code = [char for char in rtl_code if char != ' ' ] # convert the code to a list of characters

input_vector=[]
output_vector=[]

temp = ''
signal = ''
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
        continue
    elif temp.count("output") > 1 : 
        temp = "output"
        signal = ''
        continue
        
    if char == ')' :
        if "input" in temp :
            input_vector.append(signal)
        elif "output" in temp:
            output_vector.append(signal)
        break
    
    if "input" in temp :
        if char == "," or char ==';':
            input_vector.append(signal)
            signal = ''
        elif "output" in temp:
            temp = "output"
            signal = ''
            discard_char = 1
        elif discard_char:
            discard_char  = 0
            continue
        else: 
            signal += char
    
    if "output" in temp :
        if char == ',' or char ==';':
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
            

test_bench.write("module ")
test_bench.write(HDL_name+'_tb' + ';\n\n')

############ signals declaration ############
test_bench.write("// input signals\n")
for input in input_vector:
    test_bench.write("reg "+input+';\n')

test_bench.write("\n// output signals\n")
for output in output_vector:
    test_bench.write("wire "+ output+';\n')

############ instantiation ############
test_bench.write("\n// instantiation\n")
test_bench.write(module_name + instance_name + "(\n")

for input in input_vector:
    if ']' in input:
        input = input[input.find(']')+1:]
    test_bench.write("\t."+input+f'({input})\n')

for output in output_vector:
    if ']' in output:
        output = output[output.find(']')+1:]
    test_bench.write("\t."+output+f'({output})\n')
    
test_bench.write("\t);")

############ initial block ############
test_bench.write("\n\n// test vector generator\n")
test_bench.write("initial "+ "begin" +'\n')
test_bench.write('\n')
test_bench.write("$finish; \nend" +'\n')

test_bench.write("\nendmodule")
