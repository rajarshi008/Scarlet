
import argparse
import os, shutil
import datetime
from Scarlet.sample import Sample, Trace, convertFileType
from Scarlet.formulaTree import Formula


class SampleGenerator:
	'''
	sample generator class
	'''
	def __init__(self,
				formula_file = 'Scarlet/formulas.txt',
				trace_type = 'trace',
				sample_sizes = [(10,10),(50,50)],
				trace_lengths = [(6,6)],
				output_folder = 'Scarlet/' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
				total_num = 1,
				gen_method = 'dfa_method'):

		self.formula_file = formula_file
		self.trace_type = trace_type
		self.sample_sizes = sample_sizes
		self.trace_lengths = trace_lengths
		self.output_folder = output_folder
		self.total_num = total_num
		self.gen_method = gen_method
		self.operators = ['F', 'G', 'X', '!', '&', '|']

		if os.path.exists(self.output_folder):
			shutil.rmtree(self.output_folder)

		os.makedirs(output_folder)
		formula_file_name = self.formula_file.split('/')[-1]

		shutil.copyfile(self.formula_file, output_folder+'/'+formula_file_name)
		self.sample_sizes.sort()
		self.max_size = sample_sizes[-1]
		

	def generateFromLargeSample(self):
		
		generated_files = self.generate(gen_from_large_sample=True)
		#generating small benchmarks from large ones
		self.generateSmallBenchmarks(generated_files, self.sample_sizes[:-1])



	def generate(self, gen_from_large_sample=False):

		if gen_from_large_sample:
			sample_sizes = [self.max_size]
		else:	
			sample_sizes = self.sample_sizes

		traces_folder = self.output_folder+'/TracesFiles/' 
		os.makedirs(traces_folder)

		#if trace_type == 'words':
		#	words_folder = output_folder+'/TracesFiles/'
		#	os.makedirs(words_folder)

		generated_files = []
		with open(self.formula_file, 'r') as file:
			formula_num=0
			for line in file:
				
				formula_text, alphabet = line.split(';')
				alphabet = alphabet.split(',')
				alphabet[-1] = alphabet[-1].rstrip('\n')
				
				#trace_lengths = lengths.split(',')
				#trace_lengths = [(int(i),int(i)) for i in trace_lengths]

				formula = Formula.convertTextToFormula(formula_text)
		
				formula_num+=1
				print('---------------Generating Benchmarks for formula %s---------------'%formula.prettyPrint())
				
				for size in sample_sizes:
					for length_range in self.trace_lengths:
						for num in range(self.total_num):
							length_mean = (length_range[0]+length_range[1])//2
							sample=Sample(positive=[], negative=[])

							trace_file = traces_folder+'f:'+str(formula_num).zfill(2)+'-'+'nw:'+str((size[0]+size[1])//2).zfill(3)+'-'+'ml:'+str(length_mean).zfill(2)+'-'+str(num)+'.trace'
							generated_files.append(trace_file)

							if self.gen_method=='dfa_method':
								sample.generator_dfa_in_batch_advanced(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, 
																		filename=trace_file, is_words=(self.trace_type=='words'), operators=self.operators)
							# sample.generator(formula=formula, length_range=length_range, num_traces=size, filename=word_file, is_word=(trace_type=='words'))
							elif self.gen_method=='random':
								sample.generator(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, 
													filename=trace_file, is_words=(self.trace_type=='words'), operators=self.operators)
							elif self.gen_method=='random_walk':
								sample.generator_random_walk(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, 
																filename=trace_file, is_words=(self.trace_type=='words'), operators=self.operators)


							#convertFileType(wordfile=word_file, tracefile=trace_file, operators=operators)
						# else:

						# 	if gen_method=='dfa_method':
						# 		sample.generator_dfa_in_batch_advanced(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)
						# 	elif gen_method=='random':
						# 		sample.generator(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)
						# 	elif gen_method=='random_walk':
						# 		sample.generator_random_walk(formula=formula, length_range=length_range, num_traces=size, alphabet=alphabet, filename=trace_file, is_words=(trace_type=='words'), operators=operators)
							

						# sample.generator(formula=formula, length_range=length_range, num_traces=size, filename=trace_file, is_words=(trace_type=='words'), operators=operators)


							assert sample.isFormulaConsistent(formula)

		return generated_files


	def generateSmallBenchmarks(self, generated_files, sizes):
		
		for filename in generated_files:
			
			s = Sample(positive=[],negative=[])
			s.readFromFile(filename)
			
			for (i,j) in sizes:
				
				new_filename = filename.replace("nw:"+str((self.max_size[0]+self.max_size[1])//2).zfill(3), "nw:"+str(i).zfill(3))
				new_positive = s.positive[:i]
				new_negative = s.negative[:j]
				new_s = Sample(positive=new_positive, negative=new_negative, alphabet=s.alphabet)
				new_s.writeToFile(new_filename)



#Data type for parser
def tupleList(s):
	try:
		return tuple(map(int , s.split(',')))
	except:
		print("Wrong format; provide comma separated values")



def main():

	parser = argparse.ArgumentParser()
	parser.add_argument('--formula_file', '-f', dest='formula_file', default = 'formulas.txt')
	parser.add_argument('--size', '-s', dest='sample_sizes', default=[(10,10),(50,50),(100,100),(200,200),(500,500)], nargs='+', type=tupleList)
	parser.add_argument('--lengths', '-l', dest='trace_lengths', default=[(6,6)], nargs='+', type=tupleList)
	parser.add_argument('--total_num', '-n', dest='total_num', default=1, type=int)
	parser.add_argument('--output_folder', '-o', dest='output_folder', default = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
	parser.add_argument('--generation_method', '-g', dest='gen_method', default='dfa_method')

	args,unknown = parser.parse_known_args()
	formula_file = 'Scarlet/'+ args.formula_file
	trace_type = 'trace'
	sample_sizes = list(args.sample_sizes)
	trace_lengths = list(args.trace_lengths)
	output_folder = 'Scarlet/' + args.output_folder
	total_num = int(args.total_num)
	gen_method = args.gen_method
	operators = ['F', 'G', 'X', '!', '&', '|']


	generator = SampleGenerator(formula_file=formula_file,
				trace_type=trace_type,
				sample_sizes=sample_sizes,
				trace_lengths=trace_lengths,
				output_folder=output_folder,
				total_num=total_num,
				gen_method=gen_method)

	generator.generateFromLargeSample()

if __name__=='__main__':
	main()