from sample import Sample, Trace, convertFileType
from formulaTree import Formula
import argparse
import os, shutil
import datetime

def genSysliteTraces(input_file, output_file):
 	allTraces = Sample(positive=[], negative=[], is_words=False)
 	allTraces.readFromFile(input_file)

 	num_prop = len(allTraces.positive[0].vector[0])

 	prop_list = allTraces.alphabet
	
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


def generateBenchmarks(formula_file, trace_type, sample_sizes, trace_lengths, operators, total_num, output_folder, syslite, gen_method):

	traces_folder = output_folder+'/TracesFiles/' 
	os.makedirs(traces_folder)

	#if trace_type == 'words':
	#	words_folder = output_folder+'/TracesFiles/'
	#	os.makedirs(words_folder)

	if syslite:
		syslite_folder = output_folder+'/SysliteFiles/'
		os.makedirs(syslite_folder)

	generated_files = []
	with open(formula_file, 'r') as file:
		formula_num=0
		for line in file:
			#Has a makeshift addition of trace lengths
			formula_text, alphabet, lengths = line.split(';')
			alphabet = alphabet.split(',')
			alphabet[-1] = alphabet[-1].rstrip('\n')
			trace_lengths = lengths.split(',')
			trace_lengths = [(int(i),int(i)) for i in trace_lengths]

			formula = Formula.convertTextToFormula(formula_text)
	
			formula_num+=1
			print('---------------Generating Benchmarks for formula %s---------------'%formula.prettyPrint())
			
			for size in sample_sizes:
				for length_range in trace_lengths:
					for num in range(total_num):
						length_mean = (length_range[0]+length_range[1])//2
						sample=Sample(positive=[], negative=[])

						trace_file = traces_folder+'f:'+str(formula_num).zfill(2)+'-'+'nw:'+str((size[0]+size[1])//2).zfill(3)+'-'+'ml:'+str(length_mean).zfill(2)+'-'+str(num)+'.trace'
						generated_files.append(trace_file)

						if gen_method=='dfa_method':
							sample.generator_dfa_in_batch_advanced(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)
						# sample.generator(formula=formula, length_range=length_range, num_traces=size, filename=word_file, is_word=(trace_type=='words'))
						elif gen_method=='random':
							sample.generator(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)
						elif gen_method=='random_walk':
							sample.generator_random_walk(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)


							#convertFileType(wordfile=word_file, tracefile=trace_file, operators=operators)
						# else:

						# 	if gen_method=='dfa_method':
						# 		sample.generator_dfa_in_batch_advanced(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)
						# 	elif gen_method=='random':
						# 		sample.generator(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)
						# 	elif gen_method=='random_walk':
						# 		sample.generator_random_walk(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)
							

						# sample.generator(formula=formula, length_range=length_range, num_traces=size, filename=trace_file, is_words=(trace_type=='words'), operators=operators)


						if sample.isFormulaConsistent(formula):
							print("Formula is consistent with sample")

						if syslite:
							syslite_file = syslite_folder +'f:'+str(formula_num).zfill(2)+'-'+ 'nw:'+str((size[0]+size[1])//2).zfill(3)+'-'+'ml:'+str(length_mean).zfill(2)+'-'+str(num)+'.trace'
							genSysliteTraces(trace_file, syslite_file)

	return generated_files


#Data type for parser
def tupleList(s):
	try:
		return tuple(map(int , s.split(',')))
	except:
		print("Wrong format; provide comma separated values")

def generateSmallBenchmarks(generated_files, max_size, sizes):
	
	for filename in generated_files:
		
		s = Sample(positive=[],negative=[])
		s.readFromFile(filename)
		
		for (i,j) in sizes:
			
			new_filename = filename.replace("nw:"+str((max_size[0]+max_size[1])//2).zfill(3), "nw:"+str(i).zfill(3))
			new_positive = s.positive[:i]
			new_negative = s.negative[:j]
			new_s = Sample(positive=new_positive, negative=new_negative, alphabet=s.alphabet)
			new_s.writeToFile(new_filename)
			new_sysfilename = new_filename.replace('TracesFiles', 'SysliteFiles')
			genSysliteTraces(new_filename, new_sysfilename)


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--formula_file', dest='formula_file', default = 'formulas.txt')
	parser.add_argument('--trace_type', dest='trace_type', default = 'trace')
	parser.add_argument('--operators', dest='operators', default = ['F', 'G', 'X', '!', '&', '|'], type=list)
	parser.add_argument('--size', dest='sample_sizes', default=[(10,10),(50,50),(100,100),(200,200),(500,500)], nargs='+', type=tupleList)
	parser.add_argument('--lengths', dest='trace_lengths', default=[(6,6)], nargs='+', type=tupleList)
	parser.add_argument('--total_num', dest='total_num', default=1, type=int)
	parser.add_argument('--output_folder', dest='output_folder', default = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	parser.add_argument('--syslite', dest='syslite', action='store_true', default=True)
	parser.add_argument('--generation_method', dest='gen_method', default='dfa_method')

	args,unknown = parser.parse_known_args()
	formula_file = args.formula_file
	trace_type = args.trace_type
	sample_sizes = list(args.sample_sizes)
	trace_lengths = list(args.trace_lengths)
	output_folder = args.output_folder
	syslite = bool(args.syslite)
	operators = list(args.operators)
	total_num = int(args.total_num)
	gen_method = args.gen_method

	#For generating a fresh set of benchmarks
	if os.path.exists(output_folder):
		shutil.rmtree(output_folder)

	os.makedirs(output_folder)
	shutil.copyfile(formula_file, output_folder+'/'+formula_file)
	sample_sizes.sort()
	max_size = sample_sizes[-1]
	generated_files = generateBenchmarks(formula_file, trace_type, [max_size], trace_lengths, operators, total_num, output_folder, syslite, gen_method)
	#generating small benchmarks from large ones
	generateSmallBenchmarks(generated_files, max_size, sample_sizes[:-1])

if __name__=='__main__':
	main()