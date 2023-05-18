import pytest
from Scarlet.inferLTL import dltl2Formula
from Scarlet.formulaTree import Formula
import random

def is_formula_valid(tree):

    label = tree.label 
    if label in ['F', 'G', 'X', '!']:#unary operators
        if tree.left == None or tree.right != None:
            return False
        else:
            return is_formula_valid(tree.left)

    elif label in ['&', '|']:#binary operators
        if tree.left == None or tree.right == None:
            return False
        else:
            return is_formula_valid(tree.left) and is_formula_valid(tree.right)
    
    else:#propositions
        return tree.left == None and tree.right == None

def random_dltl(length):

    dltl = tuple()
    for _ in range(length):    
        value = random.choice(['>',''])+str(random.randint(0,5))
        atom = sorted(random.sample([0,1,2],k=random.randint(1,3)))
        signed_atom = tuple([random.choice(['+','-'])+str(i) for i in atom])
        dltl += (value, signed_atom)

    return dltl

num_tests = 20
@pytest.mark.parametrize("test_num", [i for i in range(num_tests)])
def test_dltl2Formula(test_num):
    '''
    Testing dltl2formula by checking the formula 
    '''
    #random generation of dltl formula

    alphabet = ['p', 'q', 'r']
    dltl_len = random.randint(1,5)
    dltl_tuple = random_dltl(dltl_len)

    dltl_formula = dltl2Formula(dltl_tuple, False, alphabet)

    assert is_formula_valid(dltl_formula)

f = Formula.convertTextToFormula('X(X(X(&(&(!(p),q),r))))')
is_formula_valid(f)
