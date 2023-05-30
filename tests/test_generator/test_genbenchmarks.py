import pytest
from Scarlet.genBenchmarks import SampleGenerator
from Scarlet.sample import Sample, Trace
import glob
import random
import os

num_tests = 10

@pytest.mark.parametrize("test_num", [i for i in range(num_tests)])
def test_genbenchmarks(test_num):
    '''
    Testing genbenchmarks by checking consistency with the formula
    '''
    sg = SampleGenerator(formula_file = 'Scarlet/tests/test_generator/formulas.txt',
                        trace_type = 'trace',
                        sample_sizes = [(10,10),(50,50)],
                        trace_lengths = [(6,6)],
                        output_folder = 'Scarlet/tests/test_generator/test_generations',
                        total_num = 1,
                        gen_method = 'dfa_method'
                        )

    num_sample = random.randint(10,20)
    trace_len = random.randint(5,10)
    sg.sample_sizes = [(num_sample,num_sample)]
    sg.trace_lengths = [(trace_len,trace_len)]

    sg.generate()

    folder_path = 'Scarlet/tests/test_generator/test_generations/TracesFiles'
    trace_files = [file for file in os.listdir(folder_path) if file.endswith(".trace")]

    # Iterate over the csv_files list and remove each file
    for file_name in trace_files:
        file_path = os.path.join(folder_path, file_name)  # Construct the full file path
        os.remove(file_path)  # Remove the file
        print("Removed file: {file_name}")