from sample import Sample, Trace, convertFileType
from formulaTree import Formula
import argparse
import os, shutil, glob
import datetime

def lineToTrace(line):
	lasso_start = None
	try:
		traceData, lasso_start = line.split('::')
	except:
		traceData = line
	trace_vector = [tuple([int(varValue) for varValue in varsInTimestep.split(',')]) for varsInTimestep in
				   traceData.split(';')]

	return (trace_vector, lasso_start)

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

	output_dir = '/'.join(output_file.split('/')[:-1])

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
		

	syslite_file = output_file
	f = open(syslite_file, "w")
	f.writelines(allLines)


def genTraces(input_file, output_file):
	
	allTraces = Sample(positive=[], negative=[], is_words=False)


	with open(input_file, 'r') as file:
		mode = 0
		count=0
		while True:
			count
			line=file.readline()
			if line=='':
				break

			if line == '---\n':
				mode+=1
				continue

			if mode==0:
				allTraces.alphabet = list(line.split(','))

			if mode==1:	
				# can read from both word file type and trace file type
				
				trace_vector, lasso_start = lineToTrace(line)
				trace = Trace(vector=trace_vector, lasso_start=lasso_start, is_word=False)	 	
				allTraces.positive.append(trace)

			if mode==1:
				
				trace_vector, lasso_start = lineToTrace(line)
				trace = Trace(vector=trace_vector, lasso_start=lasso_start, is_word=False)	 	
				allTraces.negative.append(trace)
	


	output_dir = '/'.join(output_file.split('/')[:-1])

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	

	allTraces.operators = ['F','G','X','!','&','|']			
	allTraces.writeToFile(output_file)
				



'''
#converting flie files to syslite
path = 'all_benchmarks/syslite_benchmarks'
trace_files = glob.glob(path + "/**/*.trace", recursive = True)

for input_file in trace_files:
	output_file = input_file.replace('TracesFiles','SysliteFiles')
	genSysliteTraces(input_file, output_file)
'''

#converting syslite files flie


path = 'syslite_benchmarks'
trace_files = glob.glob(path + "/**/*.trace", recursive = True)

print(trace_files)

for input_file in trace_files:
	
	output_file = input_file.replace('SysliteFiles', 'TracesFiles')
	if os.path.isfile(input_file):
		#print(input_file)
		#os.rename(input_file, input_file+'.trace')

		genTraces(input_file, output_file)
