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
				is_word = False, 
				timeout = 900, 
				verbosity = 1,
				method = 'SC',
				thres = 0,
				last = False):
		
		self.is_word = is_word
		self.timeout = timeout
		self.verbosity = verbosity
		self.method = method
		self.thres = thres
		self.last = last

		logging.basicConfig(format='%(message)s', level=logging_levels[verbosity])


	def learn(self, tracefile, outputfile='results.csv'):
	
		self.input_file = tracefile
		self.csvname = outputfile

		self.sample = Sample(positive=[],negative=[])
		logging.info("Running on file %s"%self.input_file)

		self.sample.readFromFile(self.input_file)
		self.operators = self.sample.operators

		if self.operators==[]:
			self.operators = ['F', 'G', 'X', '&', '|', '!']
			logging.info('Default operators used: %s'%','.join(self.operators))	
		else:
			logging.info('Operators used: %s'%','.join(self.operators))

		manager = multiprocessing.Manager()
		return_dict = manager.dict()
		jobs = []
		
		p = multiprocessing.Process(target=inferLTL, args=(self.sample, self.csvname, self.operators, self.method, 
													self.is_word, self.last, self.thres, return_dict))
		
		jobs.append(p)
		p.start()

		p.join(self.timeout)
		if p.is_alive():
			print("Timeout reached, check your output in results folder")
			p.terminate()
			p.join()

		for proc in jobs:
			proc.join()
		
		return (return_dict.values())


def main():

	parser = argparse.ArgumentParser()

	parser.add_argument('--input_file', '-i', dest='input_file', default = './example.trace')
	parser.add_argument('--timeout', '-t', dest='timeout', default=900, type=int)
	parser.add_argument('--outputcsv', '-o', dest='csvname', default= './result.csv')
	parser.add_argument('--verbose', '-v', dest='verbose', default=3, action='count')
	parser.add_argument('--method', '-m', dest='method', default = 'SC')
	parser.add_argument('--words', '-w', dest= 'words', default = False, action='store_true')
	parser.add_argument('-thres', '-l', dest='thres', default=0)
	args,unknown = parser.parse_known_args()

	input_file = args.input_file
	is_word = True if ('.words' in input_file) or args.words  else False
	timeout = float(args.timeout)
	verbosity = int(args.verbose)-1
	method = args.method
	csvname = args.csvname
	thres = float(args.thres)
	last = False


	learner = LTLlearner(is_word=is_word, timeout=timeout, verbosity=verbosity,
												method=method, thres=thres,last=last)
	learner.learn(tracefile=input_file, outputfile=csvname)


if __name__ == "__main__":
    main()
