import heapq as hq
from formulaTree import Formula
import time
import logging


"""
Formulas should contain:
- the formula itself as a tree (DAG?)
- size
- set of accepted positive words
- set of rejected negative words
- score (number of accepted positive words + number of rejected negative words)
"""

#{formula: (friend_set, victim_set)}
'''
OPTIMISATION:
Take postraces as argument instead of formulas



'''


#Calculate the Boolean set cover from the covering set 

class BooleanSetCover: 

	def __init__(self, sample, operators):

		self.sample = sample
		self.positive_set = {i for i in range(len(self.sample.positive))}
		self.negative_set = {i for i in range(len(self.sample.negative))}
		self.full_set = (self.positive_set, self.negative_set)
		self.max_cover_size = len(self.positive_set) + len(self.negative_set)
		self.score = {}
		self.cover_size = {}
		self.heap = []
		self.formula_dict = {}
		self.operators = operators

	
	#calculates the local score of a formula with respect to the best formula 
	def score_local(self, formula, best_formula):

		return (self.cover_size[formula]-self.cover_size[best_formula])/((formula.treeSize())**(0.5)+1)
	
	#we find best formulas from the current cover set
	def find(self, upper_bound):

		best_formula_list=[]

		#get the best 5 formulas currently from the heap with the highest score
		smallest_list = hq.nsmallest(5,self.heap)
		for i in smallest_list:
			best_formula_list.append((i[1],self.cover_size[i[1]]))
		
		#sort the best formulas with their cover size
		best_formula_list = list(map(lambda x:x[0], sorted(best_formula_list, key=lambda x: x[1], reverse=True)))

		logging.debug("List of best formulas: %s"%str([(i,self.score[i]) for i in best_formula_list]))	
		
		final_formula=None
		

		for best_formula in best_formula_list:

			current_formula = best_formula
			current_value = self.cover_size[current_formula]/current_formula.treeSize()
			t0=time.time()

			success = True

			#if the current formula size is greater than the upper-bound, we ignore them
			if current_formula.treeSize() >= upper_bound:
				continue

			# We continue until we find a formula that covers the whole set
			while self.cover_size[current_formula] < self.max_cover_size:
				
				# we take "&" and "|" of all existing formulas in the heap with the best formula and check if it is better
				value={}
				for (_,formula) in self.heap[1:]:

# P = Sort(Q)
# P = (Sort, pointer_to_Q)
# P2 = Sort(Q)
# hash_table[str(Q)] = hash_
# if format(Q) in hash_table:
# 	hash_ = hash_table[str(Q)]
# 	P = (Sort, hash_)
# else:
# 	hash_table[Q] = ...	

					if '&' in self.operators:
						# could check whether it has a shared prefix of X and G
						# to make the conjunction smaller
						new_formula = Formula(['&', current_formula, formula])
						new_formula.size = current_formula.size + formula.size + 1
						if new_formula.treeSize() <= upper_bound:
							self.formula_dict[new_formula] = (self.formula_dict[formula][0].intersection(self.formula_dict[best_formula][0]), self.formula_dict[formula][1].intersection(self.formula_dict[best_formula][1]))
							self.cover_size[new_formula] = len(self.formula_dict[new_formula][0]) - len(self.formula_dict[new_formula][1])+ len(self.negative_set)
							value[new_formula] = self.score_local(new_formula, current_formula)
							
					if '|' in self.operators:
						# could check whether it has a shared prefix of X and F
						# to make the disjunction smaller
						new_formula = Formula(['|', current_formula, formula])
						new_formula.size = current_formula.size + formula.size + 1
						if new_formula.treeSize() <= upper_bound:
							self.formula_dict[new_formula] = (self.formula_dict[formula][0].union(self.formula_dict[best_formula][0]), self.formula_dict[formula][1].union(self.formula_dict[best_formula][1]))
							self.cover_size[new_formula] = len(self.formula_dict[new_formula][0]) - len(self.formula_dict[new_formula][1])+ len(self.negative_set)
							value[new_formula] = self.score_local(new_formula, current_formula)
							
					
				current_value = 0
				success=True
				for formula in value.keys():
					#if the resulting formula is better than the best formula then we continue with the resulting formula
					
					if value[formula] > current_value:
						current_formula = formula
						current_value = value[formula]


				if current_value == 0:
					'''
					if we reach upto a formula that we cannot improve with the existing formulas, 
					we push them to the heap as interesting formulas if it is already not in the heap
					'''
					if current_formula not in self.score:	
						self.score[current_formula] = self.cover_size[current_formula]
						hq.heappush(self.heap, (-self.score[current_formula], current_formula))
					
					success = False
					break
			t1= time.time()-t0
			
			logging.debug("* Time spent for %s is %.3f"%(best_formula, t1))
			
			if success:
				upper_bound = current_formula.treeSize() 
				final_formula = current_formula
		
		return final_formula, upper_bound

