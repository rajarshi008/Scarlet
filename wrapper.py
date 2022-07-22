'''
runs the code in multiple threads in parallel
'''

import os, csv
import argparse
from run_tests import run_test
from rq import Queue, Worker, Connection
from redis import Redis
from random import seed
from random import random

'''
Run the following:
rq worker -b -q genGraphs &
'''

def run_in_queue(benchmark_folder, timeout, method):
	trace_file_list = []
	for root, dirs, files in os.walk(benchmark_folder):
		for file in files:
			if file.endswith('.trace'):
				trace_file_name = str(os.path.join(root, file))
				trace_file_list.append(trace_file_name)


	redis_conn = Redis()
	q = Queue('genGraphs', connection=redis_conn)
	q.empty()
	
	for trace_file in trace_file_list:
		outputcsv = trace_file+'-out.csv'
		q.enqueue(run_test, args=(trace_file, timeout, outputcsv, method), job_timeout=timeout+10)
	print('Length of queue', len(q))

#Compiling
def compile(benchmark_folder):
	trace_file_list = []
	for root, dirs, files in os.walk(benchmark_folder):
		for file in files:
			if file.endswith('.trace'):
				trace_file_name = str(os.path.join(root, file))
				trace_file_list.append(trace_file_name)
	with open('compiled.csv', 'w') as compiledcsv:
		header = ['File Name']
		writer = csv.writer(compiledcsv)
		all_rows = [header]

		for trace_file in trace_file_list:
			with open(trace_file+'-out.csv') as csvfile:
				rows = csv.reader(csvfile)
				data_row = []
				for row in rows:
					data_row += row
				new_row = [trace_file]+data_row
				all_rows.append(new_row)
		writer.writerows(all_rows)


def main():

	timeout = 200
	benchmark_folder = 'third-check/TracesFiles'
	method = 'DT'

	parser = argparse.ArgumentParser()
	parser.add_argument('--compile', dest='compile_results', action='store_true', default=False)
	args,unknown = parser.parse_known_args()

	compile_results = bool(args.compile_results)
	if not compile_results:
		run_in_queue(benchmark_folder, timeout, method)
	else:
		compile(benchmark_folder)

if __name__ == "__main__":
    main()






