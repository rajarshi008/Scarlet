from inferLTL import inferLTL
from sample import Sample
import argparse
import logging
import time


logging_levels = {0:logging.WARNING, 1:logging.INFO, 2:logging.DEBUG}

def run_test():

	parser = argparse.ArgumentParser()

	parser.add_argument('--input_file', '-i', dest='input_file', default = './dummy.trace')
	parser.add_argument('--timeout', '-t', dest='sample_sizes', default=[5], nargs='+', type=int)
	parser.add_argument('--verbose', '-v', dest='verbose', default=False, action='count')


	args,unknown = parser.parse_known_args()

	input_file = args.input_file
	file_type = 'word' if '.words' in input_file else 'trace'
	verbosity = int(args.verbose)
	logging.basicConfig(format='%(message)s', level=logging_levels[verbosity])

	
	sample = Sample()
	sample.readFromFile(input_file)
	operators = sample.operators


	if operators==[]:
		operators = ['F', 'G', 'X', '&', '|', '!']
		logging.info('Default operators used: %s'%''.join(operators))	
					

	time1= time.time()
	formula = inferLTL(sample, operators)
	time1 = time.time()-time1
	
	if formula == None:
		logging.info('No formula found') 
	else:
		logging.info('Formula found %s'%formula.prettyPrint())	

	logging.info("The time taken is: "+ str(round(time1,3))+ " secs") 

	if verbosity>1:
		ver = sample.isFormulaConsistent(formula)
		if not ver:
			logging.error("Inferred formula that is inconsistent, please report to the authors")
			return
		else:
			logging.debug("Inferred formula is correct")

	
	

	




run_test()