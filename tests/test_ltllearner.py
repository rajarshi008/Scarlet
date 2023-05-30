import pytest
from Scarlet.ltllearner import LTLlearner
from Scarlet.sample import Sample, Trace
import heapq as hq
import logging
import glob
import os

 
file_paths = glob.glob('Scarlet/tests/test_benchmarks/*.trace')
threshold = [0,0.10]
params = [(f,t) for f in file_paths for t in threshold]

@pytest.mark.parametrize("filename, thres", params)
def test_boolean_set_cover(filename, thres):
    '''
    Testing LTLlearner by invoking the verifier to check consistency with the sample
    '''
    print(filename, thres)
    learner = LTLlearner(input_file=filename, timeout=100, thres=thres, csvname=filename.strip('.trace')+'.csv')

    formula = learner.learn()[0]

    folder_path = 'Scarlet/tests/test_benchmarks/'
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

    # Iterate over the csv_files list and remove each file
    for file_name in csv_files:
        file_path = os.path.join(folder_path, file_name)  # Construct the full file path
        os.remove(file_path)  # Remove the file
        print("Removed file: {file_name}")


    sample = Sample(positive=[], negative=[], alphabet=[])
    sample.readFromFile(filename)

    misclass = 0
    for w in sample.positive:
        if w.evaluateFormula(formula,sample.letter2pos) == False:
            misclass += 1

    for w in sample.negative:
        if w.evaluateFormula(formula,sample.letter2pos) == True:
            misclass += 1


    misclass_percent = misclass/(len(sample.positive)+len(sample.negative))  

    assert misclass_percent <= thres


