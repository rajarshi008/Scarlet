import pytest
from Scarlet.ltllearner import LTLlearner
from Scarlet.sample import Sample, Trace
import heapq as hq
import logging
import glob

 
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



    # Test the find() method with invalid upper_bound


#ver true in the test suite

#incr length

#incr width


'''
    bsc.cover_size == {Formula.convertTextToFormula('p'): 8, Formula.convertTextToFormula('F(p)'): 7, Formula.convertTextToFormula('q'): 5, \
                                    Formula.convertTextToFormula('F(q)'): 8, Formula.convertTextToFormula('!(q)'): 5, \
                                    Formula.convertTextToFormula('F(!(q))'): 5, Formula.convertTextToFormula('G(!(q))'): 2, \
                                    Formula.convertTextToFormula('G(p)'): 5, Formula.convertTextToFormula('G(q)'): 5, \
                                    Formula.convertTextToFormula('G(!(p))'): 3, Formula.convertTextToFormula('X(p)'): 6, \
                                    Formula.convertTextToFormula('F(X(p))'): 6, Formula.convertTextToFormula('X(!(q))'): 5, \
                                    Formula.convertTextToFormula('F(X(!(q)))'): 5, Formula.convertTextToFormula('X(q)'): 5, \
                                    Formula.convertTextToFormula('F(X(q))'): 7, Formula.convertTextToFormula('X(G(!(q)))'): 3, \
                                    Formula.convertTextToFormula('X(G(p))'): 5, Formula.convertTextToFormula('X(G(q))'): 5, \
                                    Formula.convertTextToFormula('X(X(!(p)))'): 5, Formula.convertTextToFormula('F(X(X(!(p))))'): 5, \
                                    Formula.convertTextToFormula('X(X(!(q)))'): 3, Formula.convertTextToFormula('F(X(X(!(q))))'): 3, \
                                    Formula.convertTextToFormula('X(X(p))'): 5, Formula.convertTextToFormula('F(X(X(p)))'): 5, \
                                    Formula.convertTextToFormula('X(X(q))'): 7, Formula.convertTextToFormula('F(X(X(q)))'): 7, \
                                    Formula.convertTextToFormula('X(G(!(p)))'): 4, Formula.convertTextToFormula('X(X(G(!(p))))'): 5, \
                                    Formula.convertTextToFormula('X(X(G(!(q))))'): 3, Formula.convertTextToFormula('X(X(G(p)))'): 5, \
                                    Formula.convertTextToFormula('X(X(G(q)))'): 7}
    
    assert bsc.heap == [( -4.0, Formula.convertTextToFormula('p')), ( -3.31, Formula.convertTextToFormula('F(q)')),\
                        ( -2.56, Formula.convertTextToFormula('X(X(q))')), ( -2.9, Formula.convertTextToFormula('F(p)')),\
                        ( -2.49, Formula.convertTextToFormula('X(p)')), ( -2.5, Formula.convertTextToFormula('q')), ( -2.07, Formula.convertTextToFormula('X(q)')),\
                        ( -2.56, Formula.convertTextToFormula('F(X(q))')), ( -2.07, Formula.convertTextToFormula('G(q)')),\
                        ( -1.67, Formula.convertTextToFormula('X(X(!p))')), ( -2.07, Formula.convertTextToFormula('!q')),\
                        ( -1.83, Formula.convertTextToFormula('X(X(p))')), ( -2.33, Formula.convertTextToFormula('F(X(X(q)))')),\
                        ( -1.55, Formula.convertTextToFormula('X(X(G(!p)))')), ( -1.67, Formula.convertTextToFormula('X(X(G(p)))')),\
                        ( -2.33, Formula.convertTextToFormula('X(X(G(q)))')), ( -1.0, Formula.convertTextToFormula('X(G(!q))')),\
                        ( -1.83, Formula.convertTextToFormula('X(G(p))')), ( -1.83, Formula.convertTextToFormula('X(G(q))')),\
                        ( -1.1, Formula.convertTextToFormula('G(!p)')), ( -1.55, Formula.convertTextToFormula('F(X(X(!p)))')), \
                        ( -1.0, Formula.convertTextToFormula('X(X(!q))')),( -0.93, Formula.convertTextToFormula('F(X(X(!q)))')),\
                        ( -1.83, Formula.convertTextToFormula('F(!q)')),( -1.67, Formula.convertTextToFormula('F(X(X(p)))')),\
                        ( -1.83, Formula.convertTextToFormula('X(!q)')),( -2.2, Formula.convertTextToFormula('F(X(p))')),\
                        ( -0.73, Formula.convertTextToFormula('G(!q)')),( -1.33, Formula.convertTextToFormula('X(G(!p))')),\
                        ( -0.93, Formula.convertTextToFormula('X(X(G(!q)))')),( -1.67, Formula.convertTextToFormula('F(X(!q))')),\
                        ( -2.07, Formula.convertTextToFormula('G(p)'))]
'''