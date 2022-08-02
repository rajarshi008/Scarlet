import time
import logging
import heapq as hq
from Scarlet.formulaTree import Formula, merge


# The greedy algorithm for the Boolean subset cover problem
class BooleanSetCover:
	
	def __init__(self, sample, operators, thres):

		self.sample = sample
		self.positive_set = {i for i in range(len(self.sample.positive))}           
		self.negative_set = {i for i in range(len(self.sample.negative))}           
		self.full_set = (self.positive_set, self.negative_set)			            
		self.max_cover_size = len(self.positive_set) + len(self.negative_set)       
		self.thres = thres
		self.score = {}
		self.cover_size = {}
		self.heap = []
		self.new_heap = []
		self.formula_dict = {}
		self.operators = operators
		self.bool_dict={} # saves the best boolean combination for each of the best formulas 

	
	def score_local(self, best_formula, current_formula):
		'''
			Calculates the score of a formula with respect to the best formula till now
		'''
		return (self.cover_size[best_formula]-self.cover_size[current_formula])/((best_formula.treeSize())**(0.5)+1)
	
	


	def find(self, upper_bound):
		'''
			Finds set of best formulas of size less than upper-bound from the current cover set
		'''
		init_upper_bound = upper_bound
		best_formula_list=[]
		smallest_list = hq.nsmallest(5,self.heap)   #get the best 5 formulas currently from the heap with the highest score
		for i in smallest_list:
			best_formula_list.append((i[1],self.cover_size[i[1]])) 

		best_formula_list = list(map(lambda x:x[0], sorted(best_formula_list, key=lambda x: x[1], reverse=True))) #we take the best 5 formulas and sort them with their cover size

		logging.debug("List of best formulas: %s"%str([(i,self.score[i]) for i in best_formula_list]))	
		
		final_formula=None


		for best_formula in best_formula_list:

			current_formula = best_formula
			current_value = self.cover_size[current_formula]/current_formula.treeSize()
			t0=time.time()

			success = True

			if current_formula.treeSize() >= upper_bound:
				continue
 
			while self.cover_size[current_formula] < self.max_cover_size*(1-self.thres): #Continue until we find a formula that covers the whole set
				
				value={}
				
				try:
					(previous_best,score_best)= self.bool_dict[current_formula]
					mod_heap = self.new_heap
				except:
					mod_heap=self.heap

				for (_,formula) in mod_heap:
					
					if formula.treeSize() > upper_bound:
						continue


					if '&' in self.operators:

						new_formula = merge('&', current_formula, formula) #Decrease formula size by taking possible operators common
						new_formula.size = new_formula.treeSize()
						if new_formula.size <= upper_bound:
							if new_formula not in self.formula_dict:
								self.formula_dict[new_formula] = (self.formula_dict[formula][0].intersection(self.formula_dict[current_formula][0]), self.formula_dict[formula][1].intersection(self.formula_dict[current_formula][1]))
								self.cover_size[new_formula] = len(self.formula_dict[new_formula][0]) - len(self.formula_dict[new_formula][1])+ len(self.negative_set)
							value[new_formula] = self.score_local(new_formula, current_formula)


					if '|' in self.operators:

						new_formula = merge('|', current_formula, formula)
						new_formula.size = new_formula.treeSize()
						if new_formula.size <= upper_bound:
							if new_formula not in self.formula_dict:
								self.formula_dict[new_formula] = (self.formula_dict[formula][0].union(self.formula_dict[current_formula][0]), self.formula_dict[formula][1].union(self.formula_dict[current_formula][1]))
								self.cover_size[new_formula] = len(self.formula_dict[new_formula][0]) - len(self.formula_dict[new_formula][1])+ len(self.negative_set)
							value[new_formula] = self.score_local(new_formula, current_formula)
						
					
				current_value = 0
				success = True
				old_formula= current_formula
				for formula in value.keys():
					if value[formula] > current_value:
						current_formula = formula
						current_value = value[formula]	

				try: 
					prev_formula,prev_value = self.bool_dict[old_formula]
					if current_value > prev_value or prev_formula.treeSize() >= upper_bound: 
						self.bool_dict[old_formula]= (current_formula, current_value)
					else:
						current_formula,current_value= prev_formula, prev_value

				except:
					self.bool_dict[old_formula]= (current_formula, current_value)

				if current_value == 0:
					'''
					if we reach upto a formula that we cannot improve anymore by boolean combinations, 
					we push them to the heap as an interesting formula
					'''
					if current_formula not in self.score:
						self.score[current_formula] = self.cover_size[current_formula]/((current_formula.treeSize())**(0.5)+1)
						hq.heappush(self.heap, (-self.score[current_formula], current_formula))
					
					success = False
					break
			t1= time.time()-t0
			
			logging.debug("* Time spent for %s is %.3f"%(best_formula, t1))
			
			if success:
				upper_bound = current_formula.treeSize() 
				final_formula = current_formula

        #if the upperbound has changed in Boolean setcover process, we modify the heap by removing all larger size formulas
		if init_upper_bound != upper_bound:  
			small_heap = []
			hq.heapify(small_heap)
			for (score,formula) in self.heap:
				if formula.treeSize() < upper_bound: 
					hq.heappush(small_heap, (score,formula))

			self.heap = small_heap

		return final_formula, upper_bound

