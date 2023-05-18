import pytest
from Scarlet.sample import Sample
from Scarlet.booleanSubsetCover import BooleanSetCover
from Scarlet.formulaTree import Formula
import heapq as hq
import random
import logging


num_tests = 10
@pytest.mark.parametrize("test_num", [i for i in range(num_tests)])
def test_boolean_set_cover(test_num):
    '''
    Testing boolean set cover using random formulas that have random cover set
    '''
    
    logging.debug("============== Checking BooleanSubsetCover on Test {test_num} ==============")

    sample = Sample()
    sample.readFromFile('Scarlet/example.trace')

    # Create a BooleanSetCover object
    bsc = BooleanSetCover(sample, ['&', '|'], 0.1)

    # Test the initialization of the object
    bsc.positive_set = {i for i in range(len(bsc.sample.positive))}           
    bsc.negative_set = {i for i in range(len(bsc.sample.negative))}           
    bsc.full_set = (bsc.positive_set, bsc.negative_set)
    bsc.max_cover_size = len(bsc.positive_set) + len(bsc.negative_set)

    bsc.score == {}
    
    random_formulas = [Formula.convertTextToFormula('p'), Formula.convertTextToFormula('F(p)'), Formula.convertTextToFormula('q'), \
                                    Formula.convertTextToFormula('F(q)'), Formula.convertTextToFormula('!(q)'), \
                                    Formula.convertTextToFormula('F(!(q))'), Formula.convertTextToFormula('G(!(q))'), \
                                    Formula.convertTextToFormula('G(p)'), Formula.convertTextToFormula('G(q)'), \
                                    Formula.convertTextToFormula('G(!(p))'), Formula.convertTextToFormula('X(p)'), \
                                    Formula.convertTextToFormula('F(X(p))'), Formula.convertTextToFormula('X(!(q))'), \
                                    Formula.convertTextToFormula('F(X(!(q)))'), Formula.convertTextToFormula('X(q)'), \
                                    Formula.convertTextToFormula('F(X(q))'), Formula.convertTextToFormula('X(G(!(q)))'), \
                                    Formula.convertTextToFormula('X(G(p))'), Formula.convertTextToFormula('X(G(q))'), \
                                    Formula.convertTextToFormula('X(X(!(p)))'), Formula.convertTextToFormula('F(X(X(!(p))))'), \
                                    Formula.convertTextToFormula('X(X(!(q)))'), Formula.convertTextToFormula('F(X(X(!(q))))'), \
                                    Formula.convertTextToFormula('X(X(p))'), Formula.convertTextToFormula('F(X(X(p)))'), \
                                    Formula.convertTextToFormula('X(X(q))'), Formula.convertTextToFormula('F(X(X(q)))'), \
                                    Formula.convertTextToFormula('X(G(!(p)))'), Formula.convertTextToFormula('X(X(G(!(p))))'), \
                                    Formula.convertTextToFormula('X(X(G(!(q))))'), Formula.convertTextToFormula('X(X(G(p)))'), \
                                    Formula.convertTextToFormula('X(X(G(q)))')]
    

    for formula in random_formulas:

        pos_friend_set = set(random.sample(bsc.positive_set,k=random.randint(1,len(bsc.positive_set))))
        neg_friend_set = set(random.sample(bsc.negative_set,k=random.randint(1,len(bsc.negative_set))))
        
        bsc.formula_dict[formula] = (pos_friend_set, neg_friend_set)
        bsc.score[formula] = ((len(pos_friend_set) - len(neg_friend_set) + len(bsc.negative_set))/((formula.treeSize())**(0.5)+1))
        bsc.cover_size[formula]  = len(pos_friend_set) - len(neg_friend_set) + len(bsc.negative_set)
                        
        hq.heappush(bsc.heap, (-bsc.score[formula], formula))
        hq.heappush(bsc.new_heap, (-bsc.score[formula], formula))


    # Testing the main find() method
    upper_bound = 10
    result = bsc.find(upper_bound)
    
    final_formula = result[0]
    final_upperbound = result[1]
    if final_formula is not None:
        assert final_formula.treeSize() <= upper_bound
        assert final_upperbound <= upper_bound
        assert (len(bsc.formula_dict[final_formula][0]) - len(bsc.formula_dict[final_formula][1]) \
                + len(bsc.negative_set)) >= bsc.max_cover_size*(1-bsc.thres)
    else:
        assert final_upperbound == upper_bound

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