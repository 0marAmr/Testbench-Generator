HDL_name = 'FA' # str(input("Enter verilog file name: "))
file = open(HDL_name+'.v', 'r')
test_bench=open(HDL_name+'_tb.v', 'w')

list =file.read().split()
print(list) 
print(type(list))
input_vector=[]
output_vector=[]
start1=0
end1=0
end2=0


for i, value in enumerate(list):
    if value == 'input':
        start1=i
    if value == 'output':
        end1=i        
    if value == ');':
        end2=i
        break
    

input_vector=list[start1+1:end1]
input_vector[-1]=input_vector[-1].rstrip(',')
output_vector=list[end1+1:end2]
print(input_vector)
print(output_vector)

test_bench.write("module ")
test_bench.write(HDL_name+'_tb' + ';\n\n')
test_bench.write("reg "+' '.join(input_vector)+';\n')
test_bench.write("wire "+' '.join(output_vector)+';\n\n')


test_bench.write("initial "+ "begin" +'\n')
test_bench.write('\n')
test_bench.write("end" +'\n')



test_bench.write("\nendmodule")
