import pytest
from Scarlet.ltllearner import LTLlearner
from Scarlet.sample import Sample, Trace
import heapq as hq
import logging
import glob
import os

 
file_list = ['test%s.trace'%str(i) for i in range(1,8)]
threshold = [0,0.10]
params = [(f,t) for f in file_list for t in threshold]

@pytest.mark.parametrize("test_file, thres", params)
def test_ltllearner(test_file, thres):
    '''
    Testing LTLlearner by invoking the verifier to check consistency with the sample
    '''
    
    folder_path = 'Scarlet/tests/test_learner/test_benchmarks/'
    learner = LTLlearner(input_file=folder_path+test_file, timeout=100, thres=thres, csvname=test_file.strip('.trace')+'.csv')

    formula = learner.learn()[0]
    
    csv_files = [file for file in os.listdir(folder_path) if file.endswith(".csv")]

    # Iterate over the csv_files list and remove each file
    for file_name in csv_files:
        file_path = os.path.join(folder_path, file_name)  # Construct the full file path
        os.remove(file_path)  # Remove the file
        print("Removed file: {file_name}")


    sample = Sample(positive=[], negative=[], alphabet=[])
    sample.readFromFile(folder_path + test_file)

    misclass = 0
    for w in sample.positive:
        if w.evaluateFormula(formula,sample.letter2pos) == False:
            misclass += 1

    for w in sample.negative:
        if w.evaluateFormula(formula,sample.letter2pos) == True:
            misclass += 1


    misclass_percent = misclass/(len(sample.positive)+len(sample.negative))  

    assert misclass_percent <= thres


