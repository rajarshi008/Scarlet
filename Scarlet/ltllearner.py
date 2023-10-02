'''
Takes user inputs, parse them and call the main inferltl function
'''
import argparse
import logging
import time
import multiprocessing
from Scarlet.inferLTL import inferLTL
from Scarlet.sample import Sample

logging_levels = {0:logging.WARNING, 1:logging.INFO, 2:logging.DEBUG}


class LTLlearner:
	'''
	learner class for running as a module
	'''
	def __init__(self,
				input_file = 'Scarlet/example.trace', 
				is_word = False, 
				timeout = 900, 
				verbosity = 2,
				method = 'SC',
				csvname = 'Scarlet/result.csv',
				thres = 0,
				last = False):

		self.input_file = input_file 
		self.is_word = False
		self.timeout = timeout
		self.verbosity = verbosity
		self.method = method
		self.csvname = csvname
		self.thres = thres
		self.last = last

		logging.basicConfig(format='%(message)s', level=logging_levels[verbosity])

		self.sample = Sample(positive=[],negative=[])
		logging.info("Running on file %s"%input_file)

		self.sample.readFromFile(input_file)
		self.operators = ['F', 'G', 'X', '&', '|', '!']
		logging.info('Operators used: %s'%','.join(self.operators))	
		logging.info("Logging level %s"%verbosity)
		

	def learn(self):
					
		manager = multiprocessing.Manager()
		return_dict = manager.dict()
		jobs = []
		
		p = multiprocessing.Process(target=inferLTL, args=(self.sample, self.csvname, self.operators, self.method, self.verbosity, 
													self.is_word, self.last, self.thres, return_dict))
		
		jobs.append(p)
		p.start()

		p.join(self.timeout)
		if p.is_alive():
			print("Timeout reached, check your output in result file")
			p.terminate()
			p.join()

		for proc in jobs:
			proc.join()
		
		return (return_dict.values())





def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--input_file', '-i', dest='input_file', default = 'example.trace')
	parser.add_argument('--timeout', '-t', dest='timeout', default=900, type=int)
	parser.add_argument('--outputcsv', '-o', dest='csvname', default= 'result.csv')
	parser.add_argument('--verbose', '-v', dest='verbose', default=1, action='count')
	parser.add_argument('-thres', '-l', dest='thres', default=0)
	args,unknown = parser.parse_known_args()

	input_file = 'Scarlet/'+ args.input_file
	is_word = False
	timeout = float(args.timeout)
	verbosity = int(args.verbose)-1
	method = 'SC'
	csvname = 'Scarlet/' + args.csvname
	thres = float(args.thres)
	last = False


	learner = LTLlearner(input_file=input_file, is_word=is_word, timeout=timeout, verbosity=verbosity,
												method=method, csvname=csvname, thres=thres,last=last)
	

	
	learner.learn()


if __name__ == "__main__":
    main()
