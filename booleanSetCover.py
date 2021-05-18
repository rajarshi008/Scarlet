import heapq as hq
from .formulaTree import Formula
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

	#def initHeap(self, formula_dict):
		"""
		create a heap containing:
		- all atomic formulas
		- conjunctions and disjunctions of two atomic formulas
		The heap is sorted by score (top element: maximal score)
		"""

	def score_local(self, formula, best_formula):

		return (self.cover_size[formula]-self.cover_size[best_formula])/((formula.treeSize())**(0.5)+1)
	


	def find(self, upper_bound):
		# We start by adding to the heap all atomic formulas

		best_formula_list=[]
		smallest_list = hq.nsmallest(5,self.heap)
		for i in smallest_list:
			best_formula_list.append((i[1],self.cover_size[i[1]]))
		
		best_formula_list = list(map(lambda x:x[0], sorted(best_formula_list, key=lambda x: x[1], reverse=True)))

		logging.debug("List of best formulas: %s"%str([(i,self.score[i]) for i in best_formula_list]))	
		final_formula=None
		
		for best_formula in best_formula_list:

			current_formula = best_formula
			current_value = self.cover_size[current_formula]/current_formula.treeSize()
			t0=time.time()

			success = True
			if current_formula.treeSize() >= upper_bound:
				continue

			while self.cover_size[current_formula] < self.max_cover_size:
				# We find the most interesting formula to combine with best_formula
				
				
				# We look at all existing formulas
				value={}
				for (_,formula) in self.heap[1:]:
					
					if '&' in self.operators:
						new_formula = Formula(['&', current_formula, formula])
						new_formula.size = current_formula.size + formula.size + 1
						if new_formula.treeSize() <= upper_bound:
							self.formula_dict[new_formula] = (self.formula_dict[formula][0].intersection(self.formula_dict[best_formula][0]), self.formula_dict[formula][1].intersection(self.formula_dict[best_formula][1]))
							self.cover_size[new_formula] = len(self.formula_dict[new_formula][0]) - len(self.formula_dict[new_formula][1])+ len(self.negative_set)
							value[new_formula] = self.score_local(new_formula, current_formula)
							
					if '|' in self.operators:
						new_formula = Formula(['|', current_formula, formula])
						new_formula.size = current_formula.size + formula.size + 1
						if new_formula.treeSize() <= upper_bound:
							self.formula_dict[new_formula] = (self.formula_dict[formula][0].union(self.formula_dict[best_formula][0]), self.formula_dict[formula][1].union(self.formula_dict[best_formula][1]))
							self.cover_size[new_formula] = len(self.formula_dict[new_formula][0]) - len(self.formula_dict[new_formula][1])+ len(self.negative_set)
							value[new_formula] = self.score_local(new_formula, current_formula)
							
					
				current_value = 0
				success=True
				for formula in value.keys():
					
					if value[formula] > current_value:
						current_formula = formula
						current_value = value[formula]


				if current_value == 0:
					
					if current_formula not in self.score:	
						self.score[current_formula] = self.cover_size[current_formula]
						print(current_formula, self.score[current_formula])
						hq.heappush(self.heap, (-self.score[current_formula], current_formula))
					
					success = False
					break
			t1= time.time()-t0
			
			logging.debug("* Time spent for %s is %.3f"%(best_formula, t1))
			
			if success:
				upper_bound = current_formula.treeSize() 
				final_formula = current_formula
		
		return final_formula, upper_bound

	"""
	Optimisations:
	* We can replace "score" with "score / size",
	or anything else that is increasing with score and decreasing with size
	* Here the greediness is lazy: we only combine formulas with the best current formula.
	We may want to do more combinations. 
	The other extreme is to do a saturation algorithm: at each step we create all possible combinations.
	We can have something in between: at each step we create combinations using only the 10 best formulas?
	"""

	def size_formula(self, formula1, formula2, operator):
		"""
		a priori the size is formula1 + formula2 + 1
		but it may differ if the two formulas can be factorised
		"""
		return formula1.size + formula2.size + 1


