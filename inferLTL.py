from booleanSetCover import BooleanSetCover

from formulaTree import Formula
from sample import Sample
import time
import heapq as hq
import logging
import csv
from decisionTree import DTlearner, DecisionTree
'''
Possible clean-ups:
- upperbound can be class variable in iSubTrace 
- 

'''

#BY DEFAULT p,q,r... alphabet
def iSubseq2Formula(iSubseq_tuple: tuple, inv: bool):

	# add formula calculation in isubTrace2FaXttern
	#print(iSubseq)
	if inv:
		
		first_atom = iSubseq_tuple[1]#('>0',('+0','-1'), ...)
		if first_atom[0][0] == '-':
			form_atom = Formula(alphabet[int(first_atom[0][1:])])
		else:
			form_atom = Formula(['!', Formula(alphabet[int(first_atom[0][1:])])])

		for i in first_atom[1:]:
			if i[0] == '-':
				form_atom = Formula(['|', form_atom, Formula(alphabet[int(i[1:])])])
			else:
				form_atom = Formula(['|', form_atom, Formula(['!', Formula(alphabet[int(i[1:])])])])
		
		if len(iSubseq_tuple)>2:	
			next_formula = Formula(['|', form_atom, iSubseq2Formula(iSubseq_tuple[2:], inv)])
		else:
			next_formula = form_atom
		
		first_digit = int(iSubseq_tuple[0].strip('>'))
		if iSubseq_tuple[0][0]=='>':
			next_formula = Formula(['G', next_formula])

		for i in range(first_digit):
			#next_formula = Formula(['|', Formula(['X', next_formula]), Formula('L')])
			next_formula = Formula(['X', next_formula])

	else:

		first_digit = int(iSubseq_tuple[0].strip('>'))
		first_atom = iSubseq_tuple[1]#('>0',('+0','-1'), ...)
		if first_atom[0][0] == '+': 
			form_atom = Formula(alphabet[int(first_atom[0][1:])])
		else:
			form_atom = Formula(['!', Formula(alphabet[int(first_atom[0][1:])])])

		for i in first_atom[1:]:
			if i[0] == '+':
				form_atom = Formula(['&', form_atom, Formula(alphabet[int(i[1:])])])
			else:
				form_atom = Formula(['&', form_atom, Formula(['!', Formula(alphabet[int(i[1:])])])])
		
		if len(iSubseq_tuple)>2:
			next_formula = Formula(['&', form_atom, iSubseq2Formula(iSubseq_tuple[2:], inv)])
		else:
			next_formula = form_atom
		for i in range(first_digit):
			next_formula = Formula(['X', next_formula])
		if iSubseq_tuple[0][0]=='>':
			next_formula = Formula(['F', next_formula])

	return next_formula

from isubsequences import iSubsequence, findiSubsequence

def iteration_seq(max_len, max_width):
	'''
	returns a list of pairs (l,w) specifying the order in which we try
	patterns of length l and width w

	Example:
	TO DO
	'''
	seq=[]
	min_val = max_len+max_width
	curr_sum=2
	while curr_sum<=min_val:
		for j in range(1,curr_sum):
			if curr_sum-j<= max_len and j<=max_width:
				seq.append((curr_sum-j,j))
		curr_sum=curr_sum+1
	return seq
# (0, atom, 1, atom, 1, atom), length-1+length-1+(width+width-1)*length  


