from sample import Sample, Trace, convertFileType
from formulaTree import Formula
import argparse
import os, shutil
import datetime

def genSysliteTraces(input_file, output_file):
 	allTraces = Sample(positive=[], negative=[], is_words=False)
 	allTraces.readFromFile(input_file)

 	num_prop = len(allTraces.positive[0].vector[0])
	
 	prop_list = [chr(ord('p')+i) for i in range(num_prop)]

 	allLines= [','.join(prop_list)]
 	allLines.append('\n---\n')

 	for trace in allTraces.positive:
 		trace_line = ';'.join([','.join([str(int(prop)) for prop in letter]) for letter in trace.vector])
 		allLines.append(trace_line+'\n')

 	allLines.append('---')

 	for trace in allTraces.negative:
 		trace_line = ';'.join([','.join([str(int(prop)) for prop in letter]) for letter in trace.vector])
 		allLines.append('\n'+trace_line)

 	syslite_file = output_file
 	f = open(syslite_file, "w")
 	f.writelines(allLines)


def generateBenchmarks(formula_file, trace_type, sample_sizes, trace_lengths, operators, output_folder = '.', syslite=False):

	traces_folder = output_folder+'/TracesFiles/' 
	os.makedirs(traces_folder)

	if trace_type == 'words':
		words_folder = output_folder+'/WordsFiles/'
		os.makedirs(words_folder)

	if syslite:
		syslite_folder = output_folder+'/SysliteFiles/'
		os.makedirs(syslite_folder)

	with open(formula_file, 'r') as file:
		formula_num=0
		for line in file:
			formula = Formula.convertTextToFormula(line)
			formula_num+=1
			print('---------------Generating Benchmarks for formula %s---------------'%formula.prettyPrint())
			for size in sample_sizes:
				for length_range in trace_lengths:
						length_mean = (length_range[0]+length_range[1])//2
						sample=Sample(positive=[], negative=[])
						trace_file = traces_folder+'f:'+str(formula_num)+'-'+ 'nw:'+str(size)+'-'+'ml:'+str(length_mean)+'.trace'
						
						if trace_type == 'words':
							word_file = words_folder+'f:'+ str(formula_num)+'-'+ 'nw:'+str(size)+'-'+ 'ml:'+str(length_mean)+'.words'
							sample.generator(formula=formula, length_range=length_range, num_traces=size, filename=word_file, is_word=(trace_type=='words'))
							convertFileType(wordfile=word_file, tracefile=trace_file, operators=operators)
						else:
							sample.generator(formula=formula, length_range=length_range, num_traces=size, filename=trace_file, is_words=(trace_type=='words'), operators=operators)

						if syslite:
							syslite_file = syslite_folder +'f:'+str(formula_num)+'-'+ 'nw:'+str(size)+'-'+'ml:'+str(length_mean)+'.trace'
							genSysliteTraces(trace_file, syslite_file)

#Data type for parser
def tupleList(s):
	try:
		return tuple(map(int , s.split(',')))
	except:
		print("Wrong format; provide comma separated values")

    
def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--formula_file', dest='formula_file', default = 'formulas.txt')
	parser.add_argument('--trace_type', dest='trace_type', default = 'trace')
	parser.add_argument('--operators', dest='operators', default = ['F', 'G', 'X', '!', '&', '|'], type=list)
	parser.add_argument('--size', dest='sample_sizes', default=[(100,100)], nargs='+', type=tupleList)
	parser.add_argument('--lengths', dest='trace_lengths', default=[(10, 12)], nargs='+', type=tupleList)
	parser.add_argument('--output_folder', dest='output_folder', default = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	parser.add_argument('--syslite', dest='syslite', action='store_true', default=True)

	args,unknown = parser.parse_known_args()

	formula_file = args.formula_file
	trace_type = args.trace_type
	sample_sizes = list(args.sample_sizes)
	trace_lengths = list(args.trace_lengths)
	output_folder = args.output_folder
	syslite = bool(args.syslite)
	operators = list(args.operators)
	print(sample_sizes, trace_lengths)

	#For generating a fresh set of benchmarks
	if os.path.exists(output_folder):
		shutil.rmtree(output_folder)

	os.makedirs(output_folder)
	shutil.copyfile(formula_file, output_folder+'/'+formula_file)
	generateBenchmarks(formula_file, trace_type, sample_sizes, trace_lengths, operators, output_folder, syslite)

 
if __name__=='__main__':
	main()