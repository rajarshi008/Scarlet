from Scarlet.directed_ltl import *
from Scarlet.inferLTL import dltl2Formula
from Scarlet.formulaTree import Formula
from Scarlet.sample import Sample, lineToTrace
import random
import pytest
import math
import re


def comb(n, m):
	'''
	n choose m
	'''
	n_factorial = 1
	for i in range(1, n + 1):
		n_factorial *= i

	m_factorial = 1
	for i in range(1, m + 1):
		m_factorial *= i

	n_minus_m_factorial = 1
	for i in range(1, n - m + 1):
		n_minus_m_factorial *= i

	result = n_factorial // (m_factorial * n_minus_m_factorial)
	return result


# Test variables
num_tests = 5
prop_types = [[], ['p'], ['p', 'q'], ['p', 'q', 'r'], ['p', 'q', 'r', 's']]
file_list = ['test%s.trace'%str(i) for i in range(1,8)]

params = [(i,prop_list) for prop_list in prop_types for i in range(num_tests)]
@pytest.mark.parametrize("test_num, prop_list", params)
def test_genPossibleAtoms(test_num, prop_list):
	
	#Checks if the generation of atoms from letters works correctly
	
	f = findDltl(sample = Sample(), operators=['F','G','X','&','|','!'], last=False, thres=0, upper_bound=30)
	rand_inv = random.choice([True, False])
	rand_letter = tuple(random.randint(0,1) for _ in range(len(prop_list)))
	print(rand_letter)
	assert f.genPossibleAtoms(letter=rand_letter, width=0, inv=rand_inv, is_end=False) == [] #there are no width 0 atoms 
	
	# testing via length check
	n = len(prop_list)
	for k in range(1,n+1):
		assert len(f.genPossibleAtoms(letter=rand_letter, width=k, inv=rand_inv,  is_end=False)) == sum(comb(n,i) for i in range(1,k+1))



@pytest.mark.parametrize("test_num, prop_list", params)
def test_extenddltl(test_num, prop_list):
	
	#Checks if the function extenddltl produces valid dltl formulas
	
	prop_nums = [str(i) for i in range(len(prop_list))]
	len_props = len(prop_nums)
	rand_inv = random.choice([True, False])
	d = Dltl(vector = tuple(), inv = rand_inv)
	d.size = -1
	f = findDltl(sample = Sample(), operators=['F','G','X','&','|','!'], last=False, thres=0, upper_bound=30)

	for i in range(5):
		rand_diff = random.randint(0,3)
		rand_letter = tuple(random.randint(0,1) for _ in range(len(prop_list)))
		rand_width = random.randint(1,len(prop_list)) if len(prop_list)>1 else 1
		rand_atoms = f.genPossibleAtoms(letter=rand_letter, width=rand_width, inv=False, is_end=False)
		try:
			d=random.choice(d.extenddltl(diff=rand_diff, atoms=rand_atoms, upper_bound=30))
			formula=dltl2Formula(dltl_tuple=d.vector, inv=False, alphabet=prop_list)
			if formula != None:
				print(d.vector, formula)	
				assert d.size == formula.treeSize()

			ch = d.vector[i]
			if i % 2 == 0:
			#check if temporal diff
				assert bool(re.match('^>?[0-9]+$',ch))
			else:
				#check if atom
				assert isinstance(ch, tuple)
				for lit in ch:
					assert bool(re.match('^[-+][%s]$'%(''.join(prop_nums)),lit))
		except:
			continue

	assert isinstance(d, Dltl)

@pytest.mark.parametrize("test_num, prop_list", params)
def test_add2dltl(test_num, prop_list):
	
	#Checks if the creation of new dltl works correctly
	
	f = findDltl(sample = Sample(), operators=['F','G','X','&','|','!'], last=False, thres=0, upper_bound=30)
	
	#base case
	rand_inv = random.choice([True, False])
	assert f.add2dltl(dltl1=Dltl(tuple(),rand_inv), dltl2=Dltl(tuple(),rand_inv)) == None


	if prop_list != []:

		rand_len = random.randint(1,5)
		dltl1_tuple = tuple()
		dltl2_tuple = tuple()
		for i in range(rand_len):
			rand_letter = tuple(random.randint(0,1) for _ in range(len(prop_list)))
			rand_atom1 = random.choice(f.genPossibleAtoms(letter=rand_letter, width=1, inv=False, is_end=False))

			rand_width = random.randint(1,len(prop_list)) if len(prop_list)>1 else 1
			rand_atom2 = random.choice(f.genPossibleAtoms(letter=rand_letter, width=rand_width, inv=False, is_end=False))

			rand_diff = random.choice(['>','']) + str(random.randint(0,3))
			dltl1_tuple += (rand_diff, rand_atom1)
			dltl2_tuple += (rand_diff, rand_atom2)

		dltl1 = Dltl(dltl1_tuple, rand_inv)
		dltl2 = Dltl(dltl2_tuple, rand_inv)
		dltl1.size = 0
		dltl2.size = 0

		print(dltl1_tuple, dltl2_tuple)
		formula = f.add2dltl(dltl1, dltl2) 

		# if dltl1 = dltl2 then the formula will be None
		assert not (dltl1_tuple == dltl2_tuple) or formula == None