#csvname is only temporary:
def inferLTL(sample, csvname, operators=['F', 'G', 'X', '!', '&', '|'], method='SC', is_word=False, last=False):
	time_counter = time.time()
	# while():
	# 	alphabet += best5formulas from the heap
	# alphabet = [a,b,c]
	# alphabet = [phi1,phi2,a,b,c]

	f=open(csvname,'w')
	f.close()
	# set of methods for indexed subsequences
	s = findiSubsequence(sample, operators, last)
	
	global alphabet
	alphabet=sample.alphabet

	if last:
		alphabet.append('L')

	reasonable_upper_bound = 30


	s.upper_bound = reasonable_upper_bound

	# set of methods for Boolean set cover
	max_len = s.max_positive_length
	if sample.is_words or is_word:
		if last:
			# not quite because we don't want p and q
			max_width = 2
		else:
			max_width = 1
	else:
		if last:
			max_width = len(sample.positive[0].vector[0])+1
		else:
			max_width = len(sample.positive[0].vector[0])

	# sequence of pairs (l,w) representing lengths and widths
	seq = iteration_seq(max_len, max_width)
	positive_set = {i for i in range(len(sample.positive))}
	negative_set = {len(positive_set)+i for i in range(len(sample.negative))}
	full_set = (positive_set, negative_set)
	full_cover = len(positive_set)+len(negative_set)

	if method == "DT":
		boolcomb = DTlearner(sample, operators)
	if method == "SC":
		boolcomb = BooleanSetCover(sample, operators)
	
	covering_formula = None
	combination_time = 0
	
	for (length, width) in seq:
		logging.info("-------------Finding from length %d and width %d iSubseqs-------------"%(length,width))
		time1 = time.time()
		
		if width>s.upper_bound:
			break

		if 3*length + 2*width -4 >= s.upper_bound: # (0, atom, 1, atom, 1, atom), length-1+length-1+(width+width-1)*length
			continue							# length -2 + 2*width*length			

		# phi = 
		# boolean combinations of
		# indexed subsequences

		# adding new letter would capture this:
		# F (G p and G q)

		# Open question: 
		# LTL over finite traces minus Until = 
		# LTL(F, X, AND, OR, Last) cup LTL(G, X, AND, OR, Last) 

		# letter = (X^10 (a and F b) AND sub2)
		# letter2 = X^10 (a and F b) OR sub3

		s.preComputeInd_next(width)
		s.coverSet(length, width)

		if s.cover_set[(length,width)]=={}:
			continue
		
		if s.Subseq_found:
			covering_iSubseq = list(s.cover_set[(length,width)].keys())[0]
			current_covering_formula = iSubseq2Formula(covering_iSubseq.vector, covering_iSubseq.inv)
		else:

			for iSubseq in s.cover_set[(length,width)].keys():

				pos_friend_set = s.cover_set[(length,width)][iSubseq][0]
				neg_friend_set = s.cover_set[(length,width)][iSubseq][1]

				if neg_friend_set == negative_set:
					continue

				formula = iSubseq2Formula(iSubseq.vector, iSubseq.inv)
				#Is the formula equivalent to some existing formula? if yes, ignore it.
				
				formula.size = iSubseq.size
				
				if method == "SC":

					boolcomb.formula_dict[formula] = (pos_friend_set, neg_friend_set)
					#score can be weighted by formula size
					boolcomb.score[formula] = ((len(pos_friend_set) - len(neg_friend_set) + len(negative_set))/((formula.treeSize())**(0.5)+1))
					#print(iSubseq, formula, len(pos_friend_set),len(neg_friend_set),len(negative_set), setcover.score[formula] )
					boolcomb.cover_size[formula]  = len(pos_friend_set) - len(neg_friend_set) + len(negative_set)
					
					hq.heappush(boolcomb.heap, (-boolcomb.score[formula], formula))
						

				if method =="DT":
					boolcomb.formula_dict[formula] = (pos_friend_set, neg_friend_set)


		
			t0=time.time()
			current_covering_formula, s.upper_bound = boolcomb.find(s.upper_bound)
			t1=time.time()
			combination_time+=t1-t0

		if current_covering_formula != None and covering_formula != current_covering_formula:
			#s.upper_bound = covering_formula.treeSize()
			covering_formula = current_covering_formula
			logging.info("Already found: %s"%covering_formula)
			logging.debug("Current formula upper bound %d"%s.upper_bound)
			
			if csvname != None:
				time_elapsed = round(time.time() - time_counter,3)
				with open(csvname, 'a+') as csvfile:
					writer = csv.writer(csvfile)
					writer.writerow([time_elapsed, covering_formula.size, covering_formula.prettyPrint()])
			
		logging.debug('########Time taken for iteration %.3f########'%(time.time()-time1))

	logging.debug("Boolean Combination Time %.3f"%combination_time)
		
	if covering_formula == None:
		logging.warning("No formula found")
		return covering_formula
	else:
		time_elapsed = time.time() - time_counter
		if csvname != None:
			time_elapsed = round(time.time() - time_counter,3)
			with open(csvname, 'a+') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow([time_elapsed, covering_formula.size, covering_formula.getNumberOfSubformulas(), covering_formula.prettyPrint(), 1])
		logging.warning("Final formula found %s"%covering_formula.prettyPrint())
		logging.warning("Time taken is: "+ str(round(time_elapsed,3))+ " secs") 
		#return covering_formula

	if isinstance(covering_formula, DecisionTree):
		ver = sample.isFormulaConsistent(covering_formula.convert2LTL())
	else:
		ver = sample.isFormulaConsistent(covering_formula)

	if not ver:
		logging.error("Inferred formula is inconsistent, please report to the authors")
		return
	else:
		logging.debug("Inferred formula is correct")

	return covering_formula
