from booleanSetCover import BooleanSetCover
from isubTraces import iSubTrace
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
def isubTrace2Formula(isubtrace: tuple):

	# add formula calculation in isubTrace2FaXttern
	#print(isubtrace)

	if isubtrace[0]!='!':
		first_digit = int(isubtrace[0].strip('>'))
		first_atom = isubtrace[1]#('>0',('+0','-1'), ...)
		if first_atom[0][0] == '+': 
			form_atom = Formula(alphabet[int(first_atom[0][1:])])
		else:
			form_atom = Formula(['!', Formula(alphabet[int(first_atom[0][1:])])])

		for i in first_atom[1:]:
			if i[0] == '+':
				form_atom = Formula(['&', form_atom, Formula(alphabet[int(i[1:])])])
			else:
				form_atom = Formula(['&', form_atom, Formula(['!', Formula(alphabet[int(i[1:])])])])
		
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
			form_atom = Formula(alphabet[int(first_atom[0][1:])])
		else:
			form_atom = Formula(['!', Formula(alphabet[int(first_atom[0][1:])])])

		for i in first_atom[1:]:
			if i[0] == '-':
				form_atom = Formula(['|', form_atom, Formula(alphabet[int(i[1:])])])
			else:
				form_atom = Formula(['|', form_atom, Formula(['!', Formula(alphabet[int(i[1:])])])])
		
		if len(isubtrace)>3:
			next_formula = Formula(['|', form_atom, isubTrace2Formula(('!',)+isubtrace[3:])])
		else:
			next_formula = form_atom
		
		if isubtrace[1][0]=='>':
			next_formula = Formula(['G', next_formula])

		for i in range(first_digit):
			#next_formula = Formula(['|', Formula(['X', next_formula]), Formula('L')])
			next_formula = Formula(['X', next_formula])

	return next_formula

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
	print('InferLTL', csvname)
	# while():
	# 	alphabet += best5formulas from the heap
	# alphabet = [a,b,c]
	# alphabet = [phi1,phi2,a,b,c]

	f=open(csvname,'w')
	f.close()
	# set of methods for indexed subsequences
	s = iSubTrace(sample, operators,last)
	
	global alphabet
	alphabet=sample.alphabet

	if last:
		alphabet.append('L')
	
	if sample.is_words:
		absolute_upper_bound = (2*s.max_positive_length + s.max_positive_length - 1)*s.num_positives - 1
	else:
		absolute_upper_bound = (2*s.max_positive_length*len(alphabet) + s.max_positive_length - 1)*s.num_positives - 1

	reasonable_upper_bound = 50 # What should be this value?



	Gformula=Formula.convertTextToFormula('G(|(|(!(q),!(r)), G(p)))')

	upper_bound = min(absolute_upper_bound, reasonable_upper_bound)

	print("Absolute upper bound", absolute_upper_bound)
	print("Reasonable upper bound", reasonable_upper_bound)
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
		logging.info("-------------Finding from length %d and width %d isubtraces-------------"%(length,width))
		time1 = time.time()
		
		if width>upper_bound:
			break

		if 3*length + 2*width -4 >= upper_bound: # (0, atom, 1, atom, 1, atom), length-1+length-1+(width+width-1)*length
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

		cover_set = s.coverSet(length, width, upper_bound)
		if cover_set=={}:
			continue
		already_found = 0
		for isubtrace in cover_set.keys():

			pos_friend_set = cover_set[isubtrace][0]
			neg_friend_set = cover_set[isubtrace][1]

			if neg_friend_set == negative_set:
				continue

			formula = isubTrace2Formula(isubtrace)
			#Is the formula equivalent to some existing formula? if yes, ignore it.

			if isubtrace[0]!='!':
				formula.size = s.len_isubtrace[(isubtrace,False)]
			else:
				formula.size = s.len_isubtrace[(isubtrace[1:], True)]
			
			if method == "SC":

				boolcomb.formula_dict[formula] = (pos_friend_set, neg_friend_set)
				#score can be weighted by formula size
				boolcomb.score[formula] = ((len(pos_friend_set) - len(neg_friend_set) + len(negative_set))/((formula.treeSize())**(0.5)+1))
				#print(isubtrace, formula, len(pos_friend_set),len(neg_friend_set),len(negative_set), setcover.score[formula] )
				boolcomb.cover_size[formula]  = len(pos_friend_set) - len(neg_friend_set) + len(negative_set)
				

				if formula==Gformula:
					print(isubtrace)
					print(pos_friend_set, neg_friend_set)
					print(boolcomb.cover_size[formula])

				if boolcomb.cover_size[formula]==full_cover and formula.treeSize()<upper_bound:
					current_covering_formula, upper_bound = formula, formula.treeSize()
					already_found = 1
					break   
				else:
					hq.heappush(boolcomb.heap, (-boolcomb.score[formula], formula))
					


			if method =="DT":
				boolcomb.formula_dict[formula] = (pos_friend_set, neg_friend_set)			
		if not already_found:
			t0=time.time()
			current_covering_formula, upper_bound = boolcomb.find(upper_bound)
			t1=time.time()
			combination_time+=t1-t0

		if current_covering_formula != None and covering_formula != current_covering_formula:
			#upper_bound = covering_formula.treeSize()
			covering_formula = current_covering_formula
			logging.info("Already found: %s"%covering_formula)
			logging.debug("Current formula upper bound %d"%upper_bound)
			
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