@pytest.mark.parametrize("test_file", file_list)
def test_preComputeInd(test_file):
	
	#Checks if the computation of the ind_table works correctly
	
	sample = Sample(positive=[], negative=[], alphabet=[], is_words=False)
	sample.readFromFile('Scarlet/tests/test_learner/test_benchmarks/'+test_file)

	f = findDltl(sample=sample, operators=['F','G','X','&','|','!'], last=False, thres=0, upper_bound=30)
	
	if len(sample.alphabet) > 1:
		for i in range(2, len(sample.alphabet)-1):
			f.preComputeInd_next(width=i)
	print(len(f.ind_table))

	for word,pos,atom in f.ind_table:

		ind_list = f.ind_table[(word, pos, atom)]
		trace = lineToTrace(word)[0]
		
		for k in ind_list:
			is_end = k == (len(trace)-1)
			assert k>=pos
			#checking if the inductively computed ind_table is actually correct
			assert is_sat(trace[k], atom, is_end)


@pytest.mark.parametrize("test_file", file_list)
def test_R_table(test_file):
	'''
	Checks if the computation of the R_table works correctly
	'''
	sample = Sample(positive=[], negative=[], alphabet=[], is_words=False)
	sample.readFromFile('Scarlet/tests/test_learner/test_benchmarks/'+test_file)

	f = findDltl(sample=sample, operators=['F','G','X','&','|','!'], last=False, thres=0, upper_bound=20)


	seq = [(1,1),(1,2),(2,1),(2,2)] # sequence of length and widths
	# checking if R_table stores the dltls of correct length and width
	for length,width in seq:
		
		f.cover_set[(length,width)] = {}
		R_table = f.R(length,width)
		for d in R_table:
			assert len(d.vector) == 2*length
			atoms = d.vector[1::2]
			max_len_atom =  max(len(a) for a in atoms)
			assert max_len_atom == width


params = [(i,test_file) for test_file in file_list for i in range(num_tests)]
@pytest.mark.parametrize("test_num, test_file", params)
def test_dltlCoverSet(test_num, test_file):
	'''
	Checks if the computation of the cover set works correctly
	'''
	sample = Sample(positive=[], negative=[], alphabet=[], is_words=False)
	sample.readFromFile('Scarlet/tests/test_learner/test_benchmarks/'+test_file)

	f = findDltl(sample=sample, operators=['F','G','X','&','|','!'], last=False, thres=0, upper_bound=30)

	#generating a random dltl formula
	dltl_tuple = tuple()
	rand_len = random.randint(1,5)
	for i in range(rand_len):
		rand_letter = tuple(random.randint(0,1) for _ in range(len(sample.alphabet)))
		rand_width = random.randint(1,len(sample.alphabet)) if len(sample.alphabet)>1 else 1
		rand_atom = random.choice(f.genPossibleAtoms(letter=rand_letter, width=rand_width, inv=False, is_end=False))

		rand_diff = random.choice(['>','']) + str(random.randint(0,3))
		dltl_tuple += (rand_diff, rand_atom)

	f.cover_set[(rand_len,rand_width)] = {}
	pos_list = {}
	neg_list = {} 

	for i in range(f.num_positives):
		rand_size = random.randint(0,len(sample.positive[i])-1)
		pos_list[i] = random.sample([k for k in range(len(sample.positive[i]))], rand_size)

	for i in range(f.num_negatives):
		rand_size = random.randint(0,len(sample.negative[i])-1)
		neg_list[i] = random.sample([k for k in range(len(sample.negative[i]))], rand_size)
	
	dltl1 = Dltl(vector=dltl_tuple, inv=False)
	f.dltlCoverSet(dltl=dltl1, pos_list=pos_list, neg_list=neg_list, sl_length=rand_len, width=rand_width)

	pos_friend_set, neg_friend_set = f.cover_set[(rand_len,rand_width)][dltl1] 
	for i in pos_friend_set:
		assert pos_list[i] != []
	for i in neg_friend_set:
		assert neg_list[i-f.num_positives] != []

	dltl2 = Dltl(vector=dltl_tuple, inv=True)
	f.dltlCoverSet(dltl=dltl2, pos_list=pos_list, neg_list=neg_list, sl_length=rand_len, width=rand_width)

	pos_friend_set, neg_friend_set = f.cover_set[(rand_len,rand_width)][dltl2] 
	for i in pos_friend_set:
		assert pos_list[i] == []
	for i in neg_friend_set:
		assert neg_list[i-f.num_positives] == []

