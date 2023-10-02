import time
import heapq as hq
import logging
import csv
from Scarlet.booleanSubsetCover import BooleanSetCover
from Scarlet.directed_ltl import Dltl, findDltl, dltl2Formula
from Scarlet.formulaTree import Formula
from Scarlet.sample import Sample
logging_levels = {0:logging.WARNING, 1:logging.INFO, 2:logging.DEBUG}



def iteration_seq(max_len, max_width):
	'''
		determines the order of exploration for (length, width)
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



def inferLTL(sample, csvname, operators=['F', 'G', 'X', '!', '&', '|'], method='SC', verbosity = 0, is_word=False, last=False, thres=0, return_dict={}):
	'''
		main function inferring separating LTL formula
	'''
	logging.basicConfig(format='%(message)s', level=logging_levels[verbosity])
	time_counter = time.time()

	f=open(csvname,'w')

	writer = csv.writer(f)
	writer.writerow(["Time Elapsed", "Formula Size", "Formula", "is Terminated?"])
	f.close()

	reasonable_upper_bound = 30 # Change the reasonable upper bound to find formulas larger than this

	s = findDltl(sample, operators, last, thres, reasonable_upper_bound)
	
	global alphabet
	alphabet=sample.alphabet
	logging.info("Alphabet: %s"%alphabet)

	if last:
		alphabet.append('L')

	

	max_len = s.max_positive_length
	if sample.is_words or is_word:
		if last:
			max_width = 2 #we want partial symbols like (p & L) which is of width 2
		else:
			max_width = 1
	else:
		if last:
			max_width = len(sample.positive[0].vector[0])+1
		else:
			max_width = len(sample.positive[0].vector[0])

	
	seq = iteration_seq(max_len, max_width)
	positive_set = {i for i in range(len(sample.positive))}
	negative_set = {len(positive_set)+i for i in range(len(sample.negative))}
	full_set = (positive_set, negative_set)
	full_cover = len(positive_set)+len(negative_set)

	
	if method == "SC": #subset cover method
		boolcomb = BooleanSetCover(sample, operators, thres)
	
	covering_formula = None
	combination_time = 0
	
	for (length, width) in seq:
		logging.info("-------------Finding from length %d and width %d dltls-------------"%(length,width))
		time1 = time.time()

		
		if width>s.upper_bound:
			break

		if 3*length + 2*width -4 >= s.upper_bound: # if size of smallest dltl for (l,w)> upper_bound, we ignore it.
			continue							   		

		s.preComputeInd_next(width)
		s.enumerate(length, width)

		boolcomb.new_heap=[]
		
		if s.cover_set[(length,width)]=={}:
			continue
		
		if s.dltl_found:
			covering_dltl = list(s.cover_set[(length,width)].keys())[0]
			current_covering_formula = dltl2Formula(covering_dltl.vector, covering_dltl.inv, alphabet)
		else:
			for dltl in s.cover_set[(length,width)].keys():

				pos_friend_set = s.cover_set[(length,width)][dltl][0]
				neg_friend_set = s.cover_set[(length,width)][dltl][1]

				if neg_friend_set == negative_set:
					continue

				formula = dltl2Formula(dltl.vector, dltl.inv, alphabet)
				formula.size = dltl.size

				if method == "SC":

					boolcomb.formula_dict[formula] = (pos_friend_set, neg_friend_set)
					boolcomb.score[formula] = ((len(pos_friend_set) - len(neg_friend_set) + len(negative_set))/((formula.treeSize())**(0.5)+1))
					boolcomb.cover_size[formula]  = len(pos_friend_set) - len(neg_friend_set) + len(negative_set)
					

					hq.heappush(boolcomb.heap, (-boolcomb.score[formula], formula))
					hq.heappush(boolcomb.new_heap, (-boolcomb.score[formula], formula))
						

				
		
			t0=time.time()
			current_covering_formula, s.upper_bound = boolcomb.find(s.upper_bound)
			t1=time.time()
			combination_time+=t1-t0

		if (not current_covering_formula is None) and covering_formula != current_covering_formula:
			covering_formula = current_covering_formula
			logging.info("Already found: %s"%covering_formula)
			logging.debug("Current formula upper bound %d"%s.upper_bound)
			
			if (not csvname is None):
				time_elapsed = round(time.time() - time_counter,3)
				with open(csvname, 'a+') as csvfile:
					writer = csv.writer(csvfile)
					writer.writerow([time_elapsed, covering_formula.getNumberOfSubformulas(), covering_formula.prettyPrint()])
			
		logging.debug('########Time taken for iteration %.3f########'%(time.time()-time1))

	logging.debug("Boolean Combination Time %.3f"%combination_time)
		
	if covering_formula is None:
		logging.warning("No formula found")
		return covering_formula
	else:
		time_elapsed = time.time() - time_counter
		if (not csvname is None):
			time_elapsed = round(time.time() - time_counter,3)
			with open(csvname, 'a+') as csvfile:
				writer = csv.writer(csvfile)
				writer.writerow([time_elapsed, covering_formula.getNumberOfSubformulas(), covering_formula.prettyPrint(), 1])
		logging.warning("Final formula found %s"%covering_formula.prettyPrint())
		logging.warning("Time taken is: "+ str(round(time_elapsed,3))+ " secs") 


	ver = sample.isFormulaConsistent(covering_formula) #verifies if the returned formula is consistent with the sample in case of perfect classification
	
	if thres==0:
		if not ver:
			logging.error("Inferred formula is inconsistent, please report to the authors")
			return
		else:
			logging.debug("Inferred formula is correct")

	return_dict['covering_formula'] = covering_formula
	return_dict['time'] = time_elapsed

	return covering_formula
