from inferLTL import inferLTL
from sample import Sample
import argparse
import logging
import time
import multiprocessing


logging_levels = {0:logging.WARNING, 1:logging.INFO, 2:logging.DEBUG}

def run_test():

	parser = argparse.ArgumentParser()

	parser.add_argument('--input_file', '-i', dest='input_file', default = './dummy.trace')
	parser.add_argument('--timeout', '-t', dest='timeout', default=900, type=int)
	parser.add_argument('--outputcsv', '-o', dest='csvname', default='./result.csv')
	parser.add_argument('--verbose', '-v', dest='verbose', default=False, action='count')
	args,unknown = parser.parse_known_args()

	input_file = args.input_file
	is_word = True if '.words' in input_file else False
	timeout = float(args.timeout)
	verbosity = int(args.verbose)
	csvname = args.csvname
	logging.basicConfig(format='%(message)s', level=logging_levels[verbosity])

	sample = Sample()
	sample.readFromFile(input_file)
	operators = sample.operators

	if operators==[]:
		operators = ['F', 'G', 'X', '&', '|', '!']
		logging.info('Default operators used: %s'%','.join(operators))	
	else:
		logging.info('Operators used: %s'%','.join(operators))
					
	
	#Starting timeout
	p = multiprocessing.Process(target=inferLTL, args=(sample, csvname, operators))
	p.start()
	p.join(timeout)
	if p.is_alive():
		logging.debug("Timeout reached, check your output in results folder")
		p.terminate()
		p.join()	
	
run_test()