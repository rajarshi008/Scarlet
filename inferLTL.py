from booleanSetCover import BooleanSetCover
from isubTraces import iSubTrace
from formulaTree import Formula
from sample import Sample
import time
import heapq as hq
import logging
'''
Possible clean-ups:
- upperbound can be class variable in iSubTrace 
- 

'''


#BY DEFAULT p,q,r... alphabet
def isubTrace2Formula(isubtrace: tuple):

	# add formula calculation in isubTrace2FaXttern
	#print(isubtrace)

	if isubtrace[0]!='!':
		first_digit = int(isubtrace[0].strip('>'))
		first_atom = isubtrace[1]#('>0',('+0','-1'), ...)
		if first_atom[0][0] == '+': 
			form_atom = Formula(chr(ord('p')+int(first_atom[0][1:])))
		else:
			form_atom = Formula(['!', Formula(chr(ord('p')+int(first_atom[0][1:])))])

		for i in first_atom[1:]:
			if i[0] == '+':
				form_atom = Formula(['&', form_atom, Formula(chr(ord('p')+int(i[1:])))])
			else:
				form_atom = Formula(['&', form_atom, Formula(['!', Formula(chr(ord('p')+int(i[1:])))])])
		
		if len(isubtrace)>2:
			next_formula = Formula(['&', form_atom, isubTrace2Formula(isubtrace[2:])])
		else:
			next_formula = form_atom
		for i in range(first_digit):
			next_formula = Formula(['X', next_formula])
		if isubtrace[0][0]=='>':
			next_formula = Formula(['F', next_formula])
	
	else:
		first_digit = int(isubtrace[1].strip('>'))
		first_atom = isubtrace[2]#('>0',('+0','-1'), ...)
		if first_atom[0][0] == '-': 
			form_atom = Formula(chr(ord('p')+int(first_atom[0][1:])))
		else:
			form_atom = Formula(['!', Formula(chr(ord('p')+int(first_atom[0][1:])))])

		for i in first_atom[1:]:
			if i[0] == '-':
				form_atom = Formula(['|', form_atom, Formula(chr(ord('p')+int(i[1:])))])
			else:
				form_atom = Formula(['|', form_atom, Formula(['!', Formula(chr(ord('p')+int(i[1:])))])])
		
		if len(isubtrace)>3:
			next_formula = Formula(['|', form_atom, isubTrace2Formula(('!',)+isubtrace[3:])])
		else:
			next_formula = form_atom
		
		if isubtrace[1][0]=='>':
			next_formula = Formula(['G', next_formula])

		for i in range(first_digit):
			next_formula = Formula(['X', next_formula])
		
	return next_formula



def iteration_seq(max_len, max_width):

	seq=[]
	min_val = min(max_len, max_width)
	curr_sum=2
	while curr_sum<min_val*2:
		for j in range(1,curr_sum):
			if curr_sum-j<= max_len and j<=max_width:
				seq.append((curr_sum-j,j))

		curr_sum=curr_sum+1
	
	if max_len>min_val:
		seq+=[(i,min_val) for i in range(min_val, max_len+1)]
	else:
		seq+=[(min_val,i) for i in range(min_val, max_width+1)]

	return seq



def inferLTL(sample, operators):


	s = iSubTrace(sample, operators)

	upper_bound = 4*s.max_positive_length
	setcover = BooleanSetCover(sample, operators)
	max_len = s.max_positive_length
	max_width = len(sample.positive[0].vector[0])
	seq = iteration_seq(max_len, max_width)
	positive_set = {i for i in range(len(sample.positive))}
	negative_set = {i for i in range(len(sample.negative))}
	full_set = (positive_set, negative_set)
	current_covering_formula = None
	setcover_time = 0


	for (length, width) in seq:
		logging.info("-------------Finding from length %d and width %d isubtraces-------------"%(length,width))
		time1 = time.time()
		if width>upper_bound:
			break
		if 3*length + width -3 >= upper_bound:
			continue

		cover_set = s.coverSet(length, width, upper_bound)
		# if length==1:
		# 	print(cover_set[('>0', ('+0',))])
		if cover_set=={}:
			continue
		
		for isubtrace in cover_set.keys():

			pos_friend_set = cover_set[isubtrace][0]
			neg_friend_set = cover_set[isubtrace][1]


			if neg_friend_set == negative_set:
				continue

			formula = isubTrace2Formula(isubtrace)
			if isubtrace[0]!='!':
				formula.size = s.len_isubtrace[(isubtrace,False)]
			else:
				formula.size = s.len_isubtrace[(isubtrace[1:], True)]
			setcover.formula_dict[formula] = (pos_friend_set, neg_friend_set)
			#score can be weighted by formula size 

			setcover.score[formula] = (len(pos_friend_set) - len(neg_friend_set) + len(negative_set))/((formula.treeSize())**(0.5)+1)
			setcover.cover_size[formula]  = len(pos_friend_set) - len(neg_friend_set) + len(negative_set)
			hq.heappush(setcover.heap, (-setcover.score[formula], formula))

		t0=time.time()
		covering_formula, upper_bound = setcover.find(upper_bound)
		t1=time.time()
		setcover_time+=t1-t0


		if covering_formula != None:
			#upper_bound = covering_formula.treeSize()
			current_covering_formula = covering_formula
			logging.info("Already found: %s"%current_covering_formula)
			logging.debug("Current formula upper bound %d"%upper_bound)

		logging.debug('########Time taken for iteration %.3f########'%(time.time()-time1))


	if current_covering_formula == None:
		print("No formula found")
		return None

	logging.debug("Setcover Time %.3f"%setcover_time)
	return current_covering_formula
	





